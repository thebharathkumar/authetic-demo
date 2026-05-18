from dataclasses import dataclass

from app.models import CoverageType
from app.risk_model import RiskAssessment
from app.schemas import QuoteRequest, QuoteResponseItem


@dataclass(frozen=True)
class CarrierPlan:
    carrier_name: str
    price_factor: float
    deductible: int
    coverage_limits: dict[CoverageType, int]
    service_score: float
    strength: str


CARRIER_PLANS = [
    CarrierPlan(
        carrier_name="Northstar Mutual",
        price_factor=0.94,
        deductible=1000,
        coverage_limits={CoverageType.AUTO: 100_000, CoverageType.HOME: 450_000, CoverageType.RENTERS: 35_000, CoverageType.LIFE: 250_000},
        service_score=88,
        strength="balanced premium and broad limits",
    ),
    CarrierPlan(
        carrier_name="Harbor Shield",
        price_factor=0.86,
        deductible=1500,
        coverage_limits={CoverageType.AUTO: 75_000, CoverageType.HOME: 350_000, CoverageType.RENTERS: 25_000, CoverageType.LIFE: 200_000},
        service_score=80,
        strength="lowest-cost option for price-sensitive shoppers",
    ),
    CarrierPlan(
        carrier_name="Pioneer Assurance",
        price_factor=1.08,
        deductible=750,
        coverage_limits={CoverageType.AUTO: 150_000, CoverageType.HOME: 600_000, CoverageType.RENTERS: 50_000, CoverageType.LIFE: 500_000},
        service_score=94,
        strength="higher limits and stronger coverage quality",
    ),
    CarrierPlan(
        carrier_name="Summit Casualty",
        price_factor=1.0,
        deductible=500,
        coverage_limits={CoverageType.AUTO: 125_000, CoverageType.HOME: 500_000, CoverageType.RENTERS: 40_000, CoverageType.LIFE: 350_000},
        service_score=90,
        strength="low deductible with competitive protection",
    ),
]

BASE_PREMIUMS = {
    CoverageType.AUTO: 110.0,
    CoverageType.HOME: 165.0,
    CoverageType.RENTERS: 24.0,
    CoverageType.LIFE: 42.0,
}


def generate_quotes(request: QuoteRequest, risk: RiskAssessment) -> list[QuoteResponseItem]:
    """Create mock carrier quotes ranked by value (price plus coverage quality)."""

    quotes: list[QuoteResponseItem] = []
    base = BASE_PREMIUMS[request.coverage_type]
    risk_multiplier = 0.72 + (risk.score / 100)
    claims_multiplier = 1 + (request.prior_claims * 0.045)

    for plan in CARRIER_PLANS:
        premium = round(base * risk_multiplier * claims_multiplier * plan.price_factor, 2)
        coverage_limit = plan.coverage_limits[request.coverage_type]
        limit_score = min(100, coverage_limit / max(BASE_PREMIUMS[request.coverage_type], 1) / 45)
        deductible_score = max(45, 100 - (plan.deductible / 25))
        coverage_score = round((plan.service_score * 0.45) + (limit_score * 0.35) + (deductible_score * 0.20), 1)
        value_score = round((coverage_score * 0.62) + ((base * 1.8 / premium) * 38), 1)
        quotes.append(
            QuoteResponseItem(
                carrier_name=plan.carrier_name,
                monthly_premium=premium,
                deductible=plan.deductible,
                coverage_limit=coverage_limit,
                coverage_score=coverage_score,
                value_score=value_score,
                risk_score=risk.score,
                rank=0,
                rationale=f"{plan.strength}; priced for a {risk.tier.lower()} risk tier.",
            )
        )

    ranked = sorted(quotes, key=lambda quote: (-quote.value_score, quote.monthly_premium))
    return [quote.model_copy(update={"rank": index}) for index, quote in enumerate(ranked, start=1)]
