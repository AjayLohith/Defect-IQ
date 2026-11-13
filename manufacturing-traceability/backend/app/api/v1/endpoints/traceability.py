from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.repositories.trace_repo import TraceRepository
from backend.app.schemas.traceability import UpstreamTraceResult, DownstreamImpactResult

router = APIRouter(prefix="/traceability", tags=["Traceability"])


@router.get("/upstream/{defect_id}", response_model=UpstreamTraceResult)
def get_upstream_trace(defect_id: str, db: Session = Depends(get_db)):
    """
    Upstream Defect-to-Supplier Trace:
    Given a defect_id, traces backwards through inspection result, production order,
    process execution, machine, consumed material lots, and upstream supplier.
    """
    repo = TraceRepository(db)
    result = repo.upstream_trace(defect_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Defect '{defect_id}' not found.",
        )
    return result


@router.get("/downstream/{lot_id}", response_model=DownstreamImpactResult)
def get_downstream_impact(lot_id: str, db: Session = Depends(get_db)):
    """
    Downstream Blast-Radius Impact:
    Given a material_lot_id, identifies all production orders where this lot was consumed,
    affected products, and resulting defects and active containment actions.
    """
    repo = TraceRepository(db)
    result = repo.downstream_lot_impact(lot_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material lot '{lot_id}' not found.",
        )
    return result

