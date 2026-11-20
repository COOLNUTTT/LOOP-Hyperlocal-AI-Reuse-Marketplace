# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create messages and flags tables with Row Level Security.

Revision ID: 0003_messages_and_flags
Revises: 0002_listings_and_images
Create Date: 2026-10-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_messages_and_flags"
down_revision: Union[str, None] = "0002_listings_and_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create messages table
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "sender_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "receiver_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("flagged_scam", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_messages_listing_id", "messages", ["listing_id"])
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"])
    op.create_index("ix_messages_receiver_id", "messages", ["receiver_id"])
    op.create_index("ix_messages_created_at", "messages", ["created_at"])
    op.create_index("ix_messages_thread", "messages", ["listing_id", "sender_id", "receiver_id"])

    # 2. Create flags table
    op.create_table(
        "flags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "reporter_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("flag_type", sa.String(length=50), nullable=False, server_default=sa.text("'manual_report'")),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'open'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_flags_listing_id", "flags", ["listing_id"])
    op.create_index("ix_flags_message_id", "flags", ["message_id"])
    op.create_index("ix_flags_reporter_id", "flags", ["reporter_id"])
    op.create_index("ix_flags_status", "flags", ["status"])

    # 3. Enable RLS
    op.execute("ALTER TABLE messages ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE flags ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE messages FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE flags FORCE ROW LEVEL SECURITY;")

    # 4. Policies for messages (non-participants strictly blocked)
    op.execute("""
        CREATE POLICY "Participants can view their thread messages"
        ON messages FOR SELECT
        USING (
            auth.role() = 'authenticated' AND (
                auth.uid() IN (SELECT auth_uid FROM users WHERE id = sender_id)
                OR auth.uid() IN (SELECT auth_uid FROM users WHERE id = receiver_id)
            )
        );
    """)
    op.execute("""
        CREATE POLICY "Senders can insert messages"
        ON messages FOR INSERT
        WITH CHECK (
            auth.role() = 'authenticated' AND
            auth.uid() IN (SELECT auth_uid FROM users WHERE id = sender_id)
        );
    """)

    # 5. Policies for flags
    op.execute("""
        CREATE POLICY "Reporters can insert flags"
        ON flags FOR INSERT
        WITH CHECK (
            auth.role() = 'authenticated' AND (
                reporter_id IS NULL OR
                auth.uid() IN (SELECT auth_uid FROM users WHERE id = reporter_id)
            )
        );
    """)
    op.execute("""
        CREATE POLICY "Reporters can view their own flags"
        ON flags FOR SELECT
        USING (
            auth.role() = 'authenticated' AND
            auth.uid() IN (SELECT auth_uid FROM users WHERE id = reporter_id)
        );
    """)


def downgrade() -> None:
    op.drop_table("flags")
    op.drop_table("messages")
