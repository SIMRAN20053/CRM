"""Customer CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.customer import Customer
from app.models.order import Order
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerDetailResponse,
    CustomerBulkCreate,
)

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=CustomerListResponse)
async def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    """List customers with pagination."""
    offset = (page - 1) * page_size

    # Total count
    total_result = await db.execute(select(func.count(Customer.id)))
    total = total_result.scalar() or 0

    # Paginated results
    result = await db.execute(
        select(Customer)
        .order_by(Customer.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    customers = result.scalars().all()

    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single customer with their order history."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Fetch orders for this customer
    orders_result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.order_date.desc())
    )
    orders = orders_result.scalars().all()

    return CustomerDetailResponse(
        customer=CustomerResponse.model_validate(customer),
        orders=orders,
    )


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    payload: CustomerCreate, db: AsyncSession = Depends(get_db)
):
    """Create a single customer."""
    customer = Customer(**payload.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.post("/bulk", status_code=201)
async def bulk_create_customers(
    payload: CustomerBulkCreate, db: AsyncSession = Depends(get_db)
):
    """Bulk-create customers from a list."""
    created: list[CustomerResponse] = []
    for item in payload.customers:
        customer = Customer(**item.model_dump())
        db.add(customer)
        created.append(customer)

    await db.commit()

    # Refresh to populate server defaults
    for c in created:
        await db.refresh(c)

    return {
        "created": len(created),
        "customers": [CustomerResponse.model_validate(c) for c in created],
    }
