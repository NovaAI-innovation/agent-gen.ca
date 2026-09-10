"""Listing validation contracts.

Centralises the contracts that every listing and release must pass before it
can leave draft state.  Error codes are stable so the frontend can map them
to user-facing messages without relying on free-text error strings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

# ── Stable error codes ──────────────────────────────────────────────────────

TITLE_EMPTY = "LISTING_TITLE_EMPTY"
TITLE_TOO_SHORT = "LISTING_TITLE_TOO_SHORT"
TITLE_TOO_LONG = "LISTING_TITLE_TOO_LONG"
TITLE_INVALID_CHARS = "LISTING_TITLE_INVALID_CHARS"
DESCRIPTION_EMPTY = "LISTING_DESCRIPTION_EMPTY"
DESCRIPTION_TOO_LONG = "LISTING_DESCRIPTION_TOO_LONG"
LONG_DESCRIPTION_TOO_LONG = "LISTING_LONG_DESCRIPTION_TOO_LONG"
PRICE_NEGATIVE = "LISTING_PRICE_NEGATIVE"
PRICE_TOO_MANY_DECIMALS = "LISTING_PRICE_TOO_MANY_DECIMALS"
PRICE_UNIT_OVERFLOW = "LISTING_PRICE_UNIT_OVERFLOW"
CATEGORY_LIMIT = "LISTING_CATEGORY_LIMIT"
TAG_LIMIT = "LISTING_TAG_LIMIT"
RELEASE_VERSION_EMPTY = "RELEASE_VERSION_EMPTY"
RELEASE_VERSION_INVALID = "RELEASE_VERSION_INVALID"
RELEASE_VERSION_TOO_LONG = "RELEASE_VERSION_TOO_LONG"
RELEASE_CHANGELOG_TOO_LONG = "RELEASE_CHANGELOG_TOO_LONG"
RELEASE_INSTALL_INSTRUCTIONS_TOO_LONG = "RELEASE_INSTALL_INSTRUCTIONS_TOO_LONG"
URL_TOO_LONG = "LISTING_URL_TOO_LONG"
URL_INVALID = "LISTING_URL_INVALID"
LICENCE_TOO_LONG = "LISTING_LICENCE_TOO_LONG"
CONFIG_JSON_TOO_LARGE = "LISTING_CONFIG_JSON_TOO_LARGE"

# ── Limits ──────────────────────────────────────────────────────────────────

TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 2_000
LONG_DESCRIPTION_MAX_LENGTH = 50_000
URL_MAX_LENGTH = 2_048
LICENCE_MAX_LENGTH = 100
MAX_CATEGORIES = 5
MAX_TAGS = 10
MAX_PRICE_INTEGER_DIGITS = 10  # 9 999 999 999.xxx
MAX_PRICE_DECIMAL_PLACES = 9
RELEASE_VERSION_MAX_LENGTH = 30
RELEASE_CHANGELOG_MAX_LENGTH = 10_000
RELEASE_INSTALL_INSTRUCTIONS_MAX_LENGTH = 20_000
CONFIG_JSON_MAX_BYTES = 512 * 1024  # 512 KB

_URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%])+$"
)

_TITLE_PATTERN = re.compile(
    r"^[a-zA-Z0-9\s\-_.'()&!+,/:=@\[\]]+$"
)

_SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*"
    r"(?:\.(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)?$"
)


@dataclass(frozen=True)
class ValidationError:
    code: str
    message: str
    field: str | None = None


def validate_title(title: str | None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not title or not title.strip():
        errors.append(ValidationError(TITLE_EMPTY, "Title is required.", "title"))
        return errors
    title = title.strip()
    if len(title) < TITLE_MIN_LENGTH:
        errors.append(ValidationError(
            TITLE_TOO_SHORT,
            f"Title must be at least {TITLE_MIN_LENGTH} characters.",
            "title",
        ))
    if len(title) > TITLE_MAX_LENGTH:
        errors.append(ValidationError(
            TITLE_TOO_LONG,
            f"Title must be at most {TITLE_MAX_LENGTH} characters.",
            "title",
        ))
    if not _TITLE_PATTERN.match(title):
        errors.append(ValidationError(
            TITLE_INVALID_CHARS,
            "Title contains disallowed characters.",
            "title",
        ))
    return errors


def validate_description(description: str | None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not description or not description.strip():
        errors.append(ValidationError(DESCRIPTION_EMPTY, "Description is required.", "description"))
        return errors
    if len(description) > DESCRIPTION_MAX_LENGTH:
        errors.append(ValidationError(
            DESCRIPTION_TOO_LONG,
            f"Description must be at most {DESCRIPTION_MAX_LENGTH:,} characters.",
            "description",
        ))
    return errors


def validate_long_description(long_description: str | None) -> list[ValidationError]:
    if long_description and len(long_description) > LONG_DESCRIPTION_MAX_LENGTH:
        return [ValidationError(
            LONG_DESCRIPTION_TOO_LONG,
            f"Long description must be at most {LONG_DESCRIPTION_MAX_LENGTH:,} characters.",
            "long_description",
        )]
    return []


def validate_price(price: Decimal | None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if price is None:
        return errors
    if price < 0:
        errors.append(ValidationError(PRICE_NEGATIVE, "Price cannot be negative.", "price_sol"))
        return errors
    # Check integer part for overflow
    sign, digits, exponent = price.as_tuple()
    decimal_places = abs(exponent) if exponent < 0 else 0
    if decimal_places > MAX_PRICE_DECIMAL_PLACES:
        errors.append(ValidationError(
            PRICE_TOO_MANY_DECIMALS,
            f"Price has too many decimal places (max {MAX_PRICE_DECIMAL_PLACES}).",
            "price_sol",
        ))
    integer_digits = len(digits) - decimal_places
    if integer_digits > MAX_PRICE_INTEGER_DIGITS:
        errors.append(ValidationError(
            PRICE_UNIT_OVERFLOW,
            f"Price integer part can be at most {MAX_PRICE_INTEGER_DIGITS} digits.",
            "price_sol",
        ))
    return errors


def validate_categories(category_ids: list[int] | None) -> list[ValidationError]:
    if category_ids and len(category_ids) > MAX_CATEGORIES:
        return [ValidationError(
            CATEGORY_LIMIT,
            f"A listing can have at most {MAX_CATEGORIES} categories.",
            "category_ids",
        )]
    return []


def validate_tags(tag_ids: list[int] | None) -> list[ValidationError]:
    if tag_ids and len(tag_ids) > MAX_TAGS:
        return [ValidationError(
            TAG_LIMIT,
            f"A listing can have at most {MAX_TAGS} tags.",
            "tag_ids",
        )]
    return []


def validate_url(value: str | None, field: str = "url") -> list[ValidationError]:
    if not value:
        return []
    if len(value) > URL_MAX_LENGTH:
        return [ValidationError(URL_TOO_LONG, f"URL too long (max {URL_MAX_LENGTH}).", field)]
    if not _URL_PATTERN.match(value):
        return [ValidationError(URL_INVALID, "Invalid URL — must start with https://.", field)]
    return []


def validate_licence(licence: str | None) -> list[ValidationError]:
    if licence and len(licence) > LICENCE_MAX_LENGTH:
        return [ValidationError(LICENCE_TOO_LONG, f"Licence too long (max {LICENCE_MAX_LENGTH}).", "licence")]
    return []


# ── Release validation ──────────────────────────────────────────────────────


def validate_release_version(version: str | None) -> list[ValidationError]:
    errors: list[ValidationError] = []
    if not version or not version.strip():
        errors.append(ValidationError(RELEASE_VERSION_EMPTY, "Version is required.", "version"))
        return errors
    version = version.strip()
    if len(version) > RELEASE_VERSION_MAX_LENGTH:
        errors.append(ValidationError(
            RELEASE_VERSION_TOO_LONG,
            f"Version must be at most {RELEASE_VERSION_MAX_LENGTH} characters.",
            "version",
        ))
        return errors
    if not _SEMVER_PATTERN.match(version):
        errors.append(ValidationError(
            RELEASE_VERSION_INVALID,
            "Version must follow semver (e.g. 1.2.3).",
            "version",
        ))
    return errors


def validate_release_changelog(changelog: str | None) -> list[ValidationError]:
    if changelog and len(changelog) > RELEASE_CHANGELOG_MAX_LENGTH:
        return [ValidationError(
            RELEASE_CHANGELOG_TOO_LONG,
            f"Changelog must be at most {RELEASE_CHANGELOG_MAX_LENGTH:,} characters.",
            "changelog",
        )]
    return []


def validate_install_instructions(instructions: str | None) -> list[ValidationError]:
    if instructions and len(instructions) > RELEASE_INSTALL_INSTRUCTIONS_MAX_LENGTH:
        return [ValidationError(
            RELEASE_INSTALL_INSTRUCTIONS_TOO_LONG,
            f"Install instructions must be at most {RELEASE_INSTALL_INSTRUCTIONS_MAX_LENGTH:,} characters.",
            "install_instructions",
        )]
    return []


def validate_config_json(config_json: Any) -> list[ValidationError]:
    if config_json is None:
        return []
    import json
    size = len(json.dumps(config_json).encode("utf-8"))
    if size > CONFIG_JSON_MAX_BYTES:
        return [ValidationError(
            CONFIG_JSON_TOO_LARGE,
            f"Config JSON must be at most {CONFIG_JSON_MAX_BYTES // 1024} KB.",
            "config_json",
        )]
    return []


# ── Aggregate validators ────────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[ValidationError, ...]


def validate_listing_create(
    *,
    title: str | None,
    description: str | None,
    long_description: str | None = None,
    price_sol: Decimal | None = None,
    category_ids: list[int] | None = None,
    tag_ids: list[int] | None = None,
) -> ValidationResult:
    errors: list[ValidationError] = []
    errors.extend(validate_title(title))
    errors.extend(validate_description(description))
    errors.extend(validate_long_description(long_description))
    errors.extend(validate_price(price_sol))
    errors.extend(validate_categories(category_ids))
    errors.extend(validate_tags(tag_ids))
    return ValidationResult(is_valid=len(errors) == 0, errors=tuple(errors))


def validate_listing_update(
    *,
    title: str | None = None,
    description: str | None = None,
    long_description: str | None = None,
    price_sol: Decimal | None = None,
    category_ids: list[int] | None = None,
    tag_ids: list[int] | None = None,
) -> ValidationResult:
    """Only validate fields that are explicitly provided (non-None)."""
    errors: list[ValidationError] = []
    if title is not None:
        errors.extend(validate_title(title))
    if description is not None:
        errors.extend(validate_description(description))
    if long_description is not None:
        errors.extend(validate_long_description(long_description))
    if price_sol is not None:
        errors.extend(validate_price(price_sol))
    if category_ids is not None:
        errors.extend(validate_categories(category_ids))
    if tag_ids is not None:
        errors.extend(validate_tags(tag_ids))
    return ValidationResult(is_valid=len(errors) == 0, errors=tuple(errors))


def validate_release_create(
    *,
    version: str | None,
    changelog: str | None = None,
    config_json: Any = None,
    install_instructions: str | None = None,
) -> ValidationResult:
    errors: list[ValidationError] = []
    errors.extend(validate_release_version(version))
    errors.extend(validate_release_changelog(changelog))
    errors.extend(validate_config_json(config_json))
    errors.extend(validate_install_instructions(install_instructions))
    return ValidationResult(is_valid=len(errors) == 0, errors=tuple(errors))