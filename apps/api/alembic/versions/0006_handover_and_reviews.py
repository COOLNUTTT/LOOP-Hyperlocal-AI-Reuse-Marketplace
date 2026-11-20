# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create handover_events and reviews tables with Row Level Security.

Revision ID: 0006_handover_and_reviews
Revises: 0005_embeddings_and_saved_searches
Create Date: 2026-10-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_handover_and_reviews"
down_revision: Union[str, None] = "0005_embeddings_and_saved_searches"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "handover_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "buyer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "seller_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("meetup_spot", sa.String(200), nullable=False),
        sa.Column("otp_hash", sa.String(128), nullable=False),
        sa.Column("otp_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("otp_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("buyer_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("seller_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_handover_events_listing_id", "handover_events", ["listing_id"])
    op.create_index("ix_handover_events_buyer_id", "handover_events", ["buyer_id"])
    op.create_index("ix_handover_events_seller_id", "handover_events", ["seller_id"])
    op.create_index("ix_handover_events_status", "handover_events", ["status"])

    op.execute("ALTER TABLE handover_events ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY handover_participants ON handover_events
        FOR ALL
        USING (buyer_id = auth.uid() OR seller_id = auth.uid())
        WITH CHECK (buyer_id = auth.uid() OR seller_id = auth.uid());
        """
    )

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "handover_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("handover_events.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reviewer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reviewee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reviews_handover_id", "reviews", ["handover_id"])
    op.create_index("ix_reviews_reviewee_id", "reviews", ["reviewee_id"])

    op.execute("ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY reviews_select_all ON reviews FOR SELECT USING (true);
        """
    )
    op.execute(
        """
        CREATE POLICY reviews_insert_own ON reviews FOR INSERT WITH CHECK (reviewer_id = auth.uid());
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS reviews_insert_own ON reviews;")
    op.execute("DROP POLICY IF EXISTS reviews_select_all ON reviews;")
    op.drop_table("reviews")
    op.execute("DROP POLICY IF EXISTS handover_participants ON handover_events;")
    op.drop_table("handover_events")
