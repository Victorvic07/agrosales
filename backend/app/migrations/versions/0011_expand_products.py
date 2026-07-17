"""Expande o cadastro de produtos.

Revision ID: 0011
Revises: 0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011"
down_revision = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


product_unit_enum = postgresql.ENUM(
    "UNIDADE",
    "QUILOGRAMA",
    "GRAMA",
    "LITRO",
    "MILILITRO",
    "CAIXA",
    "PACOTE",
    "OUTRO",
    name="product_unit",
    create_type=False,
)

product_status_enum = postgresql.ENUM(
    "ATIVO",
    "INATIVO",
    "DESCONTINUADO",
    name="product_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()

    product_unit_enum.create(bind, checkfirst=True)
    product_status_enum.create(bind, checkfirst=True)

    op.add_column(
        "products",
        sa.Column(
            "code",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "unit",
            product_unit_enum,
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "custom_unit",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "cost_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "standard_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "minimum_price",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "short_description",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "detailed_description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "internal_notes",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "image_path",
            sa.String(length=500),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "status",
            product_status_enum,
            nullable=True,
        ),
    )

    # Gera códigos únicos para os produtos já existentes.
    op.execute(
        """
        WITH numbered_products AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    ORDER BY created_at, id
                ) AS sequence_number
            FROM products
        )
        UPDATE products AS product
        SET code = (
            'PRD-' ||
            LPAD(
                numbered_products.sequence_number::text,
                6,
                '0'
            )
        )
        FROM numbered_products
        WHERE product.id = numbered_products.id
        """
    )

    # Migra os dados das colunas antigas.
    op.execute(
        """
        UPDATE products
        SET
            unit = 'UNIDADE',
            cost_price = 0,
            standard_price = 0,
            minimum_price = 0,
            short_description = description,
            status = CASE
                WHEN is_active IS TRUE
                    THEN 'ATIVO'::product_status
                ELSE 'INATIVO'::product_status
            END
        """
    )

    op.alter_column(
        "products",
        "code",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.alter_column(
        "products",
        "unit",
        existing_type=product_unit_enum,
        nullable=False,
    )

    op.alter_column(
        "products",
        "cost_price",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=False,
    )

    op.alter_column(
        "products",
        "standard_price",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=False,
    )

    op.alter_column(
        "products",
        "minimum_price",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=False,
    )

    op.alter_column(
        "products",
        "status",
        existing_type=product_status_enum,
        nullable=False,
    )

    op.alter_column(
        "products",
        "category_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )

    op.create_unique_constraint(
        "uq_products_code",
        "products",
        ["code"],
    )

    op.create_index(
        "ix_products_code",
        "products",
        ["code"],
        unique=False,
    )

    op.create_index(
        "ix_products_status",
        "products",
        ["status"],
        unique=False,
    )

    op.drop_column(
        "products",
        "description",
    )

    op.drop_column(
        "products",
        "is_active",
    )


def downgrade() -> None:
    op.add_column(
        "products",
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
    )

    op.execute(
    """
    UPDATE products
    SET
        unit = 'UNIDADE'::product_unit,
        cost_price = 0,
        standard_price = 0,
        minimum_price = 0,
        short_description = description,
        status = CASE
            WHEN is_active IS TRUE
                THEN 'ATIVO'::product_status
            ELSE 'INATIVO'::product_status
        END
    """
)

    op.drop_index(
        "ix_products_status",
        table_name="products",
    )

    op.drop_index(
        "ix_products_code",
        table_name="products",
    )

    op.drop_constraint(
        "uq_products_code",
        "products",
        type_="unique",
    )

    op.drop_column("products", "status")
    op.drop_column("products", "image_path")
    op.drop_column("products", "internal_notes")
    op.drop_column("products", "detailed_description")
    op.drop_column("products", "short_description")
    op.drop_column("products", "minimum_price")
    op.drop_column("products", "standard_price")
    op.drop_column("products", "cost_price")
    op.drop_column("products", "custom_unit")
    op.drop_column("products", "unit")
    op.drop_column("products", "code")

    op.alter_column(
        "products",
        "category_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    bind = op.get_bind()

    product_status_enum.drop(bind, checkfirst=True)
    product_unit_enum.drop(bind, checkfirst=True)
