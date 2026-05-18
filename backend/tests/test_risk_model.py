from app.models import CoverageType
from app.risk_model import calculate_risk
from app.schemas import QuoteRequest


def test_risk_model_rewards_lower_risk_profile():
    preferred = calculate_risk(
        QuoteRequest(
            age=42,
            zip_code="50309",
            state="IA",
            coverage_type=CoverageType.RENTERS,
            household_income=120000,
            owns_home=True,
            prior_claims=0,
        )
    )
    elevated = calculate_risk(
        QuoteRequest(
            age=22,
            zip_code="33101",
            state="FL",
            coverage_type=CoverageType.AUTO,
            household_income=32000,
            owns_home=False,
            prior_claims=3,
        )
    )

    assert preferred.score < elevated.score
    assert preferred.tier == "Preferred"
    assert elevated.tier in {"Elevated", "High"}
    assert any("prior claim" in factor for factor in elevated.factors)
