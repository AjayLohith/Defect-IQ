from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator


class StateEventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    entity_type: str
    entity_id: str
    material_lot_id: Optional[str] = None
    production_order_id: Optional[str] = None
    inspection_result_id: Optional[str] = None
    defect_id: Optional[str] = None
    corrective_action_id: Optional[str] = None
    event_sequence: int
    previous_state: Optional[str] = None
    new_state: str
    event_timestamp: datetime
    actor_role: str = "SYSTEM"
    reason_code: str = "NORMAL_FLOW"
    event_notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_exact_matching_fk(self) -> "StateEventBase":
        fk_map = {
            "MATERIAL_LOT": self.material_lot_id,
            "PRODUCTION_ORDER": self.production_order_id,
            "INSPECTION_RESULT": self.inspection_result_id,
            "DEFECT": self.defect_id,
            "CORRECTIVE_ACTION": self.corrective_action_id,
        }

        if self.entity_type not in fk_map:
            raise ValueError(f"Invalid entity_type '{self.entity_type}'")

        expected_val = fk_map[self.entity_type]
        if expected_val is None or expected_val != self.entity_id:
            raise ValueError(
                f"For entity_type '{self.entity_type}', corresponding FK must equal entity_id '{self.entity_id}' (got '{expected_val}')"
            )

        for other_type, other_val in fk_map.items():
            if other_type != self.entity_type and other_val is not None:
                raise ValueError(
                    f"Foreign key for '{other_type}' must be None when entity_type is '{self.entity_type}' (got '{other_val}')"
                )

        return self


class StateEventCreate(StateEventBase):
    pass


class StateEventRead(StateEventBase):
    pass

