from functools import lru_cache

from fastapi import APIRouter, Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import CustomerProfile, QuoteOption
from app.quote_engine import generate_quotes
from app.risk_model import calculate_risk
from app.schemas import QuoteComparisonResponse, QuoteRequest, RiskScore


@lru_cache
def ensure_database() -> None:
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Insurance Quote Comparison API",
    version="0.1.0",
    description="Mock insurance quote comparison with transparent Python risk scoring.",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/quotes", response_model=QuoteComparisonResponse)
def compare_quotes(request: QuoteRequest, db: Session = Depends(get_db)) -> QuoteComparisonResponse:
    ensure_database()
    risk = calculate_risk(request)
    quotes = generate_quotes(request, risk)

    profile = CustomerProfile(**request.model_dump())
    db.add(profile)
    db.flush()

    for quote in quotes:
        db.add(
            QuoteOption(
                profile_id=profile.id,
                carrier_name=quote.carrier_name,
                monthly_premium=quote.monthly_premium,
                deductible=quote.deductible,
                coverage_limit=quote.coverage_limit,
                coverage_score=quote.coverage_score,
                risk_score=quote.risk_score,
                rank=quote.rank,
                rationale=quote.rationale,
            )
        )
    db.commit()
    db.refresh(profile)

    return QuoteComparisonResponse(
        profile_id=profile.id,
        risk=RiskScore(score=risk.score, tier=risk.tier, factors=risk.factors),
        quotes=quotes,
    )


@app.get("/api/docs", include_in_schema=False)
def vercel_docs() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title=f"{app.title} - Swagger UI")


@app.get("/api/openapi.json", include_in_schema=False)
def vercel_openapi() -> dict:
    return app.openapi()


app.include_router(router)
app.include_router(router, prefix="/api")
