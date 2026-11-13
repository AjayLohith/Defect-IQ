from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.app.database.session import get_db
from backend.app.models.lot import MaterialLot
from backend.app.models.supplier import Supplier
from backend.app.models.product import Product
from backend.app.schemas.lot import MaterialLotBase, MaterialLotDetail

router = APIRouter(prefix="/lots", tags=["Material Lots"])


@router.get("", response_model=List[MaterialLotBase])
def list_lots(
    status: Optional[str] = Query(None, description="Filter by lot status"),
    supplier_id: Optional[str] = Query(None, description="Filter by supplier ID"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List material lots with status/supplier filters."""
    stmt = select(MaterialLot)
    if status:
        stmt = stmt.where(MaterialLot.lot_status == status)
    if supplier_id:
        stmt = stmt.where(MaterialLot.supplier_id == supplier_id)
    stmt = stmt.order_by(desc(MaterialLot.received_date)).offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


@router.get("/{lot_id}", response_model=MaterialLotDetail)
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    """Get single material lot details with supplier and product names."""
    lot = db.execute(select(MaterialLot).where(MaterialLot.material_lot_id == lot_id)).scalar_one_or_none()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material lot '{lot_id}' not found.",
        )

    supp = db.execute(select(Supplier).where(Supplier.supplier_id == lot.supplier_id)).scalar_one_or_none()
    prod = db.execute(select(Product).where(Product.product_id == lot.material_product_id)).scalar_one_or_none()

    return MaterialLotDetail(
        material_lot_id=lot.material_lot_id,
        supplier_id=lot.supplier_id,
        material_product_id=lot.material_product_id,
        supplier_batch_code=lot.supplier_batch_code,
        received_date=lot.received_date,
        expiry_date=lot.expiry_date,
        received_quantity=float(lot.received_quantity),
        available_quantity=float(lot.available_quantity),
        consumed_quantity=float(lot.consumed_quantity),
        rejected_quantity=float(lot.rejected_quantity),
        quarantined_quantity=float(lot.quarantined_quantity),
        uom=lot.uom,
        lot_status=lot.lot_status,
        incoming_quality_score=float(lot.incoming_quality_score),
        supplier_name=supp.supplier_name if supp else lot.supplier_id,
        material_product_name=prod.product_name if prod else lot.material_product_id,
    )

