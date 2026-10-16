from app.db.database import SessionLocal
from app.db.seed import seed_database
from app.tools.suppliers import rank_alternative_suppliers


def test_alternative_supplier_ranking_excludes_original_supplier():
    seed_database(force_reseed=True)
    db = SessionLocal()
    try:
        ranked = rank_alternative_suppliers("SKU-004", "SUP-003", 500, db)
        assert ranked
        assert all(s["id"] != "SUP-003" for s in ranked)
        assert all("selection_score" in s for s in ranked)
        assert all("covers_required_quantity" in s for s in ranked)
    finally:
        db.close()


def test_alternative_supplier_shortfall_is_exposed():
    seed_database(force_reseed=True)
    db = SessionLocal()
    try:
        ranked = rank_alternative_suppliers("SKU-004", "SUP-003", 12000, db)
        assert ranked
        candidate = ranked[0]
        assert candidate["shortfall"] >= 0
        assert candidate["covers_required_quantity"] is False
    finally:
        db.close()
