# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create audit_logs and model_versions tables with Row Level Security.

Revision ID: 0007_model_versions_and_audit
Revises: 0006_handover_and_reviews
Create Date: 2026-10-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007_model_versions_and_audit"
down_revision: Union[str, None] = "0006_handover_and_reviews"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "actor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "details",
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
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY audit_logs_select_admin ON audit_logs
        FOR SELECT
        USING (true);
        """
    )

    op.create_table(
        "model_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("version", sa.String(50), nullable=False),
        sa.Column("onnx_path", sa.String(255), nullable=False),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "baseline_metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("trained_on_hash", sa.String(128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_model_versions_name", "model_versions", ["name"])
    op.create_index("ix_model_versions_version", "model_versions", ["version"])
    op.create_index("ix_model_versions_is_active", "model_versions", ["is_active"])
    op.create_index("ix_model_versions_created_at", "model_versions", ["created_at"])

    op.execute("ALTER TABLE model_versions ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY model_versions_select_all ON model_versions
        FOR SELECT
        USING (true);
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS model_versions_select_all ON model_versions;")
    op.drop_table("model_versions")
    op.execute("DROP POLICY IF EXISTS audit_logs_select_admin ON audit_logs;")
    op.drop_table("audit_logs")
