from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SupplierBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: str
    supplier_name: str
    supplier_status: str
    supplier_risk_tier: str
    quality_rating_score: float
    lead_time_days: int
    effective_start_date: date
    effective_end_date: Optional[date] = None

