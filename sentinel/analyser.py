"""
Handles extraction of compliance constraints,
thresholds, and business impacts from raw data
"""

import re

from pydantic import BaseModel

from sentinel.schema import RegEvent


class AnalysedRegulation(BaseModel):
    """Represents a structured, machine-readable breakdown of a regulation text."""

    source_name: str
    title: str
    extracted_thresholds: list[str]
    impact_keywords: list[str]
    obligation_level: str
    summary_snippet: str


class RegulatoryAnalyser:
    """Engine responsible for filtering and parsing unstructured compliance text."""

    @staticmethod
    def extracted_thresholds(text: str) -> list[str]:
        """Scans the text for currency limits, percentages, or numeric compliance boundaries."""
        # This matches the method name called inside analyse_event exactly
        financial_pattern = (
            r"(?:£|\$|€)\s*\d+(?:\.\d+)?\s*(?:[kKmMbB]|thousand|million)?|\d+\s*%\s*"
        )
        matches = re.findall(financial_pattern, text)
        return [match.strip() for match in matches]

    @staticmethod
    def identify_impact_scope(text: str) -> list[str]:
        """Identifies which business domains or technologies are targeted by the rule."""
        target_domains = [
            "crypto",
            "digital assets",
            "banking",
            "payments",
            "reporting",
            "security",
            "privacy",
            "aml",
            "kyc",
            "transaction",
        ]
        text_lower = text.lower()
        return [domain for domain in target_domains if domain in text_lower]

    @staticmethod
    def determine_obligation_level(text: str) -> str:
        """Determines if the text implies a binding legal requirement or an advice note."""

        text_lower = text.lower()

        # Hard compliance indicators
        critical_indicators = ["must", "shall", "required", "mandatory", "enforced"]
        # Soft compliance indicators
        advisory_indicators = [
            "should",
            "may",
            "recommend",
            "best practice",
            "guidance",
        ]

        if any(word in text_lower for word in critical_indicators):
            return "🔴 MANDATORY REQUIREMENT (CRITICAL)"
        elif any(word in text_lower for word in advisory_indicators):
            return "🟡 ADVISORY GUIDELINE (MEDIUM)"
        return "⚪ INFORMATION NOTICE (LOW)"

    @classmethod
    def analyse_event(cls, event: RegEvent) -> AnalysedRegulation:
        """
        Accepts a cryptographically secured RegEvent, processes its contents,
        and outputs a high-fidelity AnalysedRegulation object.
        """

        # This now triggers the newly added staticmethod smoothly!
        thresholds = cls.extracted_thresholds(event.content)
        impacts = cls.identify_impact_scope(event.content)
        obligation = cls.determine_obligation_level(event.content)

        # Create a clean, abbreviated preview snippet
        summary_snippet = (
            event.content[:120] + "..." if len(event.content) > 120 else event.content
        )

        return AnalysedRegulation(
            source_name=event.source_name,
            title=event.title,
            extracted_thresholds=thresholds,
            impact_keywords=impacts,
            obligation_level=obligation,
            summary_snippet=summary_snippet,
        )
