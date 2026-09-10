"""Tests for v2 catalog state machines.

These tests exercise the ListingState, CreatorState, and ReleaseState
machines without requiring a running database — they only test
transition logic and public-visibility invariants.
"""

from __future__ import annotations

import pytest

from app.models.moderation import (
    ListingState,
    CreatorState,
    ReleaseState,
)


# ── ListingState ──────────────────────────────────────────────────────────────


class TestListingState:
    def test_initial_state_is_draft(self):
        assert ListingState.initial_state() == "draft"

    def test_draft_can_only_go_to_pending_review(self):
        assert ListingState.transitions("draft") == ["pending_review"]

    def test_pending_review_can_go_to_approved_rejected_or_draft(self):
        t = ListingState.transitions("pending_review")
        assert set(t) == {"approved", "rejected", "draft"}

    def test_approved_can_go_to_published_or_draft(self):
        t = ListingState.transitions("approved")
        assert set(t) == {"published", "draft"}

    def test_published_can_go_to_draft_suspended_or_archived(self):
        t = ListingState.transitions("published")
        assert set(t) == {"draft", "suspended", "archived"}

    def test_rejected_can_only_go_to_draft(self):
        assert ListingState.transitions("rejected") == ["draft"]

    def test_suspended_can_go_to_draft_or_archived(self):
        t = ListingState.transitions("suspended")
        assert set(t) == {"draft", "archived"}

    def test_archived_can_only_go_to_draft(self):
        assert ListingState.transitions("archived") == ["draft"]

    def test_unknown_state_returns_empty(self):
        assert ListingState.transitions("nonexistent") == []

    def test_can_transition_valid(self):
        assert ListingState.can_transition("draft", "pending_review") is True
        assert ListingState.can_transition("published", "suspended") is True

    def test_can_transition_invalid(self):
        assert ListingState.can_transition("draft", "published") is False
        assert ListingState.can_transition("published", "approved") is False
        assert ListingState.can_transition("rejected", "published") is False

    def test_draft_cannot_appear_in_public_queries(self):
        public = ListingState.publicly_visible_states()
        assert "draft" not in public
        assert "pending_review" not in public
        assert "rejected" not in public
        assert "suspended" not in public

    def test_only_published_is_publicly_visible(self):
        assert ListingState.publicly_visible_states() == {"published"}

    def test_editable_states(self):
        editable = ListingState.editable_states()
        assert "draft" in editable
        assert "rejected" in editable
        assert "published" not in editable
        assert "pending_review" not in editable

    def test_full_happy_path(self):
        """Draft → pending_review → approved → published → archived → draft."""
        path = [
            ("draft", "pending_review"),
            ("pending_review", "approved"),
            ("approved", "published"),
            ("published", "archived"),
            ("archived", "draft"),
        ]
        for from_s, to_s in path:
            assert ListingState.can_transition(from_s, to_s), f"{from_s} → {to_s}"

    def test_rejection_loop(self):
        """Creator can fix and resubmit after rejection."""
        assert ListingState.can_transition("rejected", "draft")
        assert ListingState.can_transition("draft", "pending_review")

    def test_suspension_recovery(self):
        """Suspended listings can return to draft for rework."""
        assert ListingState.can_transition("suspended", "draft")
        assert ListingState.can_transition("draft", "pending_review")


# ── CreatorState ──────────────────────────────────────────────────────────────


class TestCreatorState:
    def test_initial_state_is_pending_approval(self):
        assert CreatorState.initial_state() == "pending_approval"

    def test_pending_approval_can_only_go_to_approved(self):
        assert CreatorState.transitions("pending_approval") == ["approved"]

    def test_approved_can_only_go_to_suspended(self):
        assert CreatorState.transitions("approved") == ["suspended"]

    def test_suspended_can_go_to_approved_or_banned(self):
        t = CreatorState.transitions("suspended")
        assert set(t) == {"approved", "banned"}

    def test_banned_has_no_exits(self):
        assert CreatorState.transitions("banned") == []

    def test_can_publish_only_when_approved(self):
        assert CreatorState.can_publish("approved") is True
        assert CreatorState.can_publish("pending_approval") is False
        assert CreatorState.can_publish("suspended") is False
        assert CreatorState.can_publish("banned") is False

    def test_invalid_transitions(self):
        assert CreatorState.can_transition("pending_approval", "suspended") is False
        assert CreatorState.can_transition("approved", "banned") is False
        assert CreatorState.can_transition("banned", "approved") is False


# ── ReleaseState ──────────────────────────────────────────────────────────────


class TestReleaseState:
    def test_initial_state_is_draft(self):
        assert ReleaseState.initial_state() == "draft"

    def test_draft_can_only_go_to_pending_review(self):
        assert ReleaseState.transitions("draft") == ["pending_review"]

    def test_published_cannot_go_to_approved(self):
        """Unlike listing state, published releases can't go back to approved."""
        assert ReleaseState.can_transition("published", "approved") is False

    def test_published_can_go_to_suspended_or_archived(self):
        t = ReleaseState.transitions("published")
        assert set(t) == {"suspended", "archived"}

    def test_full_release_lifecycle(self):
        path = [
            ("draft", "pending_review"),
            ("pending_review", "approved"),
            ("approved", "published"),
            ("published", "suspended"),
            ("suspended", "draft"),
        ]
        for from_s, to_s in path:
            assert ReleaseState.can_transition(from_s, to_s), f"{from_s} → {to_s}"


# ── Cross-machine invariants ─────────────────────────────────────────────────


class TestCrossMachineInvariants:
    def test_no_state_machine_allows_direct_draft_to_published(self):
        """No entity can skip review and go straight to published."""
        assert ListingState.can_transition("draft", "published") is False
        assert ReleaseState.can_transition("draft", "published") is False

    def test_no_state_machine_allows_banned_recovery(self):
        """Banned is a terminal state."""
        assert CreatorState.transitions("banned") == []

    def test_all_machines_have_initial_state(self):
        assert ListingState.initial_state() is not None
        assert CreatorState.initial_state() is not None
        assert ReleaseState.initial_state() is not None
