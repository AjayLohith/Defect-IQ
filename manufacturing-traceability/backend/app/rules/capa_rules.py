from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status

from backend.app.models.capa import CorrectiveAction, CAPAVerification
from backend.app.models.event import StateEvent


class CAPAVerificationRequiredException(HTTPException):
    def __init__(self, capa_id: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "ERR_CAPA_VERIFICATION_REQUIRED",
                "message": f"CAPA '{capa_id}' cannot be closed without at least one PASSED verification.",
                "capa_id": capa_id,
            },
        )


def verify_capa_closure_eligibility(db: Session, capa_id: str) -> CorrectiveAction:
    """
    Strict business rule enforcement:
    A CAPA cannot be closed unless it has at least one verification with result = 'PASSED'.
    """
    capa = db.execute(
        select(CorrectiveAction).where(CorrectiveAction.corrective_action_id == capa_id)
    ).scalar_one_or_none()

    if not capa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corrective action '{capa_id}' not found.",
        )

    if capa.corrective_action_status == "CLOSED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Corrective action '{capa_id}' is already CLOSED.",
        )

    # Check for passed verifications
    passed_count = db.execute(
        select(func.count(CAPAVerification.verification_id)).where(
            CAPAVerification.corrective_action_id == capa_id,
            CAPAVerification.verification_result == "PASSED",
        )
    ).scalar() or 0

    if passed_count == 0:
        raise CAPAVerificationRequiredException(capa_id=capa_id)

    return capa


def close_capa_with_event(
    db: Session,
    capa_id: str,
    actor_role: str = "QUALITY_ENGINEER",
    reason_code: str = "RC_FORMAL_CLOSURE",
    closure_notes: Optional[str] = None,
) -> CorrectiveAction:
    """
    Executes controlled CAPA closure:
    1. Validates eligibility (passing verification required).
    2. Updates status to CLOSED.
    3. Appends an immutable StateEvent record with incremented event_sequence.
    """
    capa = verify_capa_closure_eligibility(db, capa_id)
    previous_state = capa.corrective_action_status

    # Get latest event_sequence for this CAPA
    max_seq = db.execute(
        select(func.coalesce(func.max(StateEvent.event_sequence), 0)).where(
            StateEvent.entity_type == "CORRECTIVE_ACTION",
            StateEvent.corrective_action_id == capa_id,
        )
    ).scalar() or 0

    next_seq = max_seq + 1

    # Generate event ID
    total_events = db.execute(select(func.count(StateEvent.event_id))).scalar() or 0
    event_id = f"EVT-{total_events + 1:08d}"

    event_time = datetime.now(timezone.utc)

    # Append StateEvent
    event = StateEvent(
        event_id=event_id,
        entity_type="CORRECTIVE_ACTION",
        entity_id=capa_id,
        corrective_action_id=capa_id,
        material_lot_id=None,
        production_order_id=None,
        inspection_result_id=None,
        defect_id=None,
        event_sequence=next_seq,
        previous_state=previous_state,
        new_state="CLOSED",
        event_timestamp=event_time,
        actor_role=actor_role,
        reason_code=reason_code,
        event_notes=closure_notes or f"CAPA verified and formally closed by {actor_role}",
    )

    capa.corrective_action_status = "CLOSED"

    db.add(event)
    db.commit()
    db.refresh(capa)
    return capa

