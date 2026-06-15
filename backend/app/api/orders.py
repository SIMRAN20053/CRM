"""Order endpoints — list, create, and bulk-create with customer aggregation."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.order import (
    OrderCreate,
    OrderBulkCreate,
    OrderListResponse,
    OrderResponse,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


async def _update_customer_aggregates(
    db: AsyncSession, customer_id: str
) -> None:
    """Recompute total_spend, visit_count, and last_purchase_at for a customer."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if customer is None:
        return

    agg = await db.execute(
        select(
            func.coalesce(func.sum(Order.amount), 0),
            func.count(Order.id),
            func.max(Order.order_date),
        ).where(Order.customer_id == customer_id)
    )
    total_spend, visit_count, last_purchase = agg.one()

    customer.total_spend = float(total_spend)
    customer.visit_count = int(visit_count)
    customer.last_purchase_at = last_purchase
    db.add(customer)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List orders with pagination."""
    offset = (page - 1) * page_size

    total_result = await db.execute(select(func.count(Order.id)))
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Order)
        .order_by(Order.order_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()

    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    """Create a single order and update the customer's aggregated fields."""
    # Verify customer exists
    cust_result = await db.execute(
        select(Customer).where(Customer.id == payload.customer_id)
    )
    if cust_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    order = Order(**payload.model_dump())
    db.add(order)
    await db.flush()  # Ensure order is persisted before re-aggregating

    await _update_customer_aggregates(db, payload.customer_id)
    await db.commit()
    await db.refresh(order)

    return OrderResponse.model_validate(order)


@router.post("/bulk", status_code=201)
async def bulk_create_orders(
    payload: OrderBulkCreate, db: AsyncSession = Depends(get_db)
):
    """Bulk-create orders and update affected customers' aggregates."""
    affected_customers: set[str] = set()
    created: list[Order] = []

    for item in payload.orders:
        order = Order(**item.model_dump())
        db.add(order)
        created.append(order)
        affected_customers.add(item.customer_id)

    await db.flush()

    # Re-aggregate for every affected customer
    for cid in affected_customers:
        await _update_customer_aggregates(db, cid)

    await db.commit()

    for o in created:
        await db.refresh(o)

    return {
        "created": len(created),
        "orders": [OrderResponse.model_validate(o) for o in created],
    }
