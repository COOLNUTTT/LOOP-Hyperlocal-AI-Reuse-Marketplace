# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create wishlists, swap_cycles, swap_proposals, and impact_events tables with RLS.

Revision ID: 0008_swap_and_impact
Revises: 0007_model_versions_and_audit
Create Date: 2026-10-29
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0008_swap_and_impact"
down_revision: Union[str, None] = "0007_model_versions_and_audit"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wishlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("want_category", sa.String(50), nullable=False),
        sa.Column("want_text", sa.Text(), nullable=False),
        sa.Column("want_embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("max_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_wishlists_user_id", "wishlists", ["user_id"])
    op.create_index("ix_wishlists_want_category", "wishlists", ["want_category"])
    op.create_index("ix_wishlists_active", "wishlists", ["active"])

    op.execute("ALTER TABLE wishlists ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY wishlists_own_manage ON wishlists
        FOR ALL
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid());
        """
    )

    op.create_table(
        "swap_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="proposed"),
        sa.Column("length", sa.Integer(), nullable=False),
        sa.Column(
            "solver_version",
            sa.String(50),
            nullable=False,
            server_default="cpsat_set_packing_v1",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_swap_cycles_status", "swap_cycles", ["status"])

    op.execute("ALTER TABLE swap_cycles ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY swap_cycles_select_all ON swap_cycles
        FOR SELECT
        USING (true);
        """
    )

    op.create_table(
        "swap_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "cycle_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("swap_cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "giver_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "receiver_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.UniqueConstraint("cycle_id", "giver_user_id", name="uq_swap_proposals_cycle_giver"),
    )
    op.create_index("ix_swap_proposals_cycle_id", "swap_proposals", ["cycle_id"])
    op.create_index("ix_swap_proposals_giver_user_id", "swap_proposals", ["giver_user_id"])
    op.create_index("ix_swap_proposals_receiver_user_id", "swap_proposals", ["receiver_user_id"])
    op.create_index("ix_swap_proposals_listing_id", "swap_proposals", ["listing_id"])

    op.execute("ALTER TABLE swap_proposals ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY swap_proposals_participants ON swap_proposals
        FOR ALL
        USING (giver_user_id = auth.uid() OR receiver_user_id = auth.uid())
        WITH CHECK (giver_user_id = auth.uid() OR receiver_user_id = auth.uid());
        """
    )

    op.create_table(
        "impact_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "handover_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("handover_events.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("co2_kg_avoided", sa.Numeric(10, 3), nullable=False),
        sa.Column("ewaste_kg_avoided", sa.Numeric(10, 3), nullable=False),
        sa.Column("factor_source", sa.String(255), nullable=False),
        sa.Column(
            "assumptions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_impact_events_handover_id", "impact_events", ["handover_id"])
    op.create_index("ix_impact_events_listing_id", "impact_events", ["listing_id"])
    op.create_index("ix_impact_events_created_at", "impact_events", ["created_at"])

    op.execute("ALTER TABLE impact_events ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY impact_events_select_all ON impact_events
        FOR SELECT
        USING (true);
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS impact_events_select_all ON impact_events;")
    op.drop_table("impact_events")
    op.execute("DROP POLICY IF EXISTS swap_proposals_participants ON swap_proposals;")
    op.drop_table("swap_proposals")
    op.execute("DROP POLICY IF EXISTS swap_cycles_select_all ON swap_cycles;")
    op.drop_table("swap_cycles")
    op.execute("DROP POLICY IF EXISTS wishlists_own_manage ON wishlists;")
    op.drop_table("wishlists")
