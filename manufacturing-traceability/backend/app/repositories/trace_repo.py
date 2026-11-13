from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.models.defect import Defect, ContainmentAction
from backend.app.models.inspection import InspectionResult
from backend.app.models.order import ProductionOrder, MaterialConsumption
from backend.app.models.process import ProcessExecution, ProcessStep
from backend.app.models.machine import Machine
from backend.app.models.lot import MaterialLot
from backend.app.models.supplier import Supplier
from backend.app.models.product import Product
from backend.app.schemas.traceability import (
    UpstreamTraceResult,
    ConsumedLotTraceItem,
    DownstreamImpactResult,
    DownstreamImpactOrderItem,
)


class TraceRepository:
    def __init__(self, db: Session):
        self.db = db

    def upstream_trace(self, defect_id: str) -> Optional[UpstreamTraceResult]:
        defect = self.db.execute(
            select(Defect).where(Defect.defect_id == defect_id)
        ).scalar_one_or_none()

        if not defect:
            return None

        insp = self.db.execute(
            select(InspectionResult).where(InspectionResult.inspection_result_id == defect.inspection_result_id)
        ).scalar_one_or_none()

        po = self.db.execute(
            select(ProductionOrder).where(ProductionOrder.production_order_id == defect.production_order_id)
        ).scalar_one_or_none()

        prod = self.db.execute(
            select(Product).where(Product.product_id == po.product_id)
        ).scalar_one_or_none() if po else None

        pe = self.db.execute(
            select(ProcessExecution).where(ProcessExecution.process_execution_id == defect.process_execution_id)
        ).scalar_one_or_none()

        step = self.db.execute(
            select(ProcessStep).where(ProcessStep.process_step_id == pe.process_step_id)
        ).scalar_one_or_none() if pe else None

        mch = self.db.execute(
            select(Machine).where(Machine.machine_id == defect.machine_id)
        ).scalar_one_or_none()

        # Find consumed lots in this production order
        consumptions = self.db.execute(
            select(MaterialConsumption).where(
                MaterialConsumption.production_order_id == defect.production_order_id,
                MaterialConsumption.consumption_status == "COMMITTED",
            ).order_by(MaterialConsumption.consumed_at.asc())
        ).scalars().all()

        consumed_lots: List[ConsumedLotTraceItem] = []
        for c in consumptions:
            lot = self.db.execute(
                select(MaterialLot).where(MaterialLot.material_lot_id == c.material_lot_id)
            ).scalar_one_or_none()

            if lot:
                supp = self.db.execute(
                    select(Supplier).where(Supplier.supplier_id == lot.supplier_id)
                ).scalar_one_or_none()
                mat_p = self.db.execute(
                    select(Product).where(Product.product_id == lot.material_product_id)
                ).scalar_one_or_none()

                consumed_lots.append(
                    ConsumedLotTraceItem(
                        consumption_id=c.consumption_id,
                        material_lot_id=lot.material_lot_id,
                        material_product_id=lot.material_product_id,
                        material_product_name=mat_p.product_name if mat_p else lot.material_product_id,
                        supplier_id=lot.supplier_id,
                        supplier_name=supp.supplier_name if supp else lot.supplier_id,
                        supplier_batch_code=lot.supplier_batch_code,
                        consumed_quantity=float(c.consumed_quantity),
                        uom=c.uom,
                        consumed_at=c.consumed_at,
                        lot_status=lot.lot_status,
                    )
                )

        return UpstreamTraceResult(
            defect_id=defect.defect_id,
            defect_code=defect.defect_code,
            defect_category=defect.defect_category,
            severity=defect.severity,
            defect_status=defect.defect_status,
            defect_quantity=float(defect.defect_quantity),
            suspected_source=defect.suspected_source,
            detected_at=defect.detected_at,
            inspection_result_id=defect.inspection_result_id,
            disposition=insp.disposition if insp else "UNKNOWN",
            production_order_id=defect.production_order_id,
            product_id=po.product_id if po else "UNKNOWN",
            product_name=prod.product_name if prod else "Unknown Product",
            process_execution_id=defect.process_execution_id,
            step_name=step.step_name if step else "Unknown Step",
            machine_id=defect.machine_id,
            machine_name=mch.machine_name if mch else defect.machine_id,
            consumed_lots=consumed_lots,
        )

    def downstream_lot_impact(self, lot_id: str) -> Optional[DownstreamImpactResult]:
        lot = self.db.execute(
            select(MaterialLot).where(MaterialLot.material_lot_id == lot_id)
        ).scalar_one_or_none()

        if not lot:
            return None

        supp = self.db.execute(
            select(Supplier).where(Supplier.supplier_id == lot.supplier_id)
        ).scalar_one_or_none()

        mat_p = self.db.execute(
            select(Product).where(Product.product_id == lot.material_product_id)
        ).scalar_one_or_none()

        # Find all consumptions of this lot
        consumptions = self.db.execute(
            select(MaterialConsumption).where(
                MaterialConsumption.material_lot_id == lot_id
            ).order_by(MaterialConsumption.consumed_at.asc())
        ).scalars().all()

        impacted_orders: List[DownstreamImpactOrderItem] = []
        total_defects_linked = 0

        for c in consumptions:
            po = self.db.execute(
                select(ProductionOrder).where(ProductionOrder.production_order_id == c.production_order_id)
            ).scalar_one_or_none()
            if not po:
                continue

            prod = self.db.execute(
                select(Product).where(Product.product_id == po.product_id)
            ).scalar_one_or_none()

            # Defects on this order
            order_defects = self.db.execute(
                select(Defect).where(Defect.production_order_id == po.production_order_id)
            ).scalars().all()

            # Active containments
            active_cnt = 0
            for d in order_defects:
                for ca in d.containment_actions:
                    if ca.containment_status == "ACTIVE":
                        active_cnt += 1

            total_defects_linked += len(order_defects)

            impacted_orders.append(
                DownstreamImpactOrderItem(
                    production_order_id=po.production_order_id,
                    product_id=po.product_id,
                    product_name=prod.product_name if prod else po.product_id,
                    order_status=po.order_status,
                    consumed_quantity=float(c.consumed_quantity),
                    consumption_uom=c.uom,
                    consumed_at=c.consumed_at,
                    defects_count=len(order_defects),
                    active_containments_count=active_cnt,
                )
            )

        return DownstreamImpactResult(
            material_lot_id=lot.material_lot_id,
            supplier_id=lot.supplier_id,
            supplier_name=supp.supplier_name if supp else lot.supplier_id,
            supplier_batch_code=lot.supplier_batch_code,
            material_product_id=lot.material_product_id,
            material_product_name=mat_p.product_name if mat_p else lot.material_product_id,
            lot_status=lot.lot_status,
            received_quantity=float(lot.received_quantity),
            available_quantity=float(lot.available_quantity),
            consumed_quantity=float(lot.consumed_quantity),
            uom=lot.uom,
            impacted_orders=impacted_orders,
            total_impacted_orders=len(impacted_orders),
            total_defects_linked=total_defects_linked,
        )
