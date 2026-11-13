from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from backend.app.database.session import get_db
from backend.app.models.defect import Defect, ContainmentAction
from backend.app.models.event import StateEvent
from backend.app.schemas.containment import ContainmentActionBase, ContainmentActionCreate

router = APIRouter(prefix="/containment", tags=["Containment"])


@router.get("", response_model=List[ContainmentActionBase])
def list_containment_actions(
    status: Optional[str] = Query(None, description="Filter by containment status"),
    defect_id: Optional[str] = Query(None, description="Filter by defect ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List containment actions with optional status and defect filters."""
    stmt = select(ContainmentAction)
    if status:
        stmt = stmt.where(ContainmentAction.containment_status == status)
    if defect_id:
        stmt = stmt.where(ContainmentAction.defect_id == defect_id)
    stmt = stmt.order_by(desc(ContainmentAction.action_timestamp)).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=ContainmentActionBase, status_code=status.HTTP_201_CREATED)
def create_containment_action(data: ContainmentActionCreate, db: Session = Depends(get_db)):
    """Create a containment action and record StateEvent."""
    defect = db.execute(select(Defect).where(Defect.defect_id == data.defect_id)).scalar_one_or_none()
    if not defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect '{data.defect_id}' not found.",
        )

    total = db.execute(select(func.count(ContainmentAction.containment_action_id))).scalar() or 0
    cnt_id = f"CNT-2026-{total + 1:06d}"

    action = ContainmentAction(
        containment_action_id=cnt_id,
        defect_id=data.defect_id,
        action_type=data.action_type,
        owner_role=data.owner_role,
        action_timestamp=datetime.now(timezone.utc),
        affected_quantity=data.affected_quantity,
        containment_status="ACTIVE",
        notes=data.notes,
    )
    db.add(action)

    # If defect is OPEN, update to CONTAINED
    if defect.defect_status == "OPEN":
        prev_defect_status = defect.defect_status
        defect.defect_status = "CONTAINED"

        max_seq = db.execute(
            select(func.coalesce(func.max(StateEvent.event_sequence), 0)).where(
                StateEvent.entity_type == "DEFECT",
                StateEvent.defect_id == data.defect_id,
            )
        ).scalar() or 0

        evt_total = db.execute(select(func.count(StateEvent.event_id))).scalar() or 0
        evt = StateEvent(
            event_id=f"EVT-{evt_total + 1:08d}",
            entity_type="DEFECT",
            entity_id=data.defect_id,
            defect_id=data.defect_id,
            event_sequence=max_seq + 1,
            previous_state=prev_defect_status,
            new_state="CONTAINED",
            event_timestamp=datetime.now(timezone.utc),
            actor_role=data.owner_role,
            reason_code=data.reason_code,
            event_notes=f"Containment action {data.action_type} activated: {data.notes or ''}",
        )
        db.add(evt)

    db.commit()
    db.refresh(action)
    return action
