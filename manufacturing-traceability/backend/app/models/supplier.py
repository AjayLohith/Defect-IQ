from datetime import date
from typing import Optional
from sqlalchemy import String, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    supplier_status: Mapped[str] = mapped_column(String(32), default="QUALIFIED", nullable=False)
    supplier_risk_tier: Mapped[str] = mapped_column(String(32), default="TIER_1_LOW", nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=14, nullable=False)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    material_lots = relationship("MaterialLot", back_populates="supplier")

