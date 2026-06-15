"""Delivery receipt endpoints — webhook-style ingestion from channel services."""

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.campaign_engine import campaign_engine

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


# ---------------------------------------------------------------------------
# Request schemas (kept local — tiny, receipt-specific)
# ---------------------------------------------------------------------------

class ReceiptPayload(BaseModel):
    """Single delivery receipt from a channel service."""
    log_id: str
    status: str
    timestamp: str
    reason: str | None = None


class BatchReceiptPayload(BaseModel):
    """Batch of delivery receipts."""
    receipts: list[ReceiptPayload]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("")
async def receive_receipt(
    payload: ReceiptPayload, db: AsyncSession = Depends(get_db)
):
    """Accept a single delivery receipt and process it."""
    await campaign_engine.process_receipt(
        log_id=payload.log_id,
        status=payload.status,
        timestamp=payload.timestamp,
        reason=payload.reason,
        db=db,
    )
    return {"status": "ok"}


@router.post("/batch")
async def receive_batch_receipts(
    payload: BatchReceiptPayload, db: AsyncSession = Depends(get_db)
):
    """Accept a batch of delivery receipts and process each one."""
    processed = 0
    for receipt in payload.receipts:
        await campaign_engine.process_receipt(
            log_id=receipt.log_id,
            status=receipt.status,
            timestamp=receipt.timestamp,
            reason=receipt.reason,
            db=db,
        )
        processed += 1

    return {"status": "ok", "processed": processed}
