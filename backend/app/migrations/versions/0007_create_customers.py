from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

customer_type = postgresql.ENUM(
    "INDIVIDUAL",
    "COMPANY",
    name="customer_type",
    create_type=False,
)

customer_document_type = postgresql.ENUM(
    "CPF",
    "CNPJ",
    name="customer_document_type",
    create_type=False,
)


def upgrade() -> None:
    customer_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    customer_document_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "customer_type",
            customer_type,
            nullable=False,
        ),
        sa.Column(
            "document_type",
            customer_document_type,
            nullable=False,
        ),
        sa.Column(
            "document",
            sa.String(length=14),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "email",
            sa.String(length=254),
            nullable=True,
        ),
        sa.Column(
            "street",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "number",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "complement",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "neighborhood",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "state",
            sa.String(length=2),
            nullable=True,
        ),
        sa.Column(
            "zip_code",
            sa.String(length=8),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document",
            name="uq_customers_document",
        ),
    )

    op.create_index(
        op.f("ix_customers_document"),
        "customers",
        ["document"],
        unique=True,
    )

    op.create_index(
        op.f("ix_customers_name"),
        "customers",
        ["name"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_customers_name"),
        table_name="customers",
    )

    op.drop_index(
        op.f("ix_customers_document"),
        table_name="customers",
    )

    op.drop_table("customers")

    customer_document_type.drop(
        op.get_bind(),
        checkfirst=True,
    )

    customer_type.drop(
        op.get_bind(),
        checkfirst=True,
    )