"""
Define what a "Regulatory Event" looks like.
Use Pydantic because it forces the data to be perfect.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RegEvent(BaseModel):
    """Represents a single verified regulatory update."""

    # Name of the regulator (eg, FCA, SEC,)
    source_name: str
    # The headline or rule number
    title: str
    # The full text/summary of the change
    content: str
    # Direct link to the official source
    url: str
    # Automatically records the date and time when the data is received
    fetched_at: datetime = Field(default_factory=datetime.now)
    # SHA-256 hash of content to ensure the data hasn't been tampered with
    fingerprint: str | None = None
