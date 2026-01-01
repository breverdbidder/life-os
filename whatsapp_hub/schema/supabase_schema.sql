-- WhatsApp Hub - Supabase Database Schema
-- Repository: github.com/breverdbidder/life-os
-- Created: January 1, 2026

-- ============================================================================
-- DROP EXISTING TABLES (for clean deployment)
-- ============================================================================

DROP TABLE IF EXISTS processing_logs CASCADE;
DROP TABLE IF EXISTS whatsapp_media CASCADE;
DROP TABLE IF EXISTS whatsapp_links CASCADE;
DROP TABLE IF EXISTS whatsapp_messages CASCADE;
DROP TABLE IF EXISTS whatsapp_groups CASCADE;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Groups table: Metadata about WhatsApp group chats
CREATE TABLE whatsapp_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    export_date TIMESTAMP NOT NULL,
    message_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    storage_path TEXT, -- Path to uploaded files in Supabase Storage
    processing_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table: All WhatsApp messages
CREATE TABLE whatsapp_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID NOT NULL REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    sender TEXT NOT NULL,
    message_text TEXT,
    is_system_message BOOLEAN DEFAULT FALSE,
    reply_to_message_id UUID REFERENCES whatsapp_messages(id) ON DELETE SET NULL,
    has_media BOOLEAN DEFAULT FALSE,
    has_links BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Links table: Extracted URLs from messages
CREATE TABLE whatsapp_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES whatsapp_messages(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    display_url TEXT, -- Shortened/display version
    page_title TEXT,
    preview_image_url TEXT,
    domain TEXT,
    shared_by TEXT NOT NULL,
    shared_at TIMESTAMP NOT NULL,
    share_count INTEGER DEFAULT 1, -- How many times this URL was shared
    created_at TIMESTAMP DEFAULT NOW()
);

