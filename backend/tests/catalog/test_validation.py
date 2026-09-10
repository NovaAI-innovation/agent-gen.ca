"""Tests for listing validation contracts.

Exercise every constraint defined in app.services.catalog without requiring
a database — pure validation logic only.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.catalog import (
    # error codes
    TITLE_EMPTY,
    TITLE_TOO_SHORT,
    TITLE_TOO_LONG,
    TITLE_INVALID_CHARS,
    DESCRIPTION_EMPTY,
    DESCRIPTION_TOO_LONG,
    LONG_DESCRIPTION_TOO_LONG,
    PRICE_NEGATIVE,
    PRICE_TOO_MANY_DECIMALS,
    PRICE_UNIT_OVERFLOW,
    CATEGORY_LIMIT,
    TAG_LIMIT,
    RELEASE_VERSION_EMPTY,
    RELEASE_VERSION_INVALID,
    RELEASE_VERSION_TOO_LONG,
    RELEASE_CHANGELOG_TOO_LONG,
    RELEASE_INSTALL_INSTRUCTIONS_TOO_LONG,
    URL_TOO_LONG,
    URL_INVALID,
    CONFIG_JSON_TOO_LARGE,
    # limit constants
    TITLE_MIN_LENGTH,
    TITLE_MAX_LENGTH,
    DESCRIPTION_MAX_LENGTH,
    LONG_DESCRIPTION_MAX_LENGTH,
    RELEASE_VERSION_MAX_LENGTH,
    RELEASE_CHANGELOG_MAX_LENGTH,
    RELEASE_INSTALL_INSTRUCTIONS_MAX_LENGTH,
    CONFIG_JSON_MAX_BYTES,
    MAX_CATEGORIES,
    MAX_TAGS,
    # validators
    validate_title,
    validate_description,
    validate_long_description,
    validate_price,
    validate_categories,
    validate_tags,
    validate_url,
    validate_release_version,
    validate_release_changelog,
    validate_install_instructions,
    validate_config_json,
    validate_listing_create,
    validate_listing_update,
    validate_release_create,
)


# ── Title ─────────────────────────────────────────────────────────────────────


class TestValidateTitle:
    def test_none_yields_empty_error(self):
        errors = validate_title(None)
        assert len(errors) == 1
        assert errors[0].code == TITLE_EMPTY

    def test_blank_yields_empty_error(self):
        errors = validate_title("   ")
        assert errors[0].code == TITLE_EMPTY

    def test_too_short(self):
        errors = validate_title("ab")
        assert errors[0].code == TITLE_TOO_SHORT

    def test_exact_min_length(self):
        errors = validate_title("abc" + "x" * (TITLE_MIN_LENGTH - 3))
        assert not any(e.code == TITLE_TOO_SHORT for e in errors)

    def test_too_long(self):
        errors = validate_title("a" * (TITLE_MAX_LENGTH + 1))
        assert errors[0].code == TITLE_TOO_LONG

    def test_exact_max_length(self):
        errors = validate_title("a" * TITLE_MAX_LENGTH)
        assert not any(e.code == TITLE_TOO_LONG for e in errors)

    def test_disallowed_chars(self):
        # backtick and angle brackets are not in the allowed set
        errors = validate_title("title\nwith\x00null")
        assert any(e.code == TITLE_INVALID_CHARS for e in errors)

    def test_valid_title(self):
        errors = validate_title("My Cool Agent (v2.0)")
        assert errors == []

    def test_underscores_allowed(self):
        errors = validate_title("under_score_title_ok")
        assert errors == []


# ── Description ──────────────────────────────────────────────────────────────


class TestValidateDescription:
    def test_none_yields_empty_error(self):
        errors = validate_description(None)
        assert errors[0].code == DESCRIPTION_EMPTY

    def test_too_long(self):
        errors = validate_description("x" * (DESCRIPTION_MAX_LENGTH + 1))
        assert errors[0].code == DESCRIPTION_TOO_LONG

    def test_exact_max(self):
        errors = validate_description("x" * DESCRIPTION_MAX_LENGTH)
        assert errors == []

    def test_valid(self):
        errors = validate_description("A short useful description.")
        assert errors == []


# ── Long description ─────────────────────────────────────────────────────────


class TestLongDescription:
    def test_none_passes(self):
        assert validate_long_description(None) == []

    def test_too_long(self):
        errors = validate_long_description("x" * (LONG_DESCRIPTION_MAX_LENGTH + 1))
        assert errors[0].code == LONG_DESCRIPTION_TOO_LONG

    def test_valid(self):
        assert validate_long_description("details") == []


# ── Price ─────────────────────────────────────────────────────────────────────


class TestValidatePrice:
    def test_none_passes(self):
        assert validate_price(None) == []

    def test_zero_passes(self):
        assert validate_price(Decimal("0")) == []

    def test_negative(self):
        errors = validate_price(Decimal("-0.001"))
        assert errors[0].code == PRICE_NEGATIVE

    def test_too_many_decimals(self):
        errors = validate_price(Decimal("1.1234567890"))  # 10 decimal places
        assert errors[0].code == PRICE_TOO_MANY_DECIMALS

    def test_nine_decimals_ok(self):
        errors = validate_price(Decimal("1.123456789"))
        assert errors == []

    def test_integer_overflow(self):
        errors = validate_price(Decimal("12345678901"))  # 11 digits
        assert errors[0].code == PRICE_UNIT_OVERFLOW

    def test_ten_int_digits_ok(self):
        errors = validate_price(Decimal("9999999999"))  # 10 digits
        assert errors == []

    def test_large_with_decimals(self):
        errors = validate_price(Decimal("9999.123456789"))
        assert errors == []


# ── Categories & tags ────────────────────────────────────────────────────────


class TestValidateCategoriesAndTags:
    def test_categories_over_limit(self):
        errors = validate_categories([1, 2, 3, 4, 5, 6])
        assert errors[0].code == CATEGORY_LIMIT

    def test_categories_at_limit(self):
        assert validate_categories([1, 2, 3, 4, 5]) == []

    def test_tags_over_limit(self):
        errors = validate_tags(list(range(MAX_TAGS + 1)))
        assert errors[0].code == TAG_LIMIT

    def test_none_passes(self):
        assert validate_categories(None) == []
        assert validate_tags(None) == []


# ── URL ──────────────────────────────────────────────────────────────────────


class TestValidateUrl:
    def test_none_passes(self):
        assert validate_url(None) == []

    def test_empty_passes(self):
        assert validate_url("") == []

    def test_valid(self):
        assert validate_url("https://example.com/path?q=1") == []

    def test_missing_scheme(self):
        errors = validate_url("example.com")
        assert errors[0].code == URL_INVALID

    def test_too_long(self):
        errors = validate_url("https://example.com/" + "a" * 3000)
        assert errors[0].code == URL_TOO_LONG


# ── Release version ──────────────────────────────────────────────────────────


class TestValidateReleaseVersion:
    def test_none_is_empty(self):
        errors = validate_release_version(None)
        assert errors[0].code == RELEASE_VERSION_EMPTY

    def test_blank_is_empty(self):
        errors = validate_release_version("   ")
        assert errors[0].code == RELEASE_VERSION_EMPTY

    def test_invalid_format(self):
        errors = validate_release_version("not-a-version")
        assert errors[0].code == RELEASE_VERSION_INVALID

    def test_valid_semver(self):
        assert validate_release_version("1.2.3") == []

    def test_prerelease(self):
        assert validate_release_version("1.0.0-beta.1") == []

    def test_too_long(self):
        errors = validate_release_version("1." * 20)
        assert errors[0].code == RELEASE_VERSION_TOO_LONG


# ── Release changelog & install instructions ─────────────────────────────────


class TestReleaseTextFields:
    def test_changelog_none_passes(self):
        assert validate_release_changelog(None) == []

    def test_changelog_too_long(self):
        errors = validate_release_changelog("x" * (RELEASE_CHANGELOG_MAX_LENGTH + 1))
        assert errors[0].code == RELEASE_CHANGELOG_TOO_LONG

    def test_install_instructions_none_passes(self):
        assert validate_install_instructions(None) == []

    def test_install_instructions_too_long(self):
        errors = validate_install_instructions("x" * (RELEASE_INSTALL_INSTRUCTIONS_MAX_LENGTH + 1))
        assert errors[0].code == RELEASE_INSTALL_INSTRUCTIONS_TOO_LONG

    def test_config_json_none_passes(self):
        assert validate_config_json(None) == []

    def test_config_json_too_large(self):
        big = {"data": "x" * CONFIG_JSON_MAX_BYTES}
        errors = validate_config_json(big)
        assert errors[0].code == CONFIG_JSON_TOO_LARGE

    def test_config_json_valid(self):
        assert validate_config_json({"key": "value"}) == []


# ── Aggregate: validate_listing_create ───────────────────────────────────────


class TestListingCreateValidation:
    def test_all_valid(self):
        result = validate_listing_create(
            title="My Agent",
            description="Does great things.",
            price_sol=Decimal("1.5"),
            category_ids=[1, 2],
            tag_ids=[1],
        )
        assert result.is_valid is True
        assert result.errors == ()

    def test_multiple_errors(self):
        result = validate_listing_create(
            title="x",
            description=None,
            price_sol=Decimal("-1"),
            category_ids=[1, 2, 3, 4, 5, 6],
        )
        assert result.is_valid is False
        codes = {e.code for e in result.errors}
        assert TITLE_TOO_SHORT in codes
        assert DESCRIPTION_EMPTY in codes
        assert PRICE_NEGATIVE in codes
        assert CATEGORY_LIMIT in codes


# ── Aggregate: validate_listing_update ───────────────────────────────────────


class TestListingUpdateValidation:
    def test_only_provided_fields_validated(self):
        """Update allows partial — None fields should not trigger errors."""
        result = validate_listing_update(title="New Title")
        assert result.is_valid is True

    def test_provided_field_validated(self):
        result = validate_listing_update(description="x" * (DESCRIPTION_MAX_LENGTH + 1))
        assert result.is_valid is False
        assert result.errors[0].code == DESCRIPTION_TOO_LONG

    def test_empty_update_passes(self):
        result = validate_listing_update()
        assert result.is_valid is True


# ── Aggregate: validate_release_create ───────────────────────────────────────


class TestReleaseCreateValidation:
    def test_all_valid(self):
        result = validate_release_create(
            version="1.0.0",
            changelog="Initial release",
            config_json={"key": "value"},
            install_instructions="npm install my-agent",
        )
        assert result.is_valid is True

    def test_invalid_version(self):
        result = validate_release_create(version="bad")
        assert result.is_valid is False
        assert result.errors[0].code == RELEASE_VERSION_INVALID