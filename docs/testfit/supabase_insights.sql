-- Supabase insights table inserts
-- Generated: 2026-01-09T12:25:41.979787


INSERT INTO insights (
    category,
    source,
    system,
    insight_type,
    title,
    summary,
    metadata,
    tags,
    created_at
) VALUES (
    'competitive_intelligence',
    'testfit_analysis',
    'biddeed_ai',
    'enhancement_plan',
    'BidDeed.AI Pipeline Improvements from TestFit',
    'Transform from single-path to multi-scenario exploration. Key improvements: Stage 8 (Generative Bid Strategy - 100 scenarios), Stage 4 (Interactive Lien Scenarios), Stage 10 (Interactive HTML Reports)',
    '{"investment": "$58K, 29 weeks", "roi": "+400%", "priority": "HIGH", "status": "planned", "github_url": "https://github.com/breverdbidder/brevard-bidder-scraper/blob/main/docs/enhancements/BidDeed_Pipeline_Improvements.md", "next_steps": "Start Stage 8 (Generative Bid Strategy Engine)"}'::jsonb,
    ARRAY['testfit', 'generative-intelligence', 'multi-scenario', 'foreclosure'],
    '2026-01-09T12:25:41.979018'
);

INSERT INTO insights (
    category,
    source,
    system,
    insight_type,
    title,
    summary,
    metadata,
    tags,
    created_at
) VALUES (
    'competitive_intelligence',
    'testfit_analysis',
    'spd',
    'enhancement_plan',
    'SPD Pipeline Improvements from TestFit',
    'Clone TestFit''s generative design core (1,000 layouts in 60 seconds) + add automated permitting. Key improvement: Stage 4 (Generative Design Engine) - THIS IS THE PRODUCT',
    '{"investment": "$129K, 43 weeks", "roi": "+815%", "priority": "CRITICAL", "status": "planned", "github_url": "https://github.com/breverdbidder/spd-site-plan-dev/blob/main/docs/enhancements/SPD_Pipeline_Improvements.md", "competitive_advantage": "TestFit doesn't do permitting - SPD will", "next_steps": "Start Stage 4 (Generative Design Engine) - 12 weeks"}'::jsonb,
    ARRAY['testfit', 'direct-competitor', 'generative-design', 'site-planning', '$22M-market'],
    '2026-01-09T12:25:41.979031'
);

INSERT INTO insights (
    category,
    source,
    system,
    insight_type,
    title,
    summary,
    metadata,
    tags,
    created_at
) VALUES (
    'competitive_intelligence',
    'testfit_analysis',
    'zoning_analyst',
    'enhancement_plan',
    'Zoning Analyst Enhancements from TestFit',
    'Real-time compliance validation (<1 second) + generative scenarios (1,000 designs). Transform from static scraper to interactive compliance system. 75% Firecrawl cost savings.',
    '{"investment": "$24K, 12 weeks", "roi": "+525%", "cost_savings": "$4,488/year (Firecrawl reduction)", "priority": "HIGH", "status": "planned", "github_url": "https://github.com/breverdbidder/spd-site-plan-dev/blob/main/docs/enhancements/Zoning_Analyst_Enhancements.md", "relationship": "Foundation for SPD Stage 2", "next_steps": "Phase 1: Real-time validator (4 weeks)"}'::jsonb,
    ARRAY['testfit', 'real-time-validation', 'zoning', 'firecrawl-optimization'],
    '2026-01-09T12:25:41.979033'
);

INSERT INTO insights (
    category,
    source,
    system,
    insight_type,
    title,
    summary,
    metadata,
    tags,
    created_at
) VALUES (
    'competitive_intelligence',
    'testfit_analysis',
    'all_systems',
    'strategic_plan',
    'Master Summary: Three Systems TestFit Enhancement',
    'Complete competitive intelligence → implementation cycle for 3 agentic AI systems. TestFit''s lesson: Generative Intelligence beats single recommendations. Generate 1,000 options, let users explore.',
    '{"total_investment": "$211K, 22 months", "total_roi": "+1,740%", "total_value": "$8.25M (5 years)", "recommended_approach": "Sequential: BidDeed.AI (7mo) \u2192 Zoning Analyst (3mo) \u2192 SPD (12mo)", "priority": "STRATEGIC", "status": "planned", "github_url": "https://github.com/breverdbidder/life-os/blob/main/docs/testfit/MASTER_SUMMARY.md", "break_even": "Month 16"}'::jsonb,
    ARRAY['testfit', 'master-plan', 'three-systems', 'strategic'],
    '2026-01-09T12:25:41.979036'
);
