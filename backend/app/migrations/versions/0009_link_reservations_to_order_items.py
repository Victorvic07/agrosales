from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "stock_reservations",
        sa.Column(
            "order_item_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_stock_reservations_order_item_id_order_items",
        "stock_reservations",
        "order_items",
        ["order_item_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_stock_reservations_order_item_id",
        "stock_reservations",
        ["order_item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stock_reservations_order_item_id",
        table_name="stock_reservations",
    )

    op.drop_constraint(
        "fk_stock_reservations_order_item_id_order_items",
        "stock_reservations",
        type_="foreignkey",
    )

    op.drop_column(
        "stock_reservations",
        "order_item_id",
    )