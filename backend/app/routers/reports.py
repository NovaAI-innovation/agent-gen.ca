"""Abuse reports router.

Allows authenticated users to report public entities (listings, releases,
other users) and track their report receipt.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.deps import get_current_user
from ..db.database import get_db
from ..models.report import Report, ReportEntityType, ReportStatus
from ..models.user import User
from pydantic import BaseModel

router = APIRouter(tags=["reports"])


class ReportCreate(BaseModel):
    entity_type: ReportEntityType
    entity_id: uuid.UUID
    reason: str
    details: str | None = None


@router.post("/reports", response_model=dict, status_code=201)
async def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = Report(
        reporter_id=current_user.id,
        entity_type=data.entity_type.value,
        entity_id=data.entity_id,
        reason=data.reason,
        details=data.details,
        status=ReportStatus.OPEN.value,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    await db.commit()

    return {
        "id": str(report.id),
        "entity_type": report.entity_type,
        "entity_id": str(report.entity_id),
        "reason": report.reason,
        "status": report.status,
        "created_at": report.created_at.isoformat(),
    }


@router.get("/reports/{report_id}", response_model=dict)
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.reporter_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": str(report.id),
        "entity_type": report.entity_type,
        "entity_id": str(report.entity_id),
        "reason": report.reason,
        "details": report.details,
        "status": report.status,
        "resolution_note": report.resolution_note,
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat(),
    }