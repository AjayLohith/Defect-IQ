from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MachineBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    machine_id: str
    machine_name: str
    machine_type: str
    work_center: str
    machine_status: str
    calibration_due_date: date
    maintenance_risk_score: float


class ProcessStepBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    process_step_id: str
    step_sequence: int
    step_name: str
    step_type: str
    work_center: str
    standard_cycle_time_seconds: int
    allowed_machine_type: str

