from app.core.enums import UserRole
from app.modules.users.model import User


def test_user_roles_are_correct() -> None:
    assert {role.value for role in UserRole} == {
        "ADMINISTRADOR",
        "PRODUTOR",
        "VENDEDOR",
    }


def test_user_column_defaults_to_active() -> None:
    default = User.__table__.c.is_active.default

    assert default is not None
    assert default.arg is True