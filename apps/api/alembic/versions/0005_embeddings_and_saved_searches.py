# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Add pgvector text/image embeddings to listings and create saved_searches table with RLS.

Revision ID: 0005_embeddings_and_saved_searches
Revises: 0004_corrections
Create Date: 2026-10-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005_embeddings_and_saved_searches"
down_revision: Union[str, None] = "0004_corrections"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension if available
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Add 384-d text_embedding and 512-d image_embedding to listings
    op.execute("ALTER TABLE listings ADD COLUMN IF NOT EXISTS text_embedding vector(384);")
    op.execute("ALTER TABLE listings ADD COLUMN IF NOT EXISTS image_embedding vector(512);")

    # 3. Create HNSW indexes for fast cosine similarity search
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_listings_text_embedding_hnsw
        ON listings USING hnsw (text_embedding vector_cosine_ops);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_listings_image_embedding_hnsw
        ON listings USING hnsw (image_embedding vector_cosine_ops);
        """
    )

    # 4. Create saved_searches table
    op.create_table(
        "saved_searches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("query_embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_index("ix_saved_searches_user_id", "saved_searches", ["user_id"])

    # 5. Enable RLS on saved_searches
    op.execute("ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY saved_searches_own ON saved_searches
        FOR ALL
        USING (user_id = auth.uid())
        WITH CHECK (user_id = auth.uid());
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS saved_searches_own ON saved_searches;")
    op.drop_table("saved_searches")
    op.execute("DROP INDEX IF EXISTS ix_listings_image_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS ix_listings_text_embedding_hnsw;")
    op.execute("ALTER TABLE listings DROP COLUMN IF EXISTS image_embedding;")
    op.execute("ALTER TABLE listings DROP COLUMN IF EXISTS text_embedding;")
