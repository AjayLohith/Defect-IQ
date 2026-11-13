from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ContainmentActionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    containment_action_id: str
    defect_id: str
    action_type: str
    owner_role: str
    action_timestamp: datetime
    affected_quantity: float
    containment_status: str
    notes: Optional[str] = None


class ContainmentActionCreate(BaseModel):
    defect_id: str
    action_type: str = "QUARANTINE_LOT"
    owner_role: str = "QUALITY_ENGINEER"
    affected_quantity: float = 1.0
    notes: Optional[str] = None
    reason_code: str = "RC_IMMEDIATE_QUARANTINE"

