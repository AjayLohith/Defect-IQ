from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CAPAVerificationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    verification_id: str
    corrective_action_id: str
    verification_date: date
    verification_method: str
    verification_result: str
    verified_by_role: str
    evidence_reference: str


class CAPAVerificationCreate(BaseModel):
    verification_date: date
    verification_method: str = "AUDIT_CHECK"
    verification_result: str = "PASSED"
    verified_by_role: str = "QUALITY_ENGINEER"
    evidence_reference: str
    notes: Optional[str] = None


class CorrectiveActionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    corrective_action_id: str
    defect_id: str
    root_cause_category: str
    root_cause_description: str
    owner_role: str
    due_date: date
    implementation_date: Optional[date] = None
    corrective_action_status: str
    effectiveness_target: str


class CorrectiveActionDetail(CorrectiveActionBase):
    verifications: List[CAPAVerificationBase] = []
    has_passed_verification: bool = False
    ready_for_closure: bool = False


class CorrectiveActionCreate(BaseModel):
    defect_id: str
    root_cause_category: str
    root_cause_description: str
    owner_role: str = "QUALITY_ENGINEER"
    due_date: date
    effectiveness_target: str
    actor_role: str = "QUALITY_ENGINEER"
    reason_code: str = "RC_CAPA_INITIATED"


class CAPACloseRequest(BaseModel):
    actor_role: str = "QUALITY_ENGINEER"
    closure_notes: Optional[str] = None
    reason_code: str = "RC_FORMAL_CLOSURE"

