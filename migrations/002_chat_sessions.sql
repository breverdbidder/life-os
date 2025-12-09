-- Create chat_sessions table for Life OS mobile chat
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL,
    messages JSONB,
    last_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast session lookups
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC);

-- Enable RLS but allow service role full access
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- Policy for service role (API backend)
CREATE POLICY "Service role full access" ON chat_sessions
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Upsert function for updating sessions
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
