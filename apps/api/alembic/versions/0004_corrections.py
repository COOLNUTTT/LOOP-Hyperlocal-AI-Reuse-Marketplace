# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create corrections table with Row Level Security and training eligibility flag.

Revision ID: 0004_corrections
Revises: 0003_messages_and_flags
Create Date: 2026-10-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_corrections"
down_revision: Union[str, None] = "0003_messages_and_flags"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create corrections table
    op.create_table(
        "corrections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field", sa.String(50), nullable=False),
        sa.Column("ai_value", sa.Text(), nullable=False),
        sa.Column("user_value", sa.Text(), nullable=False),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("model_version", sa.String(50), nullable=False, server_default="v1.0.0"),
        sa.Column("eligible_for_training", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("data_origin", sa.String(20), nullable=False, server_default="real"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # 2. Indexes for efficient lookup during active learning extraction
    op.create_index("ix_corrections_listing_id", "corrections", ["listing_id"])
    op.create_index("ix_corrections_user_id", "corrections", ["user_id"])
    op.create_index("ix_corrections_field", "corrections", ["field"])
    op.create_index("ix_corrections_eligible_for_training", "corrections", ["eligible_for_training"])
    op.create_index("ix_corrections_created_at", "corrections", ["created_at"])

    # 3. Enable RLS
    op.execute("ALTER TABLE corrections ENABLE ROW LEVEL SECURITY;")

    # Users can view their own corrections
    op.execute(
        """
        CREATE POLICY corrections_select_own ON corrections
        FOR SELECT
        USING (user_id = auth.uid());
        """
    )

    # Users can insert corrections for their own listings
    op.execute(
        """
        CREATE POLICY corrections_insert_own ON corrections
        FOR INSERT
        WITH CHECK (user_id = auth.uid());
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS corrections_insert_own ON corrections;")
    op.execute("DROP POLICY IF EXISTS corrections_select_own ON corrections;")
    op.drop_table("corrections")
