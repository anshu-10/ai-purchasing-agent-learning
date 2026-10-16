from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.db.database import DBSupplier

def get_supplier_info(supplier_id: str, db: Session) -> Optional[Dict[str, Any]]:
    supplier = db.query(DBSupplier).filter(DBSupplier.id == supplier_id).first()
    if not supplier:
        return None
        
    return {
        "id": supplier.id,
        "name": supplier.name,
        "lead_time_days": supplier.lead_time_days,
        "minimum_order_quantity": supplier.minimum_order_quantity,
        "available_quantity": supplier.available_quantity,
        "unit_cost": supplier.unit_cost
    }

def get_alternative_suppliers(product_id: str, db: Session) -> List[Dict[str, Any]]:
    """Return supplier candidates for a product."""
    suppliers = db.query(DBSupplier).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "lead_time_days": s.lead_time_days,
            "minimum_order_quantity": s.minimum_order_quantity,
            "available_quantity": s.available_quantity,
            "unit_cost": s.unit_cost,
        }
        for s in suppliers
    ]


def rank_alternative_suppliers(
    product_id: str,
    original_supplier_id: str,
    required_qty: int,
    db: Session,
) -> List[Dict[str, Any]]:
    """Rank alternatives using deterministic procurement signals."""
    candidates = get_alternative_suppliers(product_id, db)
    ranked = []

    for supplier in candidates:
        if supplier["id"] == original_supplier_id:
            continue

        capacity = supplier["available_quantity"]
        moq = supplier["minimum_order_quantity"]
        covers_quantity = capacity >= required_qty
        meets_moq = required_qty >= moq
        shortfall = max(required_qty - capacity, 0)

        score = 0
        score += 50 if covers_quantity else 0
        score += 20 if meets_moq else 0
        score += max(0, 15 - min(supplier["lead_time_days"], 15))
        score += max(0, 15 - min(int(supplier["unit_cost"] / 100), 15))

        ranked.append({
            **supplier,
            "covers_required_quantity": covers_quantity,
            "meets_moq": meets_moq,
            "shortfall": shortfall,
            "selection_score": score,
        })

    return sorted(
        ranked,
        key=lambda x: (
            x["covers_required_quantity"],
            x["meets_moq"],
            x["selection_score"],
            -x["unit_cost"],
            -x["lead_time_days"],
        ),
        reverse=True,
    )
