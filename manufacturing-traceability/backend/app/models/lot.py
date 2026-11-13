from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base

class MaterialLot(Base):
    __tablename__ = "material_lots"

    material_lot_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(String(32), ForeignKey("suppliers.supplier_id"), nullable=False)
    material_product_id: Mapped[str] = mapped_column(String(32), ForeignKey("products.product_id"), nullable=False)
    supplier_batch_code: Mapped[str] = mapped_column(String(64), nullable=False)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    available_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=Decimal("0.0"), nullable=False)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=Decimal("0.0"), nullable=False)
    quarantined_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=Decimal("0.0"), nullable=False)
    uom: Mapped[str] = mapped_column(String(16), nullable=False)
    lot_status: Mapped[str] = mapped_column(String(32), default="RECEIVED", nullable=False)
    incoming_quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("95.0"), nullable=False)

    supplier = relationship("Supplier", back_populates="material_lots")
    material_product = relationship("Product")
    consumptions = relationship("MaterialConsumption", back_populates="material_lot")
    defects = relationship("Defect", back_populates="material_lot")