-- Media table: Attachments metadata
CREATE TABLE whatsapp_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES whatsapp_messages(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    media_type TEXT NOT NULL, -- 'image', 'video', 'document', 'audio'
    file_size BIGINT,
    mime_type TEXT,
    storage_url TEXT NOT NULL, -- Supabase Storage URL
    thumbnail_url TEXT, -- For images/videos
    width INTEGER, -- For images/videos
    height INTEGER, -- For images/videos
    duration INTEGER, -- For videos/audio (seconds)
    uploaded_by TEXT NOT NULL,
    uploaded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Processing logs: Audit trail for ETL pipeline
CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id UUID REFERENCES whatsapp_groups(id) ON DELETE CASCADE,
    stage TEXT NOT NULL, -- 'upload', 'parse', 'links', 'media', 'sync'
    status TEXT NOT NULL, -- 'started', 'completed', 'failed'
    details JSONB,
    error_message TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Messages indexes
CREATE INDEX idx_messages_group_timestamp ON whatsapp_messages(group_id, timestamp DESC);
CREATE INDEX idx_messages_sender ON whatsapp_messages(sender);
CREATE INDEX idx_messages_has_media ON whatsapp_messages(has_media) WHERE has_media = TRUE;
CREATE INDEX idx_messages_has_links ON whatsapp_messages(has_links) WHERE has_links = TRUE;

-- Full-text search on message content
CREATE INDEX idx_messages_search ON whatsapp_messages 
    USING gin(to_tsvector('english', message_text));

-- Links indexes
CREATE INDEX idx_links_url ON whatsapp_links(url);
CREATE INDEX idx_links_domain ON whatsapp_links(domain);
CREATE INDEX idx_links_shared_at ON whatsapp_links(shared_at DESC);
CREATE INDEX idx_links_message ON whatsapp_links(message_id);

-- Media indexes
CREATE INDEX idx_media_type ON whatsapp_media(media_type);
CREATE INDEX idx_media_message ON whatsapp_media(message_id);
CREATE INDEX idx_media_uploaded_at ON whatsapp_media(uploaded_at DESC);

-- Processing logs indexes
CREATE INDEX idx_logs_group ON processing_logs(group_id);
CREATE INDEX idx_logs_stage_status ON processing_logs(stage, status);
CREATE INDEX idx_logs_created ON processing_logs(created_at DESC);

-- Groups indexes
CREATE INDEX idx_groups_status ON whatsapp_groups(processing_status);
CREATE INDEX idx_groups_created ON whatsapp_groups(created_at DESC);

-- ============================================================================
-- CUSTOM FUNCTIONS
-- ============================================================================

-- Function: Search messages with full-text search
CREATE OR REPLACE FUNCTION search_messages(
    search_query TEXT,
    group_filter UUID DEFAULT NULL,
    limit_count INTEGER DEFAULT 50
)
RETURNS TABLE (
    message_id UUID,
    group_id UUID,
    group_name TEXT,
    sender TEXT,
    message_text TEXT,
    timestamp TIMESTAMP,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id AS message_id,
        m.group_id,
        g.name AS group_name,
        m.sender,
        m.message_text,
        m.timestamp,
        ts_rank(to_tsvector('english', m.message_text), 
                plainto_tsquery('english', search_query)) AS rank
    FROM whatsapp_messages m
    JOIN whatsapp_groups g ON m.group_id = g.id
    WHERE 
        to_tsvector('english', m.message_text) @@ plainto_tsquery('english', search_query)
        AND (group_filter IS NULL OR m.group_id = group_filter)
    ORDER BY rank DESC, m.timestamp DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Get group statistics
CREATE OR REPLACE FUNCTION get_group_stats(group_uuid UUID)
RETURNS TABLE (
    total_messages BIGINT,
    total_links BIGINT,
    total_media BIGINT,
    unique_senders BIGINT,
    date_range_start TIMESTAMP,
    date_range_end TIMESTAMP,
    messages_per_day NUMERIC,
    top_senders JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT 
            COUNT(DISTINCT m.id) AS msg_count,
            COUNT(DISTINCT l.id) AS link_count,
            COUNT(DISTINCT med.id) AS media_count,
            COUNT(DISTINCT m.sender) AS sender_count,
            MIN(m.timestamp) AS min_date,
            MAX(m.timestamp) AS max_date
        FROM whatsapp_messages m
        LEFT JOIN whatsapp_links l ON l.message_id = m.id
        LEFT JOIN whatsapp_media med ON med.message_id = m.id
        WHERE m.group_id = group_uuid
    ),
    top_senders_data AS (
        SELECT jsonb_agg(
            jsonb_build_object(
                'sender', sender,
                'message_count', msg_count
            )
        ) AS senders_json
        FROM (
            SELECT sender, COUNT(*) AS msg_count
            FROM whatsapp_messages
            WHERE group_id = group_uuid
            GROUP BY sender
            ORDER BY msg_count DESC
            LIMIT 10
        ) sub
    )
    SELECT 
        s.msg_count,
        s.link_count,
        s.media_count,
        s.sender_count,
        s.min_date,
        s.max_date,
        CASE 
            WHEN s.max_date > s.min_date 
            THEN s.msg_count::NUMERIC / GREATEST(EXTRACT(EPOCH FROM (s.max_date - s.min_date)) / 86400, 1)
            ELSE 0
        END AS messages_per_day,
        COALESCE(ts.senders_json, '[]'::jsonb) AS top_senders
    FROM stats s
    CROSS JOIN top_senders_data ts;
END;
$$ LANGUAGE plpgsql;

-- Function: Update group statistics (trigger-based)
CREATE OR REPLACE FUNCTION update_group_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE whatsapp_groups
    SET 
        message_count = (
            SELECT COUNT(*) 
            FROM whatsapp_messages 
            WHERE group_id = NEW.group_id
        ),
        participant_count = (
            SELECT COUNT(DISTINCT sender) 
            FROM whatsapp_messages 
            WHERE group_id = NEW.group_id
        ),
        date_range_start = (
            SELECT MIN(timestamp) 
            FROM whatsapp_messages 
            WHERE group_id = NEW.group_id
        ),
        date_range_end = (
            SELECT MAX(timestamp) 
            FROM whatsapp_messages 
            WHERE group_id = NEW.group_id
        ),
        updated_at = NOW()
    WHERE id = NEW.group_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update group stats on message insert
CREATE TRIGGER trigger_update_group_stats
AFTER INSERT ON whatsapp_messages
FOR EACH ROW
EXECUTE FUNCTION update_group_stats();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE whatsapp_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE whatsapp_media ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own data
-- Note: Requires auth.uid() which is set by Supabase authentication
-- For now, allowing all access (update with auth.uid() when implementing user auth)

CREATE POLICY "Allow all access to groups" ON whatsapp_groups
    FOR ALL USING (true);

CREATE POLICY "Allow all access to messages" ON whatsapp_messages
    FOR ALL USING (true);

CREATE POLICY "Allow all access to links" ON whatsapp_links
    FOR ALL USING (true);

CREATE POLICY "Allow all access to media" ON whatsapp_media
    FOR ALL USING (true);

CREATE POLICY "Allow all access to logs" ON processing_logs
    FOR ALL USING (true);

-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- View: Daily message activity across all groups
CREATE MATERIALIZED VIEW mv_daily_activity AS
SELECT 
    DATE(timestamp) AS activity_date,
    group_id,
    COUNT(*) AS message_count,
    COUNT(DISTINCT sender) AS active_senders,
    SUM(CASE WHEN has_links THEN 1 ELSE 0 END) AS messages_with_links,
    SUM(CASE WHEN has_media THEN 1 ELSE 0 END) AS messages_with_media
FROM whatsapp_messages
GROUP BY DATE(timestamp), group_id;

CREATE INDEX idx_daily_activity ON mv_daily_activity(activity_date DESC, group_id);

-- View: Top shared domains
CREATE MATERIALIZED VIEW mv_top_domains AS
SELECT 
    domain,
    COUNT(*) AS share_count,
    COUNT(DISTINCT message_id) AS unique_shares,
    MAX(shared_at) AS last_shared
FROM whatsapp_links
WHERE domain IS NOT NULL
GROUP BY domain
ORDER BY share_count DESC;

CREATE INDEX idx_top_domains ON mv_top_domains(share_count DESC);

-- View: Media summary by type
CREATE MATERIALIZED VIEW mv_media_summary AS
SELECT 
    media_type,
    COUNT(*) AS file_count,
    SUM(file_size) AS total_size_bytes,
    AVG(file_size) AS avg_size_bytes,
    MAX(uploaded_at) AS last_upload
FROM whatsapp_media
GROUP BY media_type;

CREATE INDEX idx_media_summary ON mv_media_summary(media_type);

-- ============================================================================
-- REFRESH MATERIALIZED VIEWS (run daily via cron or manually)
-- ============================================================================

-- Run this to refresh analytics:
-- REFRESH MATERIALIZED VIEW mv_daily_activity;
-- REFRESH MATERIALIZED VIEW mv_top_domains;
-- REFRESH MATERIALIZED VIEW mv_media_summary;

-- ============================================================================
-- STORAGE BUCKETS (create via Supabase Dashboard or CLI)
-- ============================================================================

-- Storage bucket: whatsapp-uploads (for user uploads - chat.txt + media folder)
-- Storage bucket: whatsapp-media (for processed media files)

-- To create via SQL (requires Supabase extensions):
-- INSERT INTO storage.buckets (id, name, public) VALUES ('whatsapp-uploads', 'whatsapp-uploads', false);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('whatsapp-media', 'whatsapp-media', false);

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample group
INSERT INTO whatsapp_groups (name, export_date, processing_status)
VALUES ('Family Chat', '2026-01-01 10:00:00', 'pending');

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    deployed_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO schema_version (version) VALUES ('1.0.0');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
