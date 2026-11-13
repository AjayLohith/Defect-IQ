from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(32), nullable=False)
    revision: Mapped[str] = mapped_column(String(16), default="A", nullable=False)
    base_uom: Mapped[str] = mapped_column(String(16), default="EA", nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    boms = relationship("BOM", back_populates="product")
    production_orders = relationship("ProductionOrder", back_populates="product")

