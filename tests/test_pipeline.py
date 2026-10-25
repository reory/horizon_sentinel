import pytest
from hypothesis import given
from hypothesis import strategies as st
from sentinel.analyser import AnalysedRegulation, RegulatoryAnalyser
from sentinel.auditor import BusinessProfile, ComplianceAuditor
from sentinel.core import generate_fingerprint, secure_event, verify_integrity
from sentinel.schema import RegEvent


def test_crypto_shield_valid_seal():
    """Verifies that a perfectly sealed RegEvent passes integrity checks."""

    content = "All cryptogrpahic tracking rules must be enforced."
    fingerprint = generate_fingerprint(content)

    event = RegEvent(
        source_name="FCA Feed",
        url="http://example.com",
        title="Cryptography Rules",
        content=content,
        fingerprint=fingerprint,
    )

    assert verify_integrity(event) is True


def test_crypto_shield_detects_tampering():
    """Verifies that altering a single character causes the shield to fail."""

    content = "All cryptographic tracking rules must be enforced."
    fingerprint = generate_fingerprint(content)

    event = RegEvent(
        source_name="FCA Feed",
        url="http://example.com",
        title="Cryptography rules",
        content=content,
        fingerprint=fingerprint,
    )

    # Simulate a malicious change
    event.content = "All cryptographic tracking rules must be ignored."

    assert verify_integrity(event) is False


def test_secure_event_applies_seal():
    """Brings core.py to 100% coverage by exercising secure_event."""

    event = RegEvent(
        source_name="FCA", url="http://x.com", title="TT", content="Secured"
    )

    assert event.fingerprint is None  # Starts unsealed

    sealed_event = secure_event(event)
    assert sealed_event.fingerprint is not None  # Successfully sealed


def test_auditor_flags_non_compliance():
    """Exercise the compliance matrix"""

    firm = BusinessProfile(
        company_name="Test Firm",
        handles_crypto=False,
        daily_transaction_limit_gbp=1000.0,
        has_reporting_framework=False,
    )

    analysis = AnalysedRegulation(
        source_name="FCA",
        title="Rule",
        extracted_thresholds=[],
        impact_keywords=["crypto"],
        obligation_level="🔴 MANDATORY REQUIREMENT (CRITICAL)",
        summary_snippet="Must report tracking.",
    )

    result = ComplianceAuditor.evaluate_compliance(analysis, firm)
    assert result.risk_score == "⚠️ ATTENTION REQUIRED (MEDIUM RISK)"


# ----------------------------------------------------------------------------


@given(st.text())
def test_crypto_shield_invariance_property(random_text):
    """
    Hypothesis test: No matter what random string text is fed into
    the engine, a correct signature must ALWAYS pass validation.
    """

    fingerprint = generate_fingerprint(random_text)
    event = RegEvent(
        source_name="TEST",
        url="http://test.com",
        title="Test Title",
        content=random_text,
        fingerprint=fingerprint,
    )

    assert verify_integrity(event) is True


@given(st.text())
def test_analyser_never_crashes_on_garbage_input(random_text):
    """
    Hypothesis stress test: Ensures that the RegulatoryAnalyser regex functions
    and string splits never crash out with an unhandled exception, even if
    the scraped website text returns total binary gibberish or symbols.
    """

    fingerprint = generate_fingerprint(random_text)
    event = RegEvent(
        source_name="TEST",
        url="http://test.com",
        title="Test Title",
        content=random_text,
        fingerprint=fingerprint,
    )

    # Code execution should be smooth and return a structure
    analysis = RegulatoryAnalyser.analyse_event(event)
    assert isinstance(analysis.extracted_thresholds, list)
    assert isinstance(analysis.impact_keywords, list)


# -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected_obligation",
    [
        (
            "The firm must maintain cash thresholds.",
            "🔴 MANDATORY REQUIREMENT (CRITICAL)",
        ),
        (
            "The company shall declare financial boundaries.",
            "🔴 MANDATORY REQUIREMENT (CRITICAL)",
        ),
        (
            "Operators should follow optimal guidance rules.",
            "🟡 ADVISORY GUIDELINE (MEDIUM)",
        ),
        (
            "General information bulletin note regarding crypto.",
            "⚪ INFORMATION NOTICE (LOW)",
        ),
    ],
)
def test_obligation_level_classification(text, expected_obligation):
    """Verfies that legal statutory language weight are mapped precisely."""

    fingerprint = generate_fingerprint(text)
    event = RegEvent(
        source_name="TEST",
        url="http://test.com",
        title="Test Title",
        content=text,
        fingerprint=fingerprint,
    )

    analysis = RegulatoryAnalyser.analyse_event(event)
    assert analysis.obligation_level == expected_obligation


def test_financial_threshold_extraction():
    """
    Validates that regex expressions smoothly harvest diverse currencies and bounds.
    """

    text = "Compliance triggers hit at £10k and values over £50k, along with a 25% penalty."
    fingerprint = generate_fingerprint(text)
    event = RegEvent(
        source_name="TEST",
        url="http://test.com",
        title="Test Title",
        content=text,
        fingerprint=fingerprint,
    )

    analysis = RegulatoryAnalyser.analyse_event(event)

    # Ensure regex patterns isolated the bounds successfully
    assert "£10k" in analysis.extracted_thresholds
    assert "£50k" in analysis.extracted_thresholds
    assert "25%" in analysis.extracted_thresholds
