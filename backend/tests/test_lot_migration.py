from pathlib import Path


def test_lot_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0004_create_lots.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"lots"' in content
    assert "product_variation_id" in content
    assert "physical_quantity" in content
    assert "reserved_quantity" in content
    assert "expiration_date" in content
    assert "CheckConstraint" in content