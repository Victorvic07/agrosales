from pathlib import Path


def test_initial_user_migration_exists() -> None:
    migration = Path("app/migrations/versions/0001_create_users.py")

    assert migration.exists()

    content = migration.read_text(encoding="utf-8")

    assert "op.create_table(" in content
    assert '"users"' in content
    assert "ADMINISTRADOR" in content
    assert "PRODUTOR" in content
    assert "VENDEDOR" in content