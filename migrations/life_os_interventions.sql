-- Life OS Interventions Table
-- Tracks ADHD interventions triggered by RSS feed monitoring
-- V1.0 - 2026-01-04

CREATE TABLE IF NOT EXISTS life_os_interventions (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Task reference
    task_id TEXT NOT NULL,
    task_description TEXT NOT NULL,
    task_status TEXT NOT NULL CHECK (task_status IN ('ABANDONED', 'BLOCKED', 'DEFERRED')),
    domain TEXT NOT NULL CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'ARIEL')),
    
    -- Intervention details
    intervention_type TEXT NOT NULL DEFAULT 'RSS_ALERT' CHECK (intervention_type IN ('RSS_ALERT', 'MANUAL', 'SCHEDULED', 'PATTERN_DETECTED')),
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Resolution tracking
    resolution_status TEXT NOT NULL DEFAULT 'OPEN' CHECK (resolution_status IN ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED')),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_interventions_task_id ON life_os_interventions(task_id);
CREATE INDEX IF NOT EXISTS idx_interventions_status ON life_os_interventions(resolution_status);
CREATE INDEX IF NOT EXISTS idx_interventions_triggered ON life_os_interventions(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_interventions_domain ON life_os_interventions(domain);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_life_os_interventions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_life_os_interventions_timestamp
    BEFORE UPDATE ON life_os_interventions
    FOR EACH ROW
    EXECUTE FUNCTION update_life_os_interventions_updated_at();

-- Row Level Security (RLS)
ALTER TABLE life_os_interventions ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations with service role key
CREATE POLICY "Allow service role full access"
    ON life_os_interventions
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Analytics view: Daily intervention summary
CREATE OR REPLACE VIEW daily_intervention_summary AS
SELECT 
    DATE(triggered_at) as intervention_date,
    domain,
    task_status,
    COUNT(*) as intervention_count,
    COUNT(*) FILTER (WHERE resolution_status = 'RESOLVED') as resolved_count,
    COUNT(*) FILTER (WHERE resolution_status = 'OPEN') as open_count,
    ROUND(
        COUNT(*) FILTER (WHERE resolution_status = 'RESOLVED')::NUMERIC / 
        COUNT(*)::NUMERIC * 100, 
        1
    ) as resolution_rate_percent
FROM life_os_interventions
GROUP BY DATE(triggered_at), domain, task_status
ORDER BY intervention_date DESC, intervention_count DESC;

-- Analytics view: Intervention patterns (ADHD insights)
CREATE OR REPLACE VIEW intervention_patterns AS
SELECT 
    domain,
    task_status,
    COUNT(*) as total_interventions,
    COUNT(DISTINCT task_id) as unique_tasks,
    AVG(EXTRACT(EPOCH FROM (resolved_at - triggered_at)) / 3600) as avg_resolution_hours,
    MAX(triggered_at) as last_intervention
FROM life_os_interventions
WHERE triggered_at >= NOW() - INTERVAL '30 days'
GROUP BY domain, task_status
ORDER BY total_interventions DESC;

-- Sample queries for monitoring
COMMENT ON TABLE life_os_interventions IS 
'Tracks ADHD interventions from RSS feed monitoring. 
Example queries:
- Open interventions: SELECT * FROM life_os_interventions WHERE resolution_status = ''OPEN'';
- Today''s summary: SELECT * FROM daily_intervention_summary WHERE intervention_date = CURRENT_DATE;
- Patterns: SELECT * FROM intervention_patterns;
- High abandonment days: SELECT intervention_date, SUM(intervention_count) FROM daily_intervention_summary GROUP BY intervention_date HAVING SUM(intervention_count) > 3;';
