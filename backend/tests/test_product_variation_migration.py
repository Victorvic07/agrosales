from pathlib import Path


def test_product_variation_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0003_create_product_variations.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"product_variations"' in content
    assert "internal_code" in content
    assert "standard_price" in content
    assert "commission_percentage" in content
    assert "product_id" in content