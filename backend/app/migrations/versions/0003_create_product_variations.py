from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_variations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "internal_code",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "classification",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "package_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "unit_of_measure",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "weight_or_volume",
            sa.Numeric(12, 3),
            nullable=True,
        ),
        sa.Column(
            "standard_price",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "minimum_price",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "minimum_stock",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "commission_percentage",
            sa.Numeric(5, 2),
            nullable=False,
        ),
        sa.Column(
            "barcode",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "qr_code",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
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
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("internal_code"),
        sa.UniqueConstraint("barcode"),
        sa.UniqueConstraint("qr_code"),
    )

    op.create_index(
        op.f("ix_product_variations_product_id"),
        "product_variations",
        ["product_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_product_variations_product_id"),
        table_name="product_variations",
    )
    op.drop_table("product_variations")