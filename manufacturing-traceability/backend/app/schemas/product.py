from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class BOMLineBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bom_line_id: str
    bom_id: str
    material_product_id: str
    quantity_per_unit: float
    uom: str
    scrap_factor: float
    effective_start_date: date
    effective_end_date: Optional[date] = None


class BOMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bom_id: str
    product_id: str
    revision: str
    status: str
    effective_start_date: date
    effective_end_date: Optional[date] = None
    lines: List[BOMLineBase] = []


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_name: str
    product_type: str
    base_uom: str
    lifecycle_state: str
    target_defect_rate_ppm: float
    effective_start_date: date
    effective_end_date: Optional[date] = None

