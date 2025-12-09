// Life OS Chat API - Vercel Serverless Function
// Proxies requests to Anthropic API - API key stays server-side

export default async function handler(req, res) {
  // CORS headers for your domain
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Simple auth check - password in request must match env var
  const { password, messages, session_id } = req.body;
  
  if (password !== process.env.LIFE_OS_PASSWORD) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Messages array required' });
  }

  const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
  
  if (!ANTHROPIC_API_KEY) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  // System prompt with Life OS context
  const systemPrompt = `You are Claude, integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Dual timezone: FL (America/New_York) | IL (Asia/Jerusalem)
- Family: Wife Mariam, Son Michael (16, D1 swimmer)
- Style: Direct, no softening language, action-oriented

DOMAINS:
1. BUSINESS: Foreclosure auctions, BrevardBidderAI V13.4.0, insurance agencies
2. MICHAEL D1 SWIMMING: Events (50/100/200 Free, 100 Fly, 100 Back), Keto M-Th, moderate F-Su
3. FAMILY: Orthodox observance, Shabbat, holidays
4. ARIEL PERSONAL: Health, learning, productivity

ADHD RULES:
- Track task states: INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED
- Detect abandonment: context switches, incomplete tasks
- Intervene with micro-commitments and chunking
- No softening, celebrate completions with facts

BREVARD BIDDER AI:
- 12-stage pipeline: Discovery→Scraping→Title→Lien Priority→Tax Certs→Demographics→ML Score→Max Bid→Decision Log→Report→Disposition→Archive
- Stack: GitHub + Supabase + Vercel + GitHub Actions (NO Google Drive)
- Smart Router: FREE/ULTRA_CHEAP/BUDGET/PRODUCTION/CRITICAL tiers

Current date: ${new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
Current time FL: ${new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' })} EST`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4096,
        system: systemPrompt,
        messages: messages
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Anthropic API error:', errorData);
      return res.status(response.status).json({ error: errorData.error?.message || 'API error' });
    }

    const data = await response.json();
    
    // Log to Supabase if we have credentials
    const SUPABASE_URL = process.env.SUPABASE_URL || 'https://mocerqjnksmhcjzxrewo.supabase.co';
    const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
    
    if (SUPABASE_KEY && session_id) {
      try {
        await fetch(`${SUPABASE_URL}/rest/v1/chat_sessions`, {
          method: 'POST',
          headers: {
            'apikey': SUPABASE_KEY,
            'Authorization': `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
          },
          body: JSON.stringify({
            session_id: session_id,
            messages: JSON.stringify(messages),
            last_response: data.content[0]?.text || '',
            updated_at: new Date().toISOString()
          })
        });
      } catch (logError) {
        console.error('Failed to log to Supabase:', logError);
      }
    }

    return res.status(200).json(data);
  } catch (error) {
    console.error('Handler error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
