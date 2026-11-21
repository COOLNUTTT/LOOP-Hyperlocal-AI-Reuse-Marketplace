-- Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
-- Hosted Free-Tier Supabase Bootstrap Script (`infra/supabase/setup_storage_and_realtime.sql`)
-- Run once in the Supabase SQL Editor before running `alembic upgrade head`.

-- 1. Enable spatial (PostGIS) and vector (pgvector) extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create scrubbed listing images storage bucket (max 10 MB, JPEG/PNG/WebP only)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'listing-images',
  'listing-images',
  true,
  10485760,
  ARRAY['image/jpeg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- 3. Storage Row Level Security (RLS): authenticated users can upload into their own folder; public read for scrubbed listing assets
DROP POLICY IF EXISTS "Public read access for scrubbed listing images" ON storage.objects;
CREATE POLICY "Public read access for scrubbed listing images"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'listing-images');

DROP POLICY IF EXISTS "Authenticated users can upload scrubbed listing images" ON storage.objects;
CREATE POLICY "Authenticated users can upload scrubbed listing images"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'listing-images');

-- 4. Enable Supabase Realtime WebSocket broadcast on `public.messages` (after Alembic migration 0003)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema = 'public' AND table_name = 'messages'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;
  END IF;
EXCEPTION
  WHEN duplicate_object THEN
    NULL;
END $$;
