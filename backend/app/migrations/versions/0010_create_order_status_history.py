"""create order status history

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


previous_status_enum = postgresql.ENUM(
    "DRAFT",
    "CONFIRMED",
    "CANCELLED",
    "COMPLETED",
    name="order_status_history_previous_status",
    create_type=False,
)

new_status_enum = postgresql.ENUM(
    "DRAFT",
    "CONFIRMED",
    "CANCELLED",
    "COMPLETED",
    name="order_status_history_new_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    previous_status_enum.create(
        bind,
        checkfirst=True,
    )
    new_status_enum.create(
        bind,
        checkfirst=True,
    )

    op.create_table(
        "order_status_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "order_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "previous_status",
            previous_status_enum,
            nullable=True,
        ),
        sa.Column(
            "new_status",
            new_status_enum,
            nullable=False,
        ),
        sa.Column(
            "changed_by_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_order_status_history_order_id",
        "order_status_history",
        ["order_id"],
        unique=False,
    )

    op.create_index(
        "ix_order_status_history_changed_by_user_id",
        "order_status_history",
        ["changed_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_order_status_history_changed_by_user_id",
        table_name="order_status_history",
    )

    op.drop_index(
        "ix_order_status_history_order_id",
        table_name="order_status_history",
    )

    op.drop_table("order_status_history")

    bind = op.get_bind()

    new_status_enum.drop(
        bind,
        checkfirst=True,
    )
    previous_status_enum.drop(
        bind,
        checkfirst=True,
    )