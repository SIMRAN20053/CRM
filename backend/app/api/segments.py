"""Segment endpoints — create, list, detail, and audience resolution."""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.segment import Segment
from app.schemas.segment import (
    SegmentCreate,
    SegmentListResponse,
    SegmentResponse,
)
from app.schemas.customer import CustomerResponse
from app.services.segment_engine import segment_engine

router = APIRouter(prefix="/api/segments", tags=["segments"])


@router.get("", response_model=SegmentListResponse)
async def list_segments(db: AsyncSession = Depends(get_db)):
    """List all segments."""
    total_result = await db.execute(select(func.count(Segment.id)))
    total = total_result.scalar() or 0
    
    result = await db.execute(select(Segment).order_by(Segment.created_at.desc()))
    segments = result.scalars().all()
    return SegmentListResponse(
        segments=[SegmentResponse.model_validate(s) for s in segments],
        total=total,
    )


@router.post("", response_model=SegmentResponse, status_code=201)
async def create_segment(
    payload: SegmentCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new segment. The audience_size is calculated via the segment engine."""
    # Convert rules to dict and JSON string for storage
    rules_dict = payload.rules.model_dump() if hasattr(payload.rules, "model_dump") else payload.rules
    rules_json = json.dumps(rules_dict)

    # Calculate audience size
    audience_size = await segment_engine.calculate_audience_size(rules_dict, db)

    segment = Segment(
        name=payload.name,
        description=payload.description,
        rules=rules_json,
        ai_reasoning=payload.ai_reasoning,
        confidence_score=payload.confidence_score,
        audience_size=audience_size,
    )
    db.add(segment)
    await db.commit()
    await db.refresh(segment)

    return SegmentResponse.model_validate(segment)


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(segment_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single segment's details."""
    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")
    return SegmentResponse.model_validate(segment)


@router.get("/{segment_id}/customers")
async def get_segment_customers(
    segment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get the list of customers matching a segment's rules."""
    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()
    if segment is None:
        raise HTTPException(status_code=404, detail="Segment not found")

    # Parse stored rules
    rules: Any = json.loads(segment.rules) if isinstance(segment.rules, str) else segment.rules

    customers = await segment_engine.get_audience(rules, db)
    return {
        "segment_id": segment_id,
        "audience_size": len(customers),
        "customers": [CustomerResponse.model_validate(c) for c in customers],
    }
