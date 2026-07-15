from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

reservation_status = postgresql.ENUM(
    "ACTIVE",
    "RELEASED",
    "CONSUMED",
    "CANCELLED",
    name="reservation_status",
    create_type=False,
)


def upgrade() -> None:
    reservation_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "stock_reservations",
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
            "quantity",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "status",
            reservation_status,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lot_id"],
            ["lots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_stock_reservations_quantity_positive",
        ),
    )

    op.create_index(
        op.f("ix_stock_reservations_lot_id"),
        "stock_reservations",
        ["lot_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_stock_reservations_lot_id"),
        table_name="stock_reservations",
    )

    op.drop_table("stock_reservations")

    reservation_status.drop(
        op.get_bind(),
        checkfirst=True,
    )