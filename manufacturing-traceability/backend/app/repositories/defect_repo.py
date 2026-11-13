from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.app.models.defect import Defect, ContainmentAction
from backend.app.models.order import ProductionOrder
from backend.app.models.product import Product
from backend.app.models.machine import Machine
from backend.app.models.supplier import Supplier
from backend.app.models.capa import CorrectiveAction
from backend.app.schemas.defect import DefectDetail


class DefectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, defect_id: str) -> Optional[Defect]:
        return self.db.execute(
            select(Defect).where(Defect.defect_id == defect_id)
        ).scalar_one_or_none()

    def get_detail_by_id(self, defect_id: str) -> Optional[DefectDetail]:
        defect = self.get_by_id(defect_id)
        if not defect:
            return None

        # Resolve related names
        po = self.db.execute(
            select(ProductionOrder).where(ProductionOrder.production_order_id == defect.production_order_id)
        ).scalar_one_or_none()
        prod_name = None
        prod_id = None
        if po:
            prod_id = po.product_id
            prod = self.db.execute(select(Product).where(Product.product_id == po.product_id)).scalar_one_or_none()
            if prod:
                prod_name = prod.product_name

        mch = self.db.execute(select(Machine).where(Machine.machine_id == defect.machine_id)).scalar_one_or_none()
        machine_name = mch.machine_name if mch else None

        supp_name = None
        if defect.supplier_id:
            supp = self.db.execute(select(Supplier).where(Supplier.supplier_id == defect.supplier_id)).scalar_one_or_none()
            supp_name = supp.supplier_name if supp else None

        # Counts
        cnt_count = len(defect.containment_actions) if defect.containment_actions else 0
        capa_count = len(defect.corrective_actions) if defect.corrective_actions else 0

        return DefectDetail(
            defect_id=defect.defect_id,
            inspection_result_id=defect.inspection_result_id,
            production_order_id=defect.production_order_id,
            process_execution_id=defect.process_execution_id,
            machine_id=defect.machine_id,
            material_lot_id=defect.material_lot_id,
            reported_material_lot_id=defect.reported_material_lot_id,
            supplier_id=defect.supplier_id,
            defect_code=defect.defect_code,
            defect_category=defect.defect_category,
            severity=defect.severity,
            defect_quantity=float(defect.defect_quantity),
            suspected_source=defect.suspected_source,
            detected_at=defect.detected_at,
            defect_status=defect.defect_status,
            product_id=prod_id,
            product_name=prod_name,
            machine_name=machine_name,
            supplier_name=supp_name,
            containment_actions_count=cnt_count,
            corrective_actions_count=capa_count,
        )

    def list_defects(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        machine_id: Optional[str] = None,
        order_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Defect]:
        stmt = select(Defect)
        if status:
            stmt = stmt.where(Defect.defect_status == status)
        if severity:
            stmt = stmt.where(Defect.severity == severity)
        if category:
            stmt = stmt.where(Defect.defect_category == category)
        if machine_id:
            stmt = stmt.where(Defect.machine_id == machine_id)
        if order_id:
            stmt = stmt.where(Defect.production_order_id == order_id)

        stmt = stmt.order_by(desc(Defect.detected_at)).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
