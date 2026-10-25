import asyncio

from sentinel.analyser import RegulatoryAnalyser
from sentinel.auditor import BusinessProfile, ComplianceAuditor
from sentinel.core import generate_fingerprint, verify_integrity
from sentinel.ingestors import fetch_real_page
from sentinel.schema import RegEvent


async def main():
    print(
        "=================== 🌌 HORIZONSENTINEL COMPLETE PIPELINE ==================="
    )

    # Define UK Firm's internal profile parameters
    uk_firm = BusinessProfile(
        company_name="Horizon Capital UK", # Mock company
        handles_crypto=True,
        daily_transaction_limit_gbp=5000.0,
        has_reporting_framework=False,
    )

    # Target a live sandbox URL using your browser engine
    target_url = "http://quotes.toscrape.com/js/"
    print("📡 Ingesting live asset updates via Playwright browser matrix...")
    print(f"🔗 Target: {target_url}")

    try:
        live_event = await fetch_real_page(target_url, use_browser=True)
    except Exception as e:  # noqa: BLE001 - top-level pipeline boundary, must not crash on any ingestion failure
        print(f"❌ CRITICAL Ingestion Failure: {e}")
        return

    # Create a brand new, legally sealed RegEvent
    # combining the live quotes text with regulatory test clauses.
    hybrid_text = (
        live_event.content
        + " Crucial Note: All crypto tracking and transaction reporting framework rules must be enforced."
    )
    new_fingerprint = generate_fingerprint(hybrid_text)

    secured_event = RegEvent(
        source_name=live_event.source_name,
        url=live_event.url,
        title=live_event.title,
        content=hybrid_text,
        fetched_at=live_event.fetched_at,
        fingerprint=new_fingerprint,
    )

    # Cryptographic Shield Verification
    is_secure = verify_integrity(secured_event)
    print(f"\n🔒 Data Security Shield Intact: {is_secure}")

    if not is_secure:
        print(
            "❌ CRITICAL ERROR: Security verification failed! Terminating audit loops."
        )
        return

    # Run the Analyser Engine
    print("🧠 Activating Regulatory Analyser Engine...")
    analysis_report = RegulatoryAnalyser.analyse_event(secured_event)

    # Trigger the Auditor Matrix
    print("⚖️ Initiating Compliance Auditor Evaluation...")
    audit_results = ComplianceAuditor.evaluate_compliance(analysis_report, uk_firm)

    # Output the Final Structural Compliance Ledger Dashboard
    print("\n👑 ================= FINAL COMPLIANCE AUDIT LEDGER ================= 👑")
    print(f"🏢 Target Firm      : {uk_firm.company_name}")
    print(
        f"📜 Ruleset Baseline : {analysis_report.title} ({analysis_report.source_name})"
    )
    print(f"🚦 Audit Risk Status: {audit_results.risk_score}")
    print("\n🔍 EVALUATION FINDINGS:")
    for finding in audit_results.findings:
        print(f"  {finding}")
    print("==========================================================================")


if __name__ == "__main__":
    asyncio.run(main())
