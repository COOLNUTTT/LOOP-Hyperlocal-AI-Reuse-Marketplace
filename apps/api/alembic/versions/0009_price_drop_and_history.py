# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create price_drop_suggestions and price_history tables with Row Level Security.

Revision ID: 0009_price_drop_and_history
Revises: 0008_swap_and_impact
Create Date: 2026-10-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0009_price_drop_and_history"
down_revision: Union[str, None] = "0008_swap_and_impact"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_drop_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("suggested_price", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "reason",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("p_sale_7d_before", sa.Float(), nullable=False),
        sa.Column("p_sale_7d_after", sa.Float(), nullable=False),
        sa.Column("accepted", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_price_drop_suggestions_listing_id", "price_drop_suggestions", ["listing_id"])
    op.create_index("ix_price_drop_suggestions_created_at", "price_drop_suggestions", ["created_at"])

    op.execute("ALTER TABLE price_drop_suggestions ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY price_drop_suggestions_select_all ON price_drop_suggestions
        FOR SELECT
        USING (true);
        """
    )

    op.create_table(
        "price_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subtype", sa.String(100), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("condition", sa.String(30), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="completed_trade"),
        sa.Column("data_origin", sa.String(20), nullable=False, server_default="simulated"),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_price_history_category", "price_history", ["category"])
    op.create_index("ix_price_history_subtype", "price_history", ["subtype"])
    op.create_index("ix_price_history_observed_at", "price_history", ["observed_at"])

    op.execute("ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY price_history_select_all ON price_history
        FOR SELECT
        USING (true);
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS price_history_select_all ON price_history;")
    op.drop_table("price_history")
    op.execute("DROP POLICY IF EXISTS price_drop_suggestions_select_all ON price_drop_suggestions;")
    op.drop_table("price_drop_suggestions")
