"""
In this file, the focus is on immutability.
In the world of business compliance, being able to prove that
"this is exactly what the law said at 10:00 AM on Tuesday"
is a high-value feature.
Use the hashlib library to create a digital seal.
"""

import hashlib
from sentinel.schema import RegEvent


def generate_fingerprint(text: str) -> str:
    """Creates a unique SHA-256 hash to act as a digital seal."""

    # Encode utf-8 as hashlib requires bytes
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def secure_event(event: RegEvent) -> RegEvent:
    """Applies a fingerprint to a RegEvent and returns it."""

    # Hash the content field specifically to detect text changes
    event.fingerprint = generate_fingerprint(event.content)
    return event


def verify_integrity(event: RegEvent) -> bool:
    """Checks if the current content still matches the original fingerprint."""

    # This allows a business to audit their data for tampering
    current_hash = generate_fingerprint(event.content)
    return current_hash == event.fingerprint
