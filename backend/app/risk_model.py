from dataclasses import dataclass

from app.models import CoverageType
from app.schemas import QuoteRequest

HIGH_COST_STATES = {"CA", "FL", "NY", "TX", "NJ"}
MODERATE_COST_STATES = {"AZ", "CO", "GA", "IL", "MA", "MD", "NC", "OR", "PA", "VA", "WA"}


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    tier: str
    factors: list[str]


def calculate_risk(request: QuoteRequest) -> RiskAssessment:
    """Return a transparent mock actuarial risk score from 0 (low) to 100 (high)."""

    score = 35.0
    factors: list[str] = ["Base demographic and regional exposure"]

    if request.age < 25:
        score += 16
        factors.append("Younger applicant age increases loss volatility")
    elif request.age > 70:
        score += 8
        factors.append("Senior applicant age adds moderate underwriting risk")
    elif 30 <= request.age <= 55:
        score -= 5
        factors.append("Prime-age applicant lowers expected claim volatility")

    if request.state in HIGH_COST_STATES:
        score += 10
        factors.append(f"{request.state} has elevated replacement and claim costs")
    elif request.state in MODERATE_COST_STATES:
        score += 4
        factors.append(f"{request.state} has moderate market-cost pressure")
    else:
        score -= 2
        factors.append(f"{request.state} has lower modeled cost pressure")

    coverage_adjustments = {
        CoverageType.AUTO: (8, "Auto coverage carries higher claim frequency"),
        CoverageType.HOME: (5, "Home coverage reflects property replacement exposure"),
        CoverageType.RENTERS: (-4, "Renters coverage usually has lower severity"),
        CoverageType.LIFE: (2, "Life coverage uses a flatter mock mortality factor"),
    }
    adjustment, reason = coverage_adjustments[request.coverage_type]
    score += adjustment
    factors.append(reason)

    if request.household_income >= 100_000:
        score -= 4
        factors.append("Higher income proxy improves payment stability")
    elif request.household_income < 40_000:
        score += 5
        factors.append("Lower income proxy adds affordability risk")

    if request.owns_home:
        score -= 3
        factors.append("Home ownership proxy lowers stability risk")

    if request.prior_claims:
        claim_penalty = min(request.prior_claims * 7, 24)
        score += claim_penalty
        factors.append(f"{request.prior_claims} prior claim(s) add {claim_penalty} risk points")
    else:
        score -= 3
        factors.append("No prior claims improves expected loss ratio")

    bounded_score = round(max(1.0, min(score, 100.0)), 1)
    if bounded_score < 35:
        tier = "Preferred"
    elif bounded_score < 60:
        tier = "Standard"
    elif bounded_score < 80:
        tier = "Elevated"
    else:
        tier = "High"

    return RiskAssessment(score=bounded_score, tier=tier, factors=factors)
