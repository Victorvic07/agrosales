from pathlib import Path


def test_stock_reservation_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0006_create_stock_reservations.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"stock_reservations"' in content
    assert "reservation_status" in content
    assert "ACTIVE" in content
    assert "RELEASED" in content
    assert "CONSUMED" in content
    assert "CANCELLED" in content
    assert "lot_id" in content
    assert "quantity" in content