-- Create chat_sessions table for Life OS mobile chat
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    messages JSONB,
    last_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast session lookups
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC);

-- GIN index for JSONB messages (fast queries inside message content)
CREATE INDEX IF NOT EXISTS idx_chat_sessions_messages_gin ON chat_sessions USING GIN (messages);

-- Enable RLS but allow service role full access
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- Policy for service role (API backend)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Service role full access' AND tablename = 'chat_sessions') THEN
        CREATE POLICY "Service role full access" ON chat_sessions
            FOR ALL
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;
