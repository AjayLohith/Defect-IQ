from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class ProcessStep(Base):
    __tablename__ = "process_steps"

    process_step_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    step_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_quality_gate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    standard_cycle_time_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    allowed_machine_type: Mapped[str] = mapped_column(String(32), nullable=False)

    process_executions = relationship("ProcessExecution", back_populates="process_step")
    inspection_plans = relationship("InspectionPlan", back_populates="process_step")


class ProcessExecution(Base):
    __tablename__ = "process_executions"

    process_execution_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    production_order_id: Mapped[str] = mapped_column(String(32), ForeignKey("production_orders.production_order_id"), nullable=False)
    process_step_id: Mapped[str] = mapped_column(String(32), ForeignKey("process_steps.process_step_id"), nullable=False)
    machine_id: Mapped[str] = mapped_column(String(32), ForeignKey("machines.machine_id"), nullable=False)
    execution_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    execution_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    input_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    output_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    rework_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    scrap_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    quarantined_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    execution_status: Mapped[str] = mapped_column(String(32), default="COMPLETED", nullable=False)
    drift_indicator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    process_measurement: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    production_order = relationship("ProductionOrder", back_populates="process_executions")
    process_step = relationship("ProcessStep", back_populates="process_executions")
    machine = relationship("Machine", back_populates="process_executions")
    inspection_results = relationship("InspectionResult", back_populates="process_execution")
    defects = relationship("Defect", back_populates="process_execution")

