from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.repositories.capa_repo import CAPARepository
from backend.app.rules.capa_rules import close_capa_with_event
from backend.app.schemas.capa import (
    CorrectiveActionDetail,
    CorrectiveActionCreate,
    CAPAVerificationCreate,
    CAPAVerificationBase,
    CAPACloseRequest,
)

router = APIRouter(prefix="/capas", tags=["Corrective Actions (CAPA)"])


@router.get("", response_model=List[CorrectiveActionDetail])
def list_capas(
    status: Optional[str] = Query(None, description="Filter by CAPA status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List corrective actions with verification status and readiness indicators."""
    repo = CAPARepository(db)
    return repo.list_capas(status=status, limit=limit, offset=offset)


@router.get("/{capa_id}", response_model=CorrectiveActionDetail)
def get_capa(capa_id: str, db: Session = Depends(get_db)):
    """Get single CAPA details, including all verifications."""
    repo = CAPARepository(db)
    detail = repo.get_detail_by_id(capa_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corrective action '{capa_id}' not found.",
        )
    return detail


@router.post("", response_model=CorrectiveActionDetail, status_code=status.HTTP_201_CREATED)
def create_capa(data: CorrectiveActionCreate, db: Session = Depends(get_db)):
    """Create a new CAPA with StateEvent."""
    repo = CAPARepository(db)
    capa = repo.create_capa(data)
    return repo.get_detail_by_id(capa.corrective_action_id)


@router.post("/{capa_id}/verifications", response_model=CAPAVerificationBase, status_code=status.HTTP_201_CREATED)
def add_verification(capa_id: str, data: CAPAVerificationCreate, db: Session = Depends(get_db)):
    """
    Record an effectiveness verification for a CAPA.
    If result is PASSED, advances CAPA to VERIFIED state with StateEvent.
    """
    repo = CAPARepository(db)
    capa = repo.get_by_id(capa_id)
    if not capa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Corrective action '{capa_id}' not found.",
        )
    return repo.add_verification(capa_id, data)


@router.post("/{capa_id}/close", response_model=CorrectiveActionDetail)
def close_capa(capa_id: str, request: CAPACloseRequest, db: Session = Depends(get_db)):
    """
    Close a Corrective Action.
    STRICT BUSINESS RULE:
    Requires at least one PASSED verification. If none exists, fails with HTTP 422 ERR_CAPA_VERIFICATION_REQUIRED.
    Upon successful closure, appends an immutable StateEvent record.
    """
    close_capa_with_event(
        db=db,
        capa_id=capa_id,
        actor_role=request.actor_role,
        reason_code=request.reason_code,
        closure_notes=request.closure_notes,
    )
    repo = CAPARepository(db)
    return repo.get_detail_by_id(capa_id)

