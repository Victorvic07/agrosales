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


def test_expand_products_migration_exists() -> None:
    migration = Path(
        "app/migrations/versions/0011_expand_products.py"
    )

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert 'revision = "0011"' in content
    assert 'down_revision = "0010"' in content

    assert "product_unit" in content
    assert "product_status" in content

    assert '"code"' in content
    assert '"unit"' in content
    assert '"custom_unit"' in content
    assert '"cost_price"' in content
    assert '"standard_price"' in content
    assert '"minimum_price"' in content
    assert '"short_description"' in content
    assert '"detailed_description"' in content
    assert '"internal_notes"' in content
    assert '"image_path"' in content
    assert '"status"' in content

    assert "PRD-" in content
    assert "description" in content
    assert "is_active" in content
    assert "alter_column" in content
    assert "downgrade" in content
    assert "::product_unit" in content
    assert "::product_status" in content


def test_expand_products_upgrade_casts_status_values_to_postgresql_enum() -> None:
    migration = Path(
        "app/migrations/versions/0011_expand_products.py"
    )
    content = migration.read_text(encoding="utf-8")
    upgrade = content.split("def upgrade() -> None:", 1)[1].split(
        "def downgrade() -> None:", 1
    )[0]

    assert "'ATIVO'::product_status" in upgrade
    assert "'INATIVO'::product_status" in upgrade
