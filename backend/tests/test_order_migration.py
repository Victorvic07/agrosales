from pathlib import Path


def test_order_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0008_create_orders_and_items.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"orders"' in content
    assert '"order_items"' in content
    assert "order_status" in content
    assert "customer_id" in content
    assert "seller_id" in content
    assert "product_variation_id" in content