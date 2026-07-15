from pathlib import Path


def test_order_reservation_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/"
        "0009_link_reservations_to_order_items.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"stock_reservations"' in content
    assert '"order_items"' in content
    assert '"order_item_id"' in content
    assert '"id"' in content
    assert "fk_stock_reservations_order_item_id_order_items" in content
    assert "ix_stock_reservations_order_item_id" in content
    assert 'ondelete="SET NULL"' in content