from pathlib import Path


def test_categories_and_products_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0002_create_categories_and_products.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"categories"' in content
    assert '"products"' in content
    assert "category_id" in content
    assert "ForeignKeyConstraint" in content