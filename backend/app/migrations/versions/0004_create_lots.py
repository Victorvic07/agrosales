from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "product_variation_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(length=80),
            nullable=False,
        ),
        sa.Column(
            "production_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "expiration_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "physical_quantity",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "reserved_quantity",
            sa.Numeric(12, 3),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
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
            ["product_variation_id"],
            ["product_variations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.CheckConstraint(
            "physical_quantity >= 0",
            name="ck_lots_physical_quantity_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_lots_reserved_quantity_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity <= physical_quantity",
            name="ck_lots_reserved_not_above_physical",
        ),
        sa.CheckConstraint(
            "expiration_date >= production_date",
            name="ck_lots_expiration_after_production",
        ),
    )

    op.create_index(
        op.f("ix_lots_product_variation_id"),
        "lots",
        ["product_variation_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_lots_expiration_date"),
        "lots",
        ["expiration_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_lots_expiration_date"),
        table_name="lots",
    )

    op.drop_index(
        op.f("ix_lots_product_variation_id"),
        table_name="lots",
    )

    op.drop_table("lots")