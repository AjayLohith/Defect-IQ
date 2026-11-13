from backend.app.schemas.event import StateEventBase
from backend.app.schemas.product import ProductBase, BOMBase, BOMLineBase
from backend.app.schemas.supplier import SupplierBase
from backend.app.schemas.machine import MachineBase, ProcessStepBase
from backend.app.schemas.lot import MaterialLotBase, MaterialLotDetail
from backend.app.schemas.order import (
    ProductionOrderBase,
    MaterialConsumptionBase,
    ProcessExecutionBase,
    BOMReconciliationItem,
    BOMReconciliationReport,
)
from backend.app.schemas.defect import DefectBase, DefectDetail, DefectCreate
from backend.app.schemas.containment import ContainmentActionBase, ContainmentActionCreate
from backend.app.schemas.capa import (
    CorrectiveActionBase,
    CorrectiveActionDetail,
    CorrectiveActionCreate,
    CAPAVerificationBase,
    CAPAVerificationCreate,
    CAPACloseRequest,
)
from backend.app.schemas.traceability import (
    UpstreamTraceResult,
    DownstreamImpactResult,
    ConsumedLotTraceItem,
    DownstreamImpactOrderItem,
)
from backend.app.schemas.dashboard import QualityMetrics, MachineDriftMetric

__all__ = [
    "StateEventBase",
    "ProductBase",
    "BOMBase",
    "BOMLineBase",
    "SupplierBase",
    "MachineBase",
    "ProcessStepBase",
    "MaterialLotBase",
    "MaterialLotDetail",
    "ProductionOrderBase",
    "MaterialConsumptionBase",
    "ProcessExecutionBase",
    "BOMReconciliationItem",
    "BOMReconciliationReport",
    "DefectBase",
    "DefectDetail",
    "DefectCreate",
    "ContainmentActionBase",
    "ContainmentActionCreate",
    "CorrectiveActionBase",
    "CorrectiveActionDetail",
    "CorrectiveActionCreate",
    "CAPAVerificationBase",
    "CAPAVerificationCreate",
    "CAPACloseRequest",
    "UpstreamTraceResult",
    "DownstreamImpactResult",
    "ConsumedLotTraceItem",
    "DownstreamImpactOrderItem",
    "QualityMetrics",
    "MachineDriftMetric",
]
