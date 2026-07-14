from pathlib import Path


def test_inventory_movement_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0005_create_inventory_movements.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"inventory_movements"' in content
    assert "movement_type" in content
    assert "previous_balance" in content
    assert "new_balance" in content
    assert "lot_id" in content
    assert "user_id" in content