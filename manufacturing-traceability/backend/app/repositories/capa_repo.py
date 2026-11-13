from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from backend.app.models.capa import CorrectiveAction, CAPAVerification
from backend.app.models.event import StateEvent
from backend.app.schemas.capa import (
    CorrectiveActionDetail,
    CorrectiveActionCreate,
    CAPAVerificationCreate,
    CAPAVerificationBase,
)


class CAPARepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, capa_id: str) -> Optional[CorrectiveAction]:
        return self.db.execute(
            select(CorrectiveAction).where(CorrectiveAction.corrective_action_id == capa_id)
        ).scalar_one_or_none()

    def get_detail_by_id(self, capa_id: str) -> Optional[CorrectiveActionDetail]:
        capa = self.get_by_id(capa_id)
        if not capa:
            return None

        verifications = self.db.execute(
            select(CAPAVerification).where(CAPAVerification.corrective_action_id == capa_id)
        ).scalars().all()

        v_list = [
            CAPAVerificationBase(
                verification_id=v.verification_id,
                corrective_action_id=v.corrective_action_id,
                verification_date=v.verification_date,
                verification_method=v.verification_method,
                verification_result=v.verification_result,
                verified_by_role=v.verified_by_role,
                evidence_reference=v.evidence_reference,
            )
            for v in verifications
        ]

        has_passed = any(v.verification_result == "PASSED" for v in v_list)
        ready_for_closure = has_passed and capa.corrective_action_status != "CLOSED"

        return CorrectiveActionDetail(
            corrective_action_id=capa.corrective_action_id,
            defect_id=capa.defect_id,
            root_cause_category=capa.root_cause_category,
            root_cause_description=capa.root_cause_description,
            owner_role=capa.owner_role,
            due_date=capa.due_date,
            implementation_date=capa.implementation_date,
            corrective_action_status=capa.corrective_action_status,
            effectiveness_target=capa.effectiveness_target,
            verifications=v_list,
            has_passed_verification=has_passed,
            ready_for_closure=ready_for_closure,
        )

    def list_capas(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CorrectiveActionDetail]:
        stmt = select(CorrectiveAction)
        if status:
            stmt = stmt.where(CorrectiveAction.corrective_action_status == status)
        stmt = stmt.order_by(desc(CorrectiveAction.due_date)).offset(offset).limit(limit)
        capas = list(self.db.execute(stmt).scalars().all())

        return [self.get_detail_by_id(c.corrective_action_id) for c in capas if c]

    def create_capa(self, data: CorrectiveActionCreate) -> CorrectiveAction:
        total = self.db.execute(select(func.count(CorrectiveAction.corrective_action_id))).scalar() or 0
        capa_id = f"CAPA-2026-{total + 1:06d}"

        capa = CorrectiveAction(
            corrective_action_id=capa_id,
            defect_id=data.defect_id,
            root_cause_category=data.root_cause_category,
            root_cause_description=data.root_cause_description,
            owner_role=data.owner_role,
            due_date=data.due_date,
            implementation_date=None,
            corrective_action_status="OPEN",
            effectiveness_target=data.effectiveness_target,
        )
        self.db.add(capa)

        # Append StateEvent for CAPA creation
        event_count = self.db.execute(select(func.count(StateEvent.event_id))).scalar() or 0
        evt = StateEvent(
            event_id=f"EVT-{event_count + 1:08d}",
            entity_type="CORRECTIVE_ACTION",
            entity_id=capa_id,
            corrective_action_id=capa_id,
            event_sequence=1,
            previous_state=None,
            new_state="OPEN",
            event_timestamp=datetime.now(timezone.utc),
            actor_role=data.actor_role,
            reason_code=data.reason_code,
            event_notes=f"CAPA initiated: {data.root_cause_description[:100]}",
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(capa)
        return capa

    def add_verification(self, capa_id: str, data: CAPAVerificationCreate) -> CAPAVerification:
        total = self.db.execute(select(func.count(CAPAVerification.verification_id))).scalar() or 0
        verif_id = f"VRF-2026-{total + 1:06d}"

        verif = CAPAVerification(
            verification_id=verif_id,
            corrective_action_id=capa_id,
            verification_date=data.verification_date,
            verification_method=data.verification_method,
            verification_result=data.verification_result,
            verified_by_role=data.verified_by_role,
            evidence_reference=data.evidence_reference,
        )
        self.db.add(verif)

        # If verification passed, update CAPA status to VERIFIED (if not already verified or closed)
        capa = self.get_by_id(capa_id)
        if capa and data.verification_result == "PASSED" and capa.corrective_action_status in ("OPEN", "IMPLEMENTED"):
            prev_status = capa.corrective_action_status
            capa.corrective_action_status = "VERIFIED"

            max_seq = self.db.execute(
                select(func.coalesce(func.max(StateEvent.event_sequence), 0)).where(
                    StateEvent.entity_type == "CORRECTIVE_ACTION",
                    StateEvent.corrective_action_id == capa_id,
                )
            ).scalar() or 0

            evt_cnt = self.db.execute(select(func.count(StateEvent.event_id))).scalar() or 0
            evt = StateEvent(
                event_id=f"EVT-{evt_cnt + 1:08d}",
                entity_type="CORRECTIVE_ACTION",
                entity_id=capa_id,
                corrective_action_id=capa_id,
                event_sequence=max_seq + 1,
                previous_state=prev_status,
                new_state="VERIFIED",
                event_timestamp=datetime.now(timezone.utc),
                actor_role=data.verified_by_role,
                reason_code="RC_EFFECTIVENESS_VERIFIED",
                event_notes=f"Verified via {data.verification_method}: {data.evidence_reference}",
            )
            self.db.add(evt)

        self.db.commit()
        self.db.refresh(verif)
        return verif

