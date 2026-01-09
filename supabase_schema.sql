-- Capacity Compliance Table
-- Tracks Claude's token usage and violations of the 80% rule

CREATE TABLE IF NOT EXISTS capacity_compliance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tokens_used INTEGER NOT NULL,
    capacity INTEGER NOT NULL DEFAULT 1000000,
    usage_percent DECIMAL(5,2) NOT NULL,
    threshold_percent DECIMAL(5,2) NOT NULL DEFAULT 80.00,
    claimed_limitation BOOLEAN NOT NULL,
    is_violation BOOLEAN NOT NULL,
    violation_severity TEXT CHECK (violation_severity IN ('SEVERE', 'HIGH', 'MEDIUM', 'LOW')),
    conversation_id TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Indexes for fast queries
    INDEX idx_violations ON capacity_compliance(is_violation) WHERE is_violation = true,
    INDEX idx_timestamp ON capacity_compliance(timestamp DESC),
    INDEX idx_severity ON capacity_compliance(violation_severity) WHERE violation_severity IS NOT NULL
);

-- Enable Row Level Security
ALTER TABLE capacity_compliance ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role full access" ON capacity_compliance
    FOR ALL
    USING (auth.role() = 'service_role');

-- View for violation summary
CREATE OR REPLACE VIEW capacity_violations_summary AS
SELECT 
    COUNT(*) as total_violations,
    COUNT(*) FILTER (WHERE violation_severity = 'SEVERE') as severe_count,
    COUNT(*) FILTER (WHERE violation_severity = 'HIGH') as high_count,
    COUNT(*) FILTER (WHERE violation_severity = 'MEDIUM') as medium_count,
    COUNT(*) FILTER (WHERE violation_severity = 'LOW') as low_count,
    AVG(usage_percent) as avg_usage_when_violated,
    MIN(usage_percent) as worst_violation_usage,
    MAX(timestamp) as last_violation
FROM capacity_compliance
WHERE is_violation = true;

-- Comment the table
COMMENT ON TABLE capacity_compliance IS 'Tracks Claude Sonnet 4.5 capacity usage and violations of the 80% rule';
COMMENT ON COLUMN capacity_compliance.violation_severity IS 'SEVERE: <20%, HIGH: 20-40%, MEDIUM: 40-60%, LOW: 60-80%';
