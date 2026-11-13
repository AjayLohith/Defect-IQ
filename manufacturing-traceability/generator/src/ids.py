"""Deterministic zero-padded ID generators."""

def format_sku_id(seq: int) -> str:
    return f"SKU-{seq:06d}"

def format_supplier_id(seq: int) -> str:
    return f"SUP-{seq:04d}"

def format_lot_id(supplier_seq: int, year: int, seq: int) -> str:
    return f"LOT-SUP-{supplier_seq:04d}-{year}-{seq:06d}"

def format_order_id(year: int, seq: int) -> str:
    return f"WO-{year}-{seq:06d}"

def format_inspection_id(year: int, order_seq: int, insp_seq: int) -> str:
    return f"INSP-WO-{year}-{order_seq:06d}-{insp_seq:03d}"

def format_defect_id(year: int, seq: int) -> str:
    return f"DEF-{year}-{seq:06d}"

def format_capa_id(year: int, seq: int) -> str:
    return f"CAPA-{year}-{seq:06d}"

