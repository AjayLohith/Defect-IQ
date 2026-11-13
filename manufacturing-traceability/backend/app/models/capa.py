from datetime import date
from typing import Optional
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    corrective_action_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    defect_id: Mapped[str] = mapped_column(String(32), ForeignKey("defects.defect_id"), nullable=False)
    root_cause_category: Mapped[str] = mapped_column(String(32), nullable=False)
    root_cause_description: Mapped[str] = mapped_column(Text, nullable=False)
    owner_role: Mapped[str] = mapped_column(String(32), default="QUALITY_ENGINEER", nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    implementation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    corrective_action_status: Mapped[str] = mapped_column(String(32), default="OPEN", nullable=False)
    effectiveness_target: Mapped[str] = mapped_column(String(255), nullable=False)

    defect = relationship("Defect", back_populates="corrective_actions")
    verifications = relationship("CAPAVerification", back_populates="corrective_action")


class CAPAVerification(Base):
    __tablename__ = "capa_verifications"

    verification_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    corrective_action_id: Mapped[str] = mapped_column(String(32), ForeignKey("corrective_actions.corrective_action_id"), nullable=False)
    verification_date: Mapped[date] = mapped_column(Date, nullable=False)
    verification_method: Mapped[str] = mapped_column(String(32), default="AUDIT_CHECK", nullable=False)
    verification_result: Mapped[str] = mapped_column(String(16), default="PASSED", nullable=False)
    verified_by_role: Mapped[str] = mapped_column(String(32), default="QUALITY_ENGINEER", nullable=False)
    evidence_reference: Mapped[str] = mapped_column(String(255), nullable=False)

    corrective_action = relationship("CorrectiveAction", back_populates="verifications")

