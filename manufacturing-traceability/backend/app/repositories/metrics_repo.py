from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from backend.app.models.order import ProductionOrder
from backend.app.models.inspection import InspectionResult
from backend.app.models.defect import Defect, ContainmentAction
from backend.app.models.capa import CorrectiveAction, CAPAVerification
from backend.app.models.machine import Machine
from backend.app.models.process import ProcessExecution
from backend.app.schemas.dashboard import QualityMetrics, MachineDriftMetric


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_machine_drift_metrics(self) -> List[MachineDriftMetric]:
        machines = self.db.execute(select(Machine)).scalars().all()
        results: List[MachineDriftMetric] = []

        for m in machines:
            total_pex = self.db.execute(
                select(func.count(ProcessExecution.process_execution_id)).where(
                    ProcessExecution.machine_id == m.machine_id
                )
            ).scalar() or 0

            total_def = self.db.execute(
                select(func.count(Defect.defect_id)).where(
                    Defect.machine_id == m.machine_id
                )
            ).scalar() or 0

            defect_rate = float(round(total_def / total_pex, 4)) if total_pex > 0 else 0.0

            results.append(
                MachineDriftMetric(
                    machine_id=m.machine_id,
                    machine_name=m.machine_name,
                    machine_type=m.machine_type,
                    machine_status=m.machine_status,
                    maintenance_risk_score=float(m.maintenance_risk_score),
                    total_process_executions=total_pex,
                    total_defects=total_def,
                    defect_rate=defect_rate,
                )
            )

        results.sort(key=lambda x: x.defect_rate, reverse=True)
        return results

    def get_quality_metrics(self) -> QualityMetrics:
        total_orders = self.db.execute(select(func.count(ProductionOrder.production_order_id))).scalar() or 0
        completed_orders = self.db.execute(
            select(func.count(ProductionOrder.production_order_id)).where(ProductionOrder.order_status == "COMPLETED")
        ).scalar() or 0

        total_inspections = self.db.execute(select(func.count(InspectionResult.inspection_result_id))).scalar() or 0
        total_defects = self.db.execute(select(func.count(Defect.defect_id))).scalar() or 0
        open_defects = self.db.execute(
            select(func.count(Defect.defect_id)).where(Defect.defect_status.in_(["OPEN", "UNDER_INVESTIGATION", "CAPA_IN_PROGRESS"]))
        ).scalar() or 0
        critical_defects = self.db.execute(
            select(func.count(Defect.defect_id)).where(Defect.severity == "CRITICAL")
        ).scalar() or 0

        active_containments = self.db.execute(
            select(func.count(ContainmentAction.containment_action_id)).where(
                ContainmentAction.containment_status == "ACTIVE"
            )
        ).scalar() or 0

        open_capas = self.db.execute(
            select(func.count(CorrectiveAction.corrective_action_id)).where(
                CorrectiveAction.corrective_action_status != "CLOSED"
            )
        ).scalar() or 0

        # Pending verifications: CAPAs that do not have a PASSED verification
        # Subquery of CAPAs with a PASSED verification
        passed_capas_sub = select(CAPAVerification.corrective_action_id).where(
            CAPAVerification.verification_result == "PASSED"
        ).distinct()
        pending_verifications = self.db.execute(
            select(func.count(CorrectiveAction.corrective_action_id)).where(
                CorrectiveAction.corrective_action_status != "CLOSED",
                CorrectiveAction.corrective_action_id.not_in(passed_capas_sub),
            )
        ).scalar() or 0

        # Defects by severity
        sev_rows = self.db.execute(
            select(Defect.severity, func.count(Defect.defect_id)).group_by(Defect.severity)
        ).all()
        defects_by_severity: Dict[str, int] = {row[0]: int(row[1]) for row in sev_rows}

        # Defects by category
        cat_rows = self.db.execute(
            select(Defect.defect_category, func.count(Defect.defect_id)).group_by(Defect.defect_category)
        ).all()
        defects_by_category: Dict[str, int] = {row[0]: int(row[1]) for row in cat_rows}

        drift_metrics = self.get_machine_drift_metrics()

        # Overall defect rate
        overall_defect_rate = float(round(total_defects / total_inspections, 4)) if total_inspections > 0 else 0.0

        return QualityMetrics(
            total_production_orders=total_orders,
            completed_production_orders=completed_orders,
            total_inspections=total_inspections,
            total_defects=total_defects,
            open_defects=open_defects,
            critical_defects=critical_defects,
            active_containments=active_containments,
            open_capas=open_capas,
            pending_verifications=pending_verifications,
            overall_defect_rate=overall_defect_rate,
            defects_by_severity=defects_by_severity,
            defects_by_category=defects_by_category,
            top_risk_machines=drift_metrics[:5],
        )
