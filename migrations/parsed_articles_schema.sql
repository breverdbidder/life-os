-- Article Parser Schema for Life OS
-- Stores parsed articles with domain classification and summaries

CREATE TABLE IF NOT EXISTS parsed_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    domain_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    parsed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_url_parsed_at UNIQUE (url, parsed_at)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_parsed_articles_url ON parsed_articles(url);
CREATE INDEX IF NOT EXISTS idx_parsed_articles_parsed_at ON parsed_articles(parsed_at DESC);
CREATE INDEX IF NOT EXISTS idx_parsed_articles_domain_scores ON parsed_articles USING GIN (domain_scores);

-- RLS Policies (if using Row Level Security)
-- ALTER TABLE parsed_articles ENABLE ROW LEVEL SECURITY;

-- Function to get articles by domain
CREATE OR REPLACE FUNCTION get_articles_by_domain(domain_name TEXT, min_score FLOAT DEFAULT 0.1)
RETURNS TABLE (
    id UUID,
    url TEXT,
    parsed_at TIMESTAMPTZ,
    domain_score FLOAT,
    key_points TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pa.id,
        pa.url,
        pa.parsed_at,
        (pa.domain_scores->>domain_name)::FLOAT as domain_score,
        ARRAY(SELECT jsonb_array_elements_text(pa.summary->'key_points')) as key_points
    FROM parsed_articles pa
    WHERE (pa.domain_scores->>domain_name)::FLOAT >= min_score
    ORDER BY (pa.domain_scores->>domain_name)::FLOAT DESC, pa.parsed_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get recent articles across all domains
CREATE OR REPLACE FUNCTION get_recent_parsed_articles(limit_count INT DEFAULT 10)
RETURNS TABLE (
    id UUID,
    url TEXT,
    parsed_at TIMESTAMPTZ,
    primary_domain TEXT,
    primary_score FLOAT,
    word_count INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pa.id,
        pa.url,
        pa.parsed_at,
        (
            SELECT key 
            FROM jsonb_each(pa.domain_scores) 
            ORDER BY value::FLOAT DESC 
            LIMIT 1
        ) as primary_domain,
        (
            SELECT value::FLOAT 
            FROM jsonb_each(pa.domain_scores) 
            ORDER BY value::FLOAT DESC 
            LIMIT 1
        ) as primary_score,
        (pa.metadata->>'word_count')::INT as word_count
    FROM parsed_articles pa
    ORDER BY pa.parsed_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- View for business-relevant articles
CREATE OR REPLACE VIEW business_articles AS
SELECT 
    id,
    url,
    parsed_at,
    (domain_scores->>'BUSINESS')::FLOAT as business_score,
    summary->'key_points' as key_points,
    (metadata->>'reading_time')::FLOAT as reading_time_minutes
FROM parsed_articles
WHERE (domain_scores->>'BUSINESS')::FLOAT > 0.1
ORDER BY (domain_scores->>'BUSINESS')::FLOAT DESC, parsed_at DESC;

-- View for Michael D1 relevant articles
CREATE OR REPLACE VIEW michael_articles AS
SELECT 
    id,
    url,
    parsed_at,
    (domain_scores->>'MICHAEL')::FLOAT as michael_score,
    summary->'key_points' as key_points
FROM parsed_articles
WHERE (domain_scores->>'MICHAEL')::FLOAT > 0.1
ORDER BY (domain_scores->>'MICHAEL')::FLOAT DESC, parsed_at DESC;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT ON parsed_articles TO authenticated;
-- GRANT SELECT ON business_articles TO authenticated;
-- GRANT SELECT ON michael_articles TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_articles_by_domain TO authenticated;
-- GRANT EXECUTE ON FUNCTION get_recent_parsed_articles TO authenticated;

COMMENT ON TABLE parsed_articles IS 'Stores parsed articles with Life OS domain classification';
COMMENT ON FUNCTION get_articles_by_domain IS 'Retrieves articles filtered by specific Life OS domain';
COMMENT ON FUNCTION get_recent_parsed_articles IS 'Retrieves most recent parsed articles with primary domain';
