from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class Machine(Base):
    __tablename__ = "machines"

    machine_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    machine_name: Mapped[str] = mapped_column(String(255), nullable=False)
    machine_type: Mapped[str] = mapped_column(String(32), nullable=False)
    line_code: Mapped[str] = mapped_column(String(32), default="LINE-A", nullable=False)
    machine_status: Mapped[str] = mapped_column(String(32), default="OPERATIONAL", nullable=False)
    calibration_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    maintenance_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("10.0"), nullable=False)

    process_executions = relationship("ProcessExecution", back_populates="machine")
    defects = relationship("Defect", back_populates="machine")

