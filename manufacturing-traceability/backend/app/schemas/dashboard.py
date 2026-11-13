from typing import List, Dict
from pydantic import BaseModel


class MachineDriftMetric(BaseModel):
    machine_id: str
    machine_name: str
    machine_type: str
    machine_status: str
    maintenance_risk_score: float
    total_process_executions: int
    total_defects: int
    defect_rate: float


class QualityMetrics(BaseModel):
    total_production_orders: int
    completed_production_orders: int
    total_inspections: int
    total_defects: int
    open_defects: int
    critical_defects: int
    active_containments: int
    open_capas: int
    pending_verifications: int
    overall_defect_rate: float
    defects_by_severity: Dict[str, int]
    defects_by_category: Dict[str, int]
    top_risk_machines: List[MachineDriftMetric]

