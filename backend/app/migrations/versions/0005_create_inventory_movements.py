from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

movement_type = postgresql.ENUM(
    "ENTRY",
    "SALE",
    "LOSS",
    "RETURN",
    "ADJUSTMENT",
    name="movement_type",
    create_type=False,
)


def upgrade() -> None:
    movement_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "inventory_movements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "lot_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "movement_type",
            movement_type,
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "previous_balance",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "new_balance",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "reason",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lot_id"],
            ["lots.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_inventory_movements_quantity_positive",
        ),
        sa.CheckConstraint(
            "previous_balance >= 0",
            name="ck_inventory_movements_previous_balance_non_negative",
        ),
        sa.CheckConstraint(
            "new_balance >= 0",
            name="ck_inventory_movements_new_balance_non_negative",
        ),
    )

    op.create_index(
        op.f("ix_inventory_movements_lot_id"),
        "inventory_movements",
        ["lot_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_movements_user_id"),
        "inventory_movements",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_inventory_movements_user_id"),
        table_name="inventory_movements",
    )

    op.drop_index(
        op.f("ix_inventory_movements_lot_id"),
        table_name="inventory_movements",
    )

    op.drop_table("inventory_movements")

    movement_type.drop(op.get_bind(), checkfirst=True)