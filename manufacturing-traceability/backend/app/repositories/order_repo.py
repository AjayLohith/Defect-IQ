from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from backend.app.models.order import ProductionOrder, MaterialConsumption
from backend.app.models.product import Product
from backend.app.models.bom import BOM, BOMLine
from backend.app.schemas.order import (
    BOMReconciliationReport,
    BOMReconciliationItem,
)


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, order_id: str) -> Optional[ProductionOrder]:
        return self.db.execute(
            select(ProductionOrder).where(ProductionOrder.production_order_id == order_id)
        ).scalar_one_or_none()

    def list_orders(
        self,
        status: Optional[str] = None,
        product_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductionOrder]:
        stmt = select(ProductionOrder)
        if status:
            stmt = stmt.where(ProductionOrder.order_status == status)
        if product_id:
            stmt = stmt.where(ProductionOrder.product_id == product_id)
        stmt = stmt.order_by(desc(ProductionOrder.planned_start_date)).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_bom_reconciliation(self, order_id: str) -> Optional[BOMReconciliationReport]:
        order = self.get_by_id(order_id)
        if not order:
            return None

        product = self.db.execute(
            select(Product).where(Product.product_id == order.product_id)
        ).scalar_one_or_none()
        product_name = product.product_name if product else "Unknown Product"

        # Get active BOM lines for this product
        bom = self.db.execute(
            select(BOM).where(BOM.product_id == order.product_id, BOM.status == "ACTIVE")
        ).scalar_one_or_none()

        if not bom:
            # Fall back to order's assigned BOM
            bom = self.db.execute(
                select(BOM).where(BOM.bom_id == order.bom_id)
            ).scalar_one_or_none()

        bom_lines = bom.bom_lines if bom else []

        # Get actual consumptions grouped by bom_line_id
        consumptions = self.db.execute(
            select(
                MaterialConsumption.bom_line_id,
                func.sum(MaterialConsumption.consumed_quantity).label("total_consumed"),
                func.count(MaterialConsumption.consumption_id).label("count_records"),
            )
            .where(
                MaterialConsumption.production_order_id == order_id,
                MaterialConsumption.consumption_status == "COMMITTED",
            )
            .group_by(MaterialConsumption.bom_line_id)
        ).all()

        cons_map = {row[0]: (float(row[1]), int(row[2])) for row in consumptions}

        items: List[BOMReconciliationItem] = []
        is_fully_reconciled = True

        for bl in bom_lines:
            expected_qty = float(
                round(float(order.planned_quantity) * float(bl.quantity_per_unit) * (1.0 + float(bl.scrap_factor)), 4)
            )
            actual_qty, rec_count = cons_map.get(bl.bom_line_id, (0.0, 0))
            variance = float(round(actual_qty - expected_qty, 4))

            # Fetch material product name
            mat_prod = self.db.execute(
                select(Product).where(Product.product_id == bl.material_product_id)
            ).scalar_one_or_none()
            mat_name = mat_prod.product_name if mat_prod else bl.material_product_id

            if rec_count == 0:
                rec_status = "MISSING_CONSUMPTION"
                is_fully_reconciled = False
            elif abs(variance) <= 0.01:
                rec_status = "RECONCILED"
            else:
                rec_status = "VARIANCE_DETECTED"
                is_fully_reconciled = False

            items.append(
                BOMReconciliationItem(
                    bom_line_id=bl.bom_line_id,
                    material_product_id=bl.material_product_id,
                    material_name=mat_name,
                    expected_required_quantity=expected_qty,
                    actual_consumed_quantity=actual_qty,
                    quantity_variance=variance,
                    uom=bl.uom,
                    reconciliation_status=rec_status,
                    consumption_records_count=rec_count,
                )
            )

        return BOMReconciliationReport(
            production_order_id=order.production_order_id,
            product_id=order.product_id,
            product_name=product_name,
            order_status=order.order_status,
            planned_quantity=float(order.planned_quantity),
            items=items,
            is_fully_reconciled=is_fully_reconciled,
        )

