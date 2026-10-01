"""Helpers for validating post-login redirect targets."""

from typing import Optional
from urllib.parse import urlparse


def safe_internal_next_url(next_url: Optional[str]) -> Optional[str]:
    """Return next_url only when it is a safe same-origin relative path.

    A valid path must:
    - be non-empty after strip
    - start with a single '/'
    - not start with '//' (protocol-relative / open redirect)
    - not contain a URL scheme (e.g. http:, https:, javascript:)
    """
    if next_url is None:
        return None

    candidate = next_url.strip()
    if not candidate:
        return None

    if not candidate.startswith("/") or candidate.startswith("//"):
        return None

    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        return None

    # Reject sneakier absolute forms that still parse as relative-ish.
    lowered = candidate.lower()
    if "://" in candidate or lowered.startswith("javascript:"):
        return None

    return candidate
