from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DefectBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    defect_id: str
    inspection_result_id: str
    production_order_id: str
    process_execution_id: str
    machine_id: str
    material_lot_id: Optional[str] = None
    reported_material_lot_id: str
    supplier_id: Optional[str] = None
    defect_code: str
    defect_category: str
    severity: str
    defect_quantity: float
    suspected_source: str
    detected_at: datetime
    defect_status: str


class DefectDetail(DefectBase):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    machine_name: Optional[str] = None
    supplier_name: Optional[str] = None
    containment_actions_count: int = 0
    corrective_actions_count: int = 0


class DefectCreate(BaseModel):
    inspection_result_id: str
    production_order_id: str
    process_execution_id: str
    machine_id: str
    material_lot_id: Optional[str] = None
    reported_material_lot_id: str
    supplier_id: Optional[str] = None
    defect_code: str
    defect_category: str
    severity: str = "MINOR"
    defect_quantity: float = 1.0
    suspected_source: str = "MACHINE"
    actor_role: str = "QUALITY_ENGINEER"
    reason_code: str = "RC_DEFECT_DISCOVERED"
    event_notes: Optional[str] = None

