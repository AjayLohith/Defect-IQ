from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


class ConsumedLotTraceItem(BaseModel):
    consumption_id: str
    material_lot_id: str
    material_product_id: str
    material_product_name: str
    supplier_id: str
    supplier_name: str
    supplier_batch_code: str
    consumed_quantity: float
    uom: str
    consumed_at: datetime
    lot_status: str


class UpstreamTraceResult(BaseModel):
    defect_id: str
    defect_code: str
    defect_category: str
    severity: str
    defect_status: str
    defect_quantity: float
    suspected_source: str
    detected_at: datetime
    inspection_result_id: str
    disposition: str
    production_order_id: str
    product_id: str
    product_name: str
    process_execution_id: str
    step_name: Optional[str] = None
    machine_id: str
    machine_name: str
    consumed_lots: List[ConsumedLotTraceItem] = []


class DownstreamImpactOrderItem(BaseModel):
    production_order_id: str
    product_id: str
    product_name: str
    order_status: str
    consumed_quantity: float
    consumption_uom: str
    consumed_at: datetime
    defects_count: int = 0
    active_containments_count: int = 0


class DownstreamImpactResult(BaseModel):
    material_lot_id: str
    supplier_id: str
    supplier_name: str
    supplier_batch_code: str
    material_product_id: str
    material_product_name: str
    lot_status: str
    received_quantity: float
    available_quantity: float
    consumed_quantity: float
    uom: str
    impacted_orders: List[DownstreamImpactOrderItem] = []
    total_impacted_orders: int = 0
    total_defects_linked: int = 0

