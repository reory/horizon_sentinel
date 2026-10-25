"""
Handles auditing analyzed regulations against an internal business risk profile
to flag operational discrepancies or compliance non-conformances.
"""

from pydantic import BaseModel

from sentinel.analyser import AnalysedRegulation


class BusinessProfile(BaseModel):
    """Represents the internal operational params of the firm being audited."""

    company_name: str
    handles_crypto: bool  # Cryptography
    daily_transaction_limit_gbp: float
    has_reporting_framework: bool


class AuditReport(BaseModel):
    """
    The structured result of evaluating a regulation against a business profile.
    """

    is_compliant: bool
    risk_score: str
    findings: list[str]


class ComplianceAuditor:
    """
    Engine responsible for executing rule checks against active business
    profiles.
    """

    @staticmethod
    def evaluate_compliance(
        regulation: AnalysedRegulation, profile: BusinessProfile
    ) -> AuditReport:
        """
        Cross-references an extracted regulatory analysis against
        the business profile to discover structural operational gaps.
        """

        findings = []
        is_compliant = True

        # Evaluation check
        if "crypto" in regulation.impact_keywords and not profile.handles_crypto:
            findings.append(
                f"⚠️ Scope Warning: This update affects 'finance' systems "
                f"{profile.company_name} is currently flagged as non-crypto handling."
            )

        # Obligation intensity check
        if (
            regulation.obligation_level == "🔴 MANDATORY REQUIREMENT (CRITICAL)"
            and "reporting" in regulation.impact_keywords
            and not profile.has_reporting_framework
        ):
            is_compliant = False
            findings.append(
                "🚫 NON-CONFORMANCE: This rule mandates active reporting "
                "but the firm lacks an active reporting framework."
            )

        # Default safe confirmation if no gaps are found
        if not findings:
            risk_score = "✅ FULL COMPLIANCE (LOW RISK)"
            findings.append(
                "No immediate friction or compliance gaps "
                "detected for this rule payload."
            )
        elif not is_compliant:
            risk_score = "🔴 CRITICAL VIOLATION (HIGH RISK)"
        else:
            risk_score = "⚠️ ATTENTION REQUIRED (MEDIUM RISK)"

        return AuditReport(
            is_compliant=is_compliant, risk_score=risk_score, findings=findings
        )
