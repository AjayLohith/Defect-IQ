from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class ProductionOrder(Base):
    __tablename__ = "production_orders"

    production_order_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(32), ForeignKey("products.product_id"), nullable=False)
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    completed_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    accepted_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    rework_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    scrap_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    quarantined_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    order_status: Mapped[str] = mapped_column(String(32), default="PLANNED", nullable=False)
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    production_lot_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    product = relationship("Product", back_populates="production_orders")
    consumptions = relationship("MaterialConsumption", back_populates="production_order")
    process_executions = relationship("ProcessExecution", back_populates="production_order")
    inspection_results = relationship("InspectionResult", back_populates="production_order")
    defects = relationship("Defect", back_populates="production_order")


class MaterialConsumption(Base):
    __tablename__ = "material_consumptions"

    consumption_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    production_order_id: Mapped[str] = mapped_column(String(32), ForeignKey("production_orders.production_order_id"), nullable=False)
    material_lot_id: Mapped[str] = mapped_column(String(64), ForeignKey("material_lots.material_lot_id"), nullable=False)
    bom_line_id: Mapped[str] = mapped_column(String(32), ForeignKey("bom_lines.bom_line_id"), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    uom: Mapped[str] = mapped_column(String(16), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumption_status: Mapped[str] = mapped_column(String(32), default="COMMITTED", nullable=False)

    production_order = relationship("ProductionOrder", back_populates="consumptions")
    material_lot = relationship("MaterialLot", back_populates="consumptions")
    bom_line = relationship("BOMLine")

