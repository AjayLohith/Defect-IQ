from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class Defect(Base):
    __tablename__ = "defects"

    defect_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    inspection_result_id: Mapped[str] = mapped_column(String(64), ForeignKey("inspection_results.inspection_result_id"), nullable=False)
    production_order_id: Mapped[str] = mapped_column(String(32), ForeignKey("production_orders.production_order_id"), nullable=False)
    process_execution_id: Mapped[str] = mapped_column(String(32), ForeignKey("process_executions.process_execution_id"), nullable=False)
    machine_id: Mapped[str] = mapped_column(String(32), ForeignKey("machines.machine_id"), nullable=False)
    material_lot_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("material_lots.material_lot_id"), nullable=True)
    reported_material_lot_id: Mapped[str] = mapped_column(String(64), nullable=False)
    supplier_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("suppliers.supplier_id"), nullable=True)
    defect_code: Mapped[str] = mapped_column(String(32), nullable=False)
    defect_category: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="MINOR", nullable=False)
    defect_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("1.0"), nullable=False)
    suspected_source: Mapped[str] = mapped_column(String(32), default="MACHINE", nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    defect_status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)

    inspection_result = relationship("InspectionResult", back_populates="defects")
    production_order = relationship("ProductionOrder", back_populates="defects")
    process_execution = relationship("ProcessExecution", back_populates="defects")
    machine = relationship("Machine", back_populates="defects")
    material_lot = relationship("MaterialLot", back_populates="defects")
    supplier = relationship("Supplier")
    containment_actions = relationship("ContainmentAction", back_populates="defect")
    corrective_actions = relationship("CorrectiveAction", back_populates="defect")


class ContainmentAction(Base):
    __tablename__ = "containment_actions"

    containment_action_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    defect_id: Mapped[str] = mapped_column(String(32), ForeignKey("defects.defect_id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(32), default="QUARANTINE_LOT", nullable=False)
    owner_role: Mapped[str] = mapped_column(String(32), default="QUALITY_ENGINEER", nullable=False)
    action_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    affected_quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.0"), nullable=False)
    containment_status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    defect = relationship("Defect", back_populates="containment_actions")

