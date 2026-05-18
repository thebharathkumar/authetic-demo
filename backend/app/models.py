from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoverageType(StrEnum):
    AUTO = "auto"
    HOME = "home"
    RENTERS = "renters"
    LIFE = "life"


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    coverage_type: Mapped[CoverageType] = mapped_column(Enum(CoverageType), nullable=False)
    household_income: Mapped[int] = mapped_column(Integer, nullable=False)
    owns_home: Mapped[bool] = mapped_column(nullable=False, default=False)
    prior_claims: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    quotes: Mapped[list["QuoteOption"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class QuoteOption(Base):
    __tablename__ = "quote_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    carrier_name: Mapped[str] = mapped_column(String(80), nullable=False)
    monthly_premium: Mapped[float] = mapped_column(Float, nullable=False)
    deductible: Mapped[int] = mapped_column(Integer, nullable=False)
    coverage_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    coverage_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    profile: Mapped[CustomerProfile] = relationship(back_populates="quotes")
