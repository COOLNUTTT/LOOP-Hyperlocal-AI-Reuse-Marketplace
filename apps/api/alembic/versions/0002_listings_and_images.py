# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Create listings and listing_images tables with Row Level Security.

Revision ID: 0002_listings_and_images
Revises: 0001_identity_and_rls
Create Date: 2026-10-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_listings_and_images"
down_revision: Union[str, None] = "0001_identity_and_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create listings table
    op.create_table(
        "listings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "seller_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "community_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("communities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("type", sa.String(length=20), nullable=False, server_default=sa.text("'sell'")),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subtype", sa.String(length=100), nullable=True),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("condition", sa.String(length=20), nullable=False),
        sa.Column("condition_ai", sa.String(length=20), nullable=True),
        sa.Column("condition_conf", sa.Float(), nullable=True),
        sa.Column("price_ask", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_low", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_likely", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_high", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("price_ai_likely", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("fair_deal", sa.String(length=20), nullable=True),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("area_name", sa.String(length=100), nullable=False),
        sa.Column("geohash5", sa.String(length=5), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("views", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("saves", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("data_origin", sa.String(length=20), nullable=False, server_default=sa.text("'real'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_listings_seller_id", "listings", ["seller_id"])
    op.create_index("ix_listings_community_id", "listings", ["community_id"])
    op.create_index("ix_listings_category", "listings", ["category"])
    op.create_index("ix_listings_geohash5", "listings", ["geohash5"])
    op.create_index("ix_listings_status", "listings", ["status"])
    op.create_index("ix_listings_created_at", "listings", ["created_at"])
    op.create_index("ix_listings_status_category_created", "listings", ["status", "category", "created_at"])

    # 2. Create listing_images table
    op.create_table(
        "listing_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "listing_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("listings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("scrub_boxes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("scrubbed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("phash", sa.Numeric(precision=20, scale=0), nullable=True),
        sa.Column("heatmap_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_listing_images_listing_id", "listing_images", ["listing_id"])
    op.create_index("ix_listing_images_phash", "listing_images", ["phash"])

    # 3. Enable RLS
    op.execute("ALTER TABLE listings ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE listing_images ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE listings FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE listing_images FORCE ROW LEVEL SECURITY;")

    # 4. Policies for listings
    # Active listings viewable by all authenticated users; drafts/reserved/completed viewable by owner
    op.execute("""
        CREATE POLICY "Active listings viewable by all authenticated users"
        ON listings FOR SELECT
        USING (
            status = 'active'
            OR (auth.role() = 'authenticated' AND auth.uid() IN (SELECT auth_uid FROM users WHERE id = seller_id))
        );
    """)
    op.execute("""
        CREATE POLICY "Sellers can insert listings"
        ON listings FOR INSERT
        WITH CHECK (auth.uid() IN (SELECT auth_uid FROM users WHERE id = seller_id));
    """)
    op.execute("""
        CREATE POLICY "Sellers can update their own listings"
        ON listings FOR UPDATE
        USING (auth.uid() IN (SELECT auth_uid FROM users WHERE id = seller_id));
    """)
    op.execute("""
        CREATE POLICY "Sellers can delete their own listings"
        ON listings FOR DELETE
        USING (auth.uid() IN (SELECT auth_uid FROM users WHERE id = seller_id));
    """)

    # 5. Policies for listing_images
    op.execute("""
        CREATE POLICY "Listing images viewable for viewable listings"
        ON listing_images FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM listings l
                WHERE l.id = listing_images.listing_id
                AND (
                    l.status = 'active'
                    OR (auth.role() = 'authenticated' AND auth.uid() IN (SELECT auth_uid FROM users WHERE id = l.seller_id))
                )
            )
        );
    """)
    op.execute("""
        CREATE POLICY "Sellers can insert listing images"
        ON listing_images FOR INSERT
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM listings l
                WHERE l.id = listing_images.listing_id
                AND auth.uid() IN (SELECT auth_uid FROM users WHERE id = l.seller_id)
            )
        );
    """)
    op.execute("""
        CREATE POLICY "Sellers can update their listing images"
        ON listing_images FOR UPDATE
        USING (
            EXISTS (
                SELECT 1 FROM listings l
                WHERE l.id = listing_images.listing_id
                AND auth.uid() IN (SELECT auth_uid FROM users WHERE id = l.seller_id)
            )
        );
    """)
    op.execute("""
        CREATE POLICY "Sellers can delete their listing images"
        ON listing_images FOR DELETE
        USING (
            EXISTS (
                SELECT 1 FROM listings l
                WHERE l.id = listing_images.listing_id
                AND auth.uid() IN (SELECT auth_uid FROM users WHERE id = l.seller_id)
            )
        );
    """)


def downgrade() -> None:
    op.drop_table("listing_images")
    op.drop_table("listings")
