from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MaterialLotBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_lot_id: str
    supplier_id: str
    material_product_id: str
    supplier_batch_code: str
    received_date: date
    expiry_date: date
    received_quantity: float
    available_quantity: float
    consumed_quantity: float
    rejected_quantity: float
    quarantined_quantity: float
    uom: str
    lot_status: str
    incoming_quality_score: float


class MaterialLotDetail(MaterialLotBase):
    supplier_name: Optional[str] = None
    material_product_name: Optional[str] = None

