from pathlib import Path


def test_customer_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0007_create_customers.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert '"customers"' in content
    assert "customer_type" in content
    assert "customer_document_type" in content
    assert "document" in content
    assert "is_active" in content