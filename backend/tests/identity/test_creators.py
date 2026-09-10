"""Tests for approved-creator onboarding — profile submission, approval gating,
and listing creation authorization.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.services import creators as svc
from app.schemas.user import CreatorProfileIn


def _make_user(**kw) -> SimpleNamespace:
    defaults = dict(
        id=uuid4(),
        wallet_address="6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
        username=None,
        bio=None,
        handle=None,
        display_name=None,
        support_link=None,
        payout_address=None,
        terms_accepted_at=None,
        creator_status="none",
        creator_status_at=None,
        reviewer_notes=None,
    )
    defaults.update(kw)
    return SimpleNamespace(**defaults)


# ── require_approved_creator ──────────────────────────────────────────────────


class TestRequireApprovedCreator:
    def test_passes_approved(self):
        user = _make_user(creator_status="approved")
        result = svc.require_approved_creator(user)
        assert result is user

    def test_raises_403_for_unapproved(self):
        for status in ("none", "pending", "rejected"):
            user = _make_user(creator_status=status)
            with pytest.raises(Exception) as exc:
                svc.require_approved_creator(user)
            assert exc.typename == "HTTPException"
            assert exc.value.status_code == 403


# ── submit_creator_profile ────────────────────────────────────────────────────


class TestSubmitCreatorProfile:
    @pytest.mark.asyncio
    async def test_submit_sets_pending(self):
        user = _make_user(creator_status="none")
        db = AsyncMock()

        # No existing user with the same handle
        class _EmptyResult:
            def scalar_one_or_none(self):
                return None

        db.execute = AsyncMock(return_value=_EmptyResult())

        data = CreatorProfileIn(
            handle="my-handle",
            display_name="My Display",
            bio="Bio content",
            support_link="https://example.com",
            payout_address="6hc7FwQFqBaFpKzSMXFrxyJiwGEFDFpFKASvBVenDD73",
            terms_accepted=True,
        )

        result = await svc.submit_creator_profile(db, user, data)

        assert result.creator_status == "pending"
        assert result.handle == "my-handle"
        assert result.display_name == "My Display"
        assert result.terms_accepted_at is not None

    @pytest.mark.asyncio
    async def test_handle_conflict_raises_409(self):
        existing_user = _make_user(id=uuid4(), handle="taken-handle", creator_status="approved")
        user = _make_user(handle=None, creator_status="none")

        class _ExistsResult:
            def scalar_one_or_none(self):
                return existing_user

        db = AsyncMock()
        db.execute = AsyncMock(return_value=_ExistsResult())

        data = CreatorProfileIn(
            handle="taken-handle",
            display_name="Colliding",
            terms_accepted=True,
        )

        with pytest.raises(Exception) as exc:
            await svc.submit_creator_profile(db, user, data)
        assert exc.typename == "HTTPException"
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_keeps_approved_on_resubmit(self):
        user = _make_user(creator_status="approved", handle="existing")
        db = AsyncMock()

        class _EmptyResult:
            def scalar_one_or_none(self):
                return None

        db.execute = AsyncMock(return_value=_EmptyResult())

        data = CreatorProfileIn(
            handle="existing",
            display_name="Updated Name",
            terms_accepted=True,
        )

        result = await svc.submit_creator_profile(db, user, data)
        # An approved user updating their profile stays approved
        assert result.creator_status == "approved"
        assert result.display_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_keeps_pending_on_resubmit(self):
        user = _make_user(creator_status="pending")
        db = AsyncMock()

        class _EmptyResult:
            def scalar_one_or_none(self):
                return None

        db.execute = AsyncMock(return_value=_EmptyResult())

        data = CreatorProfileIn(
            handle="still-pending",
            display_name="Still Pending",
            terms_accepted=True,
        )

        result = await svc.submit_creator_profile(db, user, data)
        assert result.creator_status == "pending"


# ── review_creator ────────────────────────────────────────────────────────────


class TestReviewCreator:
    @pytest.mark.asyncio
    async def test_approve_sets_approved(self):
        user = _make_user(creator_status="pending")
        db = AsyncMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()

        result = await svc.review_creator(db, user, approve=True)
        assert result.creator_status == "approved"
        assert result.creator_status_at is not None

    @pytest.mark.asyncio
    async def test_reject_sets_rejected_with_notes(self):
        user = _make_user(creator_status="pending")
        db = AsyncMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()

        result = await svc.review_creator(db, user, approve=False, notes="Missing payout address")
        assert result.creator_status == "rejected"
        assert result.reviewer_notes == "Missing payout address"