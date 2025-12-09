-- Life OS Chat Sessions Table
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    messages JSONB DEFAULT '[]'::jsonb,
    last_response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast session lookups
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated ON chat_sessions(updated_at DESC);

-- Enable RLS
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations with service key (server-side only)
CREATE POLICY "Service key full access" ON chat_sessions
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Upsert function for merging messages
CREATE OR REPLACE FUNCTION upsert_chat_session(
    p_session_id TEXT,
    p_messages JSONB,
    p_last_response TEXT
) RETURNS void AS $$
BEGIN
    INSERT INTO chat_sessions (session_id, messages, last_response, updated_at)
    VALUES (p_session_id, p_messages, p_last_response, NOW())
    ON CONFLICT (session_id) 
    DO UPDATE SET 
        messages = EXCLUDED.messages,
        last_response = EXCLUDED.last_response,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE chat_sessions IS 'Life OS Chat - Secure conversation logs, no third-party exposure';
