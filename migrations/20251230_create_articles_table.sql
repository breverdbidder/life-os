-- Migration: Create articles table for Article Parser Agent
-- Date: 2025-12-30
-- Author: Claude AI Architect

CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    url_hash TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author TEXT,
    publication_date TEXT,
    domain TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    content_text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    extraction_source TEXT NOT NULL,
    life_os_domain TEXT NOT NULL,
    life_os_summary TEXT NOT NULL,
    key_insights JSONB DEFAULT '[]'::jsonb,
    actionable_tasks JSONB DEFAULT '[]'::jsonb,
    relevance_score INTEGER NOT NULL CHECK (relevance_score >= 0 AND relevance_score <= 10),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_articles_url_hash ON articles(url_hash);
CREATE INDEX IF NOT EXISTS idx_articles_domain ON articles(domain);
CREATE INDEX IF NOT EXISTS idx_articles_life_os_domain ON articles(life_os_domain);
CREATE INDEX IF NOT EXISTS idx_articles_relevance_score ON articles(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_extraction_source ON articles(extraction_source);

-- Full-text search on content
CREATE INDEX IF NOT EXISTS idx_articles_content_fts ON articles USING gin(to_tsvector('english', content_text));
CREATE INDEX IF NOT EXISTS idx_articles_title_fts ON articles USING gin(to_tsvector('english', title));

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_articles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_updated_at_trigger
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_articles_updated_at();

-- Row Level Security (RLS)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
CREATE POLICY articles_all_policy ON articles
    FOR ALL
    USING (true)
    WITH CHECK (true);

COMMENT ON TABLE articles IS 'Stores parsed articles with Life OS domain analysis';
COMMENT ON COLUMN articles.url_hash IS 'MD5 hash of URL for deduplication';
COMMENT ON COLUMN articles.extraction_source IS 'trafilatura, beautifulsoup, apify_ai, or failed';
COMMENT ON COLUMN articles.life_os_domain IS 'BUSINESS, MICHAEL, FAMILY, PERSONAL, or UNCATEGORIZED';
COMMENT ON COLUMN articles.relevance_score IS 'Life OS relevance score from 1-10';
