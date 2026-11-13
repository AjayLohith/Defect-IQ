from datetime import date
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class BOM(Base):
    __tablename__ = "boms"

    bom_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(32), ForeignKey("products.product_id"), nullable=False)
    revision: Mapped[str] = mapped_column(String(16), default="A", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    product = relationship("Product", back_populates="boms")
    bom_lines = relationship("BOMLine", back_populates="bom")


class BOMLine(Base):
    __tablename__ = "bom_lines"

    bom_line_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    bom_id: Mapped[str] = mapped_column(String(32), ForeignKey("boms.bom_id"), nullable=False)
    material_product_id: Mapped[str] = mapped_column(String(32), ForeignKey("products.product_id"), nullable=False)
    quantity_per_unit: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    uom: Mapped[str] = mapped_column(String(16), nullable=False)
    scrap_factor: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.02"), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    bom = relationship("BOM", back_populates="bom_lines")
    material_product = relationship("Product")

