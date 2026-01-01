-- WhatsApp Data Hub - Supabase Schema
-- Created: 2025-01-01
-- Repository: life-os/whatsapp_hub

-- ============================================================
-- TABLE: whatsapp_groups
-- Stores information about each WhatsApp group chat
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_name TEXT NOT NULL,
    group_identifier TEXT UNIQUE, -- Derived from export filename or user-provided
    export_date TIMESTAMPTZ,
    total_messages INTEGER DEFAULT 0,
    total_participants INTEGER DEFAULT 0,
    date_range_start TIMESTAMPTZ,
    date_range_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- Store additional info like participants list, description
);

CREATE INDEX idx_whatsapp_groups_identifier ON whatsapp_groups(group_identifier);
CREATE INDEX idx_whatsapp_groups_created ON whatsapp_groups(created_at);

-- ============================================================
-- TABLE: whatsapp_messages
-- Stores individual messages from group chats
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    message_timestamp TIMESTAMPTZ NOT NULL,
    sender_name TEXT NOT NULL,
    sender_phone TEXT, -- If available from export
    message_text TEXT,
    message_type TEXT DEFAULT 'text', -- text, image, video, audio, document, link, system
    is_reply BOOLEAN DEFAULT FALSE,
    reply_to_sender TEXT,
    media_filename TEXT, -- Original filename from WhatsApp
    has_media BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- Store emojis, reactions, formatting, etc.
);

CREATE INDEX idx_whatsapp_messages_group ON whatsapp_messages(group_id);
CREATE INDEX idx_whatsapp_messages_timestamp ON whatsapp_messages(message_timestamp);
CREATE INDEX idx_whatsapp_messages_sender ON whatsapp_messages(sender_name);
CREATE INDEX idx_whatsapp_messages_type ON whatsapp_messages(message_type);

-- ============================================================
-- TABLE: whatsapp_links
-- Extracted URLs from messages with metadata
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES whatsapp_messages(id) ON DELETE CASCADE,
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    url_domain TEXT,
    url_title TEXT, -- Fetched via web scraping
    url_description TEXT,
    url_preview_image TEXT, -- URL to preview image if available
    shared_by TEXT NOT NULL,
    shared_at TIMESTAMPTZ NOT NULL,
    share_count INTEGER DEFAULT 1, -- Track if URL shared multiple times
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- Store HTTP headers, redirect chains, etc.
);

CREATE INDEX idx_whatsapp_links_group ON whatsapp_links(group_id);
CREATE INDEX idx_whatsapp_links_url ON whatsapp_links(url);
CREATE INDEX idx_whatsapp_links_domain ON whatsapp_links(url_domain);
CREATE INDEX idx_whatsapp_links_shared_at ON whatsapp_links(shared_at);

-- ============================================================
-- TABLE: whatsapp_attachments
-- Downloaded and processed media files
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES whatsapp_messages(id) ON DELETE CASCADE,
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    file_type TEXT NOT NULL, -- image, video, audio, document, other
    file_extension TEXT,
    file_size_bytes BIGINT,
    mime_type TEXT,
    storage_path TEXT, -- Supabase storage path
    storage_url TEXT, -- Public URL if applicable
    thumbnail_path TEXT, -- For images/videos
    duration_seconds INTEGER, -- For audio/video
    width INTEGER, -- For images/videos
    height INTEGER, -- For images/videos
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- EXIF data, video codec, audio bitrate, etc.
);

CREATE INDEX idx_whatsapp_attachments_group ON whatsapp_attachments(group_id);
CREATE INDEX idx_whatsapp_attachments_type ON whatsapp_attachments(file_type);
CREATE INDEX idx_whatsapp_attachments_uploaded_at ON whatsapp_attachments(uploaded_at);
CREATE INDEX idx_whatsapp_attachments_message ON whatsapp_attachments(message_id);

-- ============================================================
-- TABLE: whatsapp_processing_jobs
-- Track export processing status
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    job_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    job_type TEXT DEFAULT 'full_export', -- full_export, incremental, reprocess
    total_messages_processed INTEGER DEFAULT 0,
    total_links_extracted INTEGER DEFAULT 0,
    total_attachments_processed INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB -- Processing stats, agent logs, etc.
);

CREATE INDEX idx_whatsapp_processing_jobs_status ON whatsapp_processing_jobs(job_status);
CREATE INDEX idx_whatsapp_processing_jobs_group ON whatsapp_processing_jobs(group_id);

-- ============================================================
-- TABLE: whatsapp_insights
-- Generated insights and analytics
-- ============================================================
CREATE TABLE IF NOT EXISTS whatsapp_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL, -- top_senders, most_shared_links, peak_activity_times, etc.
    insight_data JSONB NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_whatsapp_insights_group ON whatsapp_insights(group_id);
CREATE INDEX idx_whatsapp_insights_type ON whatsapp_insights(insight_type);

-- ============================================================
-- STORAGE BUCKETS
-- Define Supabase storage buckets for attachments
-- ============================================================
-- Run this via Supabase dashboard or client:
-- 
-- INSERT INTO storage.buckets (id, name, public) 
-- VALUES ('whatsapp-attachments', 'whatsapp-attachments', false);
-- 
-- Storage policies will be created to restrict access appropriately

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- Basic RLS policies - adjust based on access requirements
-- ============================================================
ALTER TABLE whatsapp_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_insights ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read all data
-- Adjust these policies based on your auth setup
CREATE POLICY "Allow authenticated read access" ON whatsapp_groups
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated read access" ON whatsapp_messages
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated read access" ON whatsapp_links
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated read access" ON whatsapp_attachments
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated read access" ON whatsapp_processing_jobs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated read access" ON whatsapp_insights
    FOR SELECT TO authenticated USING (true);

-- Allow service role full access for agent processing
-- This will be used by GitHub Actions with service role key
