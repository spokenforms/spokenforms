from __future__ import annotations


class SpokenFormsError(Exception):
    """Base exception for package errors."""


class ConfigError(SpokenFormsError):
    """Raised when configuration is invalid."""


class SensitivePolicyError(SpokenFormsError):
    """Raised when sensitive-data guardrails reject a request."""
