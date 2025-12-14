#!/usr/bin/env python3
"""
Initialize Supabase tables for Agentic Tool Discovery System
Run once during setup or when schema changes needed
"""

import os
import asyncio
import httpx

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

INIT_SQL = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tool Index Table (for dynamic discovery)
CREATE TABLE IF NOT EXISTS tool_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name TEXT NOT NULL,
    tool_description TEXT NOT NULL,
    mcp_server_name TEXT,
    category TEXT,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tool_name, mcp_server_name)
);

-- Token Metrics Table (for economics tracking)
CREATE TABLE IF NOT EXISTS token_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL,
    workflow_name TEXT NOT NULL,
    phase TEXT NOT NULL CHECK (phase IN ('exploration', 'production')),
    model TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cached_tokens INTEGER DEFAULT 0,
    tool_calls INTEGER DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    cost_usd NUMERIC(10, 6),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Extracted Skills Table (for skill extraction)
CREATE TABLE IF NOT EXISTS extracted_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_name TEXT NOT NULL UNIQUE,
    description TEXT,
    trigger_patterns JSONB DEFAULT '[]',
    tool_sequence JSONB DEFAULT '[]',
    input_schema JSONB DEFAULT '{}',
    output_schema JSONB DEFAULT '{}',
    success_criteria TEXT,
    source_chat_id TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS tool_index_category_idx ON tool_index(category);
CREATE INDEX IF NOT EXISTS tool_index_usage_idx ON tool_index(usage_count DESC);
CREATE INDEX IF NOT EXISTS token_metrics_workflow_idx ON token_metrics(workflow_id);
CREATE INDEX IF NOT EXISTS token_metrics_phase_idx ON token_metrics(phase);
CREATE INDEX IF NOT EXISTS token_metrics_created_idx ON token_metrics(created_at DESC);
CREATE INDEX IF NOT EXISTS extracted_skills_name_idx ON extracted_skills(skill_name);

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_tools(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5,
    category_filter text DEFAULT NULL
)
RETURNS TABLE (
    tool_name text,
    tool_description text,
    mcp_server_name text,
    category text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ti.tool_name,
        ti.tool_description,
        ti.mcp_server_name,
        ti.category,
        ti.metadata,
        1 - (ti.embedding <=> query_embedding) AS similarity
    FROM tool_index ti
    WHERE 
        (category_filter IS NULL OR ti.category = category_filter)
        AND 1 - (ti.embedding <=> query_embedding) > match_threshold
    ORDER BY ti.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- IVFFlat index for vector search (requires data to exist first)
-- Run after seeding: CREATE INDEX tool_index_embedding_idx ON tool_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
"""


async def init_tables():
    """Execute initialization SQL"""
    
    if not SUPABASE_KEY:
        print("❌ SUPABASE_KEY not set")
        return False
    
    # Split SQL into statements and execute via REST API
    # Note: Supabase doesn't allow raw SQL via REST, so we use individual table creates
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check connection first
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Supabase connection failed: {response.status_code}")
            return False
        
        print("✅ Supabase connection verified")
        
        # For table creation, we need to use Supabase SQL Editor or migrations
        # The REST API doesn't support DDL
        print("\n📋 SQL to run in Supabase SQL Editor:")
        print("-" * 50)
        print(INIT_SQL)
        print("-" * 50)
        print("\n⚠️  Copy the SQL above and run it in:")
        print(f"   {SUPABASE_URL.replace('.supabase.co', '')}/project/default/sql")
        
        return True


if __name__ == "__main__":
    asyncio.run(init_tables())
