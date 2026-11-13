from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Date, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class InspectionPlan(Base):
    __tablename__ = "inspection_plans"

    inspection_plan_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_id: Mapped[str] = mapped_column(String(32), ForeignKey("products.product_id"), nullable=False)
    process_step_id: Mapped[str] = mapped_column(String(32), ForeignKey("process_steps.process_step_id"), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String(32), default="IN_PROCESS", nullable=False)
    sampling_rule: Mapped[str] = mapped_column(String(32), default="ANSI_ASQ_Z1_4", nullable=False)
    acceptance_limit: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.01"), nullable=False)
    defect_categories: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    effective_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    plan_status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)

    product = relationship("Product")
    process_step = relationship("ProcessStep", back_populates="inspection_plans")
    inspection_results = relationship("InspectionResult", back_populates="inspection_plan")


class InspectionResult(Base):
    __tablename__ = "inspection_results"

    inspection_result_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    inspection_plan_id: Mapped[str] = mapped_column(String(32), ForeignKey("inspection_plans.inspection_plan_id"), nullable=False)
    production_order_id: Mapped[str] = mapped_column(String(32), ForeignKey("production_orders.production_order_id"), nullable=False)
    process_execution_id: Mapped[str] = mapped_column(String(32), ForeignKey("process_executions.process_execution_id"), nullable=False)
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    inspected_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    accepted_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    reworked_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    scrapped_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    quarantined_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    inspection_status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    disposition: Mapped[str] = mapped_column(String(32), default="ACCEPTED", nullable=False)
    defect_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=Decimal("0.0"), nullable=False)

    inspection_plan = relationship("InspectionPlan", back_populates="inspection_results")
    production_order = relationship("ProductionOrder", back_populates="inspection_results")
    process_execution = relationship("ProcessExecution", back_populates="inspection_results")
    defects = relationship("Defect", back_populates="inspection_result")

