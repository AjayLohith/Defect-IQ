from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MaterialConsumptionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    consumption_id: str
    production_order_id: str
    material_lot_id: str
    bom_line_id: str
    consumed_quantity: float
    uom: str
    consumed_at: datetime
    consumption_status: str


class ProcessExecutionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    process_execution_id: str
    production_order_id: str
    process_step_id: str
    machine_id: str
    operator_id: str
    start_time: datetime
    end_time: datetime
    input_quantity: float
    output_quantity: float
    scrap_quantity: float
    quarantined_quantity: float
    rework_quantity: float
    execution_status: str
    parameter_drift_flag: bool


class ProductionOrderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    production_order_id: str
    product_id: str
    bom_id: str
    planned_quantity: float
    completed_quantity: float
    scrap_quantity: float
    rework_quantity: float
    quarantined_quantity: float
    uom: str
    order_status: str
    planned_start_date: date
    planned_end_date: date
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    production_lot_code: str


class BOMReconciliationItem(BaseModel):
    bom_line_id: str
    material_product_id: str
    material_name: str
    expected_required_quantity: float
    actual_consumed_quantity: float
    quantity_variance: float
    uom: str
    reconciliation_status: str
    consumption_records_count: int


class BOMReconciliationReport(BaseModel):
    production_order_id: str
    product_id: str
    product_name: str
    order_status: str
    planned_quantity: float
    items: List[BOMReconciliationItem]
    is_fully_reconciled: bool

