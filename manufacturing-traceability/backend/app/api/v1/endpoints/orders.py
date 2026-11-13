from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.repositories.order_repo import OrderRepository
from backend.app.schemas.order import ProductionOrderBase, BOMReconciliationReport

router = APIRouter(prefix="/orders", tags=["Production Orders"])


@router.get("", response_model=List[ProductionOrderBase])
def list_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List production orders with optional filtering."""
    repo = OrderRepository(db)
    return repo.list_orders(status=status, product_id=product_id, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=ProductionOrderBase)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get single production order details."""
    repo = OrderRepository(db)
    order = repo.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production order '{order_id}' not found.",
        )
    return order


@router.get("/{order_id}/bom-reconciliation", response_model=BOMReconciliationReport)
def get_order_bom_reconciliation(order_id: str, db: Session = Depends(get_db)):
    """
    BOM Reconciliation Report for Production Order:
    Compares expected required BOM quantities against committed consumed quantities.
    Flags MISSING_CONSUMPTION, RECONCILED, or VARIANCE_DETECTED per BOM line.
    """
    repo = OrderRepository(db)
    report = repo.get_bom_reconciliation(order_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production order '{order_id}' not found.",
        )
    return report

