from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, computed_field

from app.models import CoverageType


class QuoteRequest(BaseModel):
    age: Annotated[int, Field(ge=18, le=100, examples=[34])]
    zip_code: Annotated[str, StringConstraints(pattern=r"^\d{5}$")] = Field(examples=["94105"])
    state: Annotated[str, StringConstraints(min_length=2, max_length=2, to_upper=True)] = Field(examples=["CA"])
    coverage_type: CoverageType = Field(examples=[CoverageType.AUTO])
    household_income: Annotated[int, Field(ge=0, le=1_000_000)] = 85000
    owns_home: bool = False
    prior_claims: Annotated[int, Field(ge=0, le=10)] = 0


class RiskScore(BaseModel):
    score: float
    tier: str
    factors: list[str]


class QuoteResponseItem(BaseModel):
    carrier_name: str
    monthly_premium: float
    deductible: int
    coverage_limit: int
    coverage_score: float
    value_score: float
    risk_score: float
    rank: int
    rationale: str


class QuoteComparisonResponse(BaseModel):
    profile_id: int
    risk: RiskScore
    quotes: list[QuoteResponseItem]

    @computed_field
    @property
    def best_quote(self) -> QuoteResponseItem | None:
        return self.quotes[0] if self.quotes else None
