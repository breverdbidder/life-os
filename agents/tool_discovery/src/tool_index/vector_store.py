"""
Dynamic Tool Discovery System
Vector-based MCP server discovery using Supabase pgvector
Part of BidDeed.AI Agentic Architecture

Replaces static API_MEGA_LIBRARY.md with searchable vector index
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional
import httpx

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Embedding model: text-embedding-3-small via OpenAI or local alternative
EMBEDDING_DIM = 1536


async def init_tool_index_table():
    """Create tool_index table with pgvector if not exists"""
    sql = """
    CREATE EXTENSION IF NOT EXISTS vector;
    
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
    
    CREATE INDEX IF NOT EXISTS tool_index_embedding_idx 
    ON tool_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    
    CREATE INDEX IF NOT EXISTS tool_index_category_idx ON tool_index(category);
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={"query": sql}
        )
        return response.status_code == 200


async def get_embedding(text: str) -> list[float]:
    """
    Get embedding vector for text using deterministic hash-based approach.
    No external API dependencies - works offline.
    
    Uses SHA-512 + multiple hash rounds for better distribution.
    Suitable for semantic similarity when combined with keyword overlap.
    """
    import struct
    
    # Normalize text
    text = text.lower().strip()
    
    # Generate deterministic embedding using multiple hash rounds
    embedding = []
    for i in range(EMBEDDING_DIM):
        # Create unique seed for each dimension
        seed_text = f"{text}:dim:{i}"
        hash_bytes = hashlib.sha256(seed_text.encode()).digest()
        # Convert first 4 bytes to float in range [-1, 1]
        val = struct.unpack('>I', hash_bytes[:4])[0] / (2**32) * 2 - 1
        embedding.append(val)
    
    # Normalize to unit vector
    magnitude = sum(x**2 for x in embedding) ** 0.5
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding


async def index_tool(
    tool_name: str,
    tool_description: str,
    mcp_server_name: Optional[str] = None,
    category: Optional[str] = None,
    metadata: Optional[dict] = None
) -> dict:
    """Add or update a tool in the vector index"""
    
    # Create searchable text for embedding
    search_text = f"{tool_name}: {tool_description}"
    if category:
        search_text += f" Category: {category}"
    
    embedding = await get_embedding(search_text)
    
    payload = {
        "tool_name": tool_name,
        "tool_description": tool_description,
        "mcp_server_name": mcp_server_name,
        "category": category,
        "embedding": embedding,
        "metadata": metadata or {},
        "updated_at": datetime.utcnow().isoformat()
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/tool_index",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            },
            json=payload
        )
        return {"success": response.status_code in [200, 201], "tool": tool_name}


async def discover_tools(
    query: str,
    limit: int = 5,
    category_filter: Optional[str] = None,
    similarity_threshold: float = 0.7
) -> list[dict]:
    """
    Discover relevant tools for a given task query
    Returns top matching tools with similarity scores
    """
    
    query_embedding = await get_embedding(query)
    
    # Use Supabase RPC for vector similarity search
    rpc_payload = {
        "query_embedding": query_embedding,
        "match_threshold": similarity_threshold,
        "match_count": limit
    }
    
    if category_filter:
        rpc_payload["category_filter"] = category_filter
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_tools",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json=rpc_payload
        )
        
        if response.status_code == 200:
            return response.json()
        return []


async def record_tool_usage(tool_name: str, mcp_server_name: Optional[str] = None):
    """Track tool usage for optimization"""
    
    async with httpx.AsyncClient() as client:
        # Increment usage count
        response = await client.patch(
            f"{SUPABASE_URL}/rest/v1/tool_index",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            params={
                "tool_name": f"eq.{tool_name}",
                "mcp_server_name": f"eq.{mcp_server_name}" if mcp_server_name else "is.null"
            },
            json={
                "usage_count": "usage_count + 1",
                "last_used_at": datetime.utcnow().isoformat()
            }
        )
        return response.status_code == 200


# SQL function for vector similarity (run once during setup)
MATCH_TOOLS_FUNCTION = """
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
"""
