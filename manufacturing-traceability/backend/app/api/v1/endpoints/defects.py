from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from backend.app.database.session import get_db
from backend.app.repositories.defect_repo import DefectRepository
from backend.app.models.defect import Defect
from backend.app.models.event import StateEvent
from backend.app.schemas.defect import DefectBase, DefectDetail, DefectCreate

router = APIRouter(prefix="/defects", tags=["Defects"])


@router.get("", response_model=List[DefectBase])
def list_defects(
    status: Optional[str] = Query(None, description="Filter by defect status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    machine_id: Optional[str] = Query(None, description="Filter by machine ID"),
    order_id: Optional[str] = Query(None, description="Filter by production order ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List operational defects with optional filters."""
    repo = DefectRepository(db)
    return repo.list_defects(
        status=status,
        severity=severity,
        category=category,
        machine_id=machine_id,
        order_id=order_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{defect_id}", response_model=DefectDetail)
def get_defect(defect_id: str, db: Session = Depends(get_db)):
    """Get single defect details with resolved relationships."""
    repo = DefectRepository(db)
    detail = repo.get_detail_by_id(defect_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect '{defect_id}' not found.",
        )
    return detail


@router.post("", response_model=DefectBase, status_code=status.HTTP_201_CREATED)
def create_defect(data: DefectCreate, db: Session = Depends(get_db)):
    """Log a new defect and record its initial append-only StateEvent."""
    total = db.execute(select(func.count(Defect.defect_id))).scalar() or 0
    defect_id = f"DEF-2026-{total + 1:06d}"

    defect = Defect(
        defect_id=defect_id,
        inspection_result_id=data.inspection_result_id,
        production_order_id=data.production_order_id,
        process_execution_id=data.process_execution_id,
        machine_id=data.machine_id,
        material_lot_id=data.material_lot_id,
        reported_material_lot_id=data.reported_material_lot_id,
        supplier_id=data.supplier_id,
        defect_code=data.defect_code,
        defect_category=data.defect_category,
        severity=data.severity,
        defect_quantity=data.defect_quantity,
        suspected_source=data.suspected_source,
        detected_at=datetime.now(timezone.utc),
        defect_status="OPEN",
    )
    db.add(defect)

    # Append StateEvent
    event_cnt = db.execute(select(func.count(StateEvent.event_id))).scalar() or 0
    evt = StateEvent(
        event_id=f"EVT-{event_cnt + 1:08d}",
        entity_type="DEFECT",
        entity_id=defect_id,
        defect_id=defect_id,
        event_sequence=1,
        previous_state=None,
        new_state="OPEN",
        event_timestamp=datetime.now(timezone.utc),
        actor_role=data.actor_role,
        reason_code=data.reason_code,
        event_notes=data.event_notes or f"Defect logged: {data.defect_code}",
    )
    db.add(evt)
    db.commit()
    db.refresh(defect)
    return defect

