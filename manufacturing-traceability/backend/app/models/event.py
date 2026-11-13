from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates
from backend.app.models.base import Base


class StateEvent(Base):
    __tablename__ = "state_events"

    event_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    material_lot_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("material_lots.material_lot_id"), nullable=True)
    production_order_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("production_orders.production_order_id"), nullable=True)
    inspection_result_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("inspection_results.inspection_result_id"), nullable=True)
    defect_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("defects.defect_id"), nullable=True)
    corrective_action_id: Mapped[Optional[str]] = mapped_column(String(32), ForeignKey("corrective_actions.corrective_action_id"), nullable=True)
    event_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_state: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    new_state: Mapped[str] = mapped_column(String(32), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(32), default="SYSTEM", nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), default="NORMAL_FLOW", nullable=False)
    event_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(entity_type = 'MATERIAL_LOT' AND material_lot_id = entity_id AND production_order_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR "
            "(entity_type = 'PRODUCTION_ORDER' AND production_order_id = entity_id AND material_lot_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR "
            "(entity_type = 'INSPECTION_RESULT' AND inspection_result_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR "
            "(entity_type = 'DEFECT' AND defect_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND inspection_result_id IS NULL AND corrective_action_id IS NULL) OR "
            "(entity_type = 'CORRECTIVE_ACTION' AND corrective_action_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL)",
            name="chk_state_events_exact_one_fk"
        ),
        UniqueConstraint("entity_type", "entity_id", "event_sequence", name="uq_state_events_entity_sequence")
    )

    def validate_integrity(self):
        """Enforces that exactly one typed FK is populated and strictly matches entity_type and entity_id."""
        fk_map = {
            "MATERIAL_LOT": self.material_lot_id,
            "PRODUCTION_ORDER": self.production_order_id,
            "INSPECTION_RESULT": self.inspection_result_id,
            "DEFECT": self.defect_id,
            "CORRECTIVE_ACTION": self.corrective_action_id,
        }
        if self.entity_type not in fk_map:
            raise ValueError(f"Invalid entity_type '{self.entity_type}'")

        expected_fk_val = fk_map[self.entity_type]
        if expected_fk_val is None or expected_fk_val != self.entity_id:
            raise ValueError(
                f"Integrity error for entity_type '{self.entity_type}': "
                f"corresponding foreign key must be populated and equal entity_id '{self.entity_id}' (got '{expected_fk_val}')"
            )

        for other_type, other_val in fk_map.items():
            if other_type != self.entity_type and other_val is not None:
                raise ValueError(
                    f"Integrity error: foreign key for '{other_type}' must be NULL when entity_type is '{self.entity_type}' (got '{other_val}')"
                )
