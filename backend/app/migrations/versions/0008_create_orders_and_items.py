from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

order_status = postgresql.ENUM(
    "DRAFT",
    "CONFIRMED",
    "CANCELLED",
    "COMPLETED",
    name="order_status",
    create_type=False,
)


def upgrade() -> None:
    order_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "orders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            order_status,
            nullable=False,
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(14, 2),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "discount_total",
            sa.Numeric(14, 2),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(14, 2),
            server_default="0",
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
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "confirmed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_orders_customer_id"),
        "orders",
        ["customer_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_orders_seller_id"),
        "orders",
        ["seller_id"],
        unique=False,
    )

    op.create_table(
        "order_items",
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
            "product_variation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "discount_amount",
            sa.Numeric(14, 2),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(14, 2),
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
            ["order_id"],
            ["orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_variation_id"],
            ["product_variations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "order_id",
            "product_variation_id",
            name="uq_order_items_order_variation",
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        sa.CheckConstraint(
            "unit_price > 0",
            name="ck_order_items_unit_price_positive",
        ),
        sa.CheckConstraint(
            "discount_amount >= 0",
            name="ck_order_items_discount_non_negative",
        ),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="ck_order_items_total_non_negative",
        ),
    )

    op.create_index(
        op.f("ix_order_items_order_id"),
        "order_items",
        ["order_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_order_items_product_variation_id"),
        "order_items",
        ["product_variation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_order_items_product_variation_id"),
        table_name="order_items",
    )

    op.drop_index(
        op.f("ix_order_items_order_id"),
        table_name="order_items",
    )

    op.drop_table("order_items")

    op.drop_index(
        op.f("ix_orders_seller_id"),
        table_name="orders",
    )

    op.drop_index(
        op.f("ix_orders_customer_id"),
        table_name="orders",
    )

    op.drop_table("orders")

    order_status.drop(
        op.get_bind(),
        checkfirst=True,
    )