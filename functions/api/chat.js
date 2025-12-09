// Life OS Chat API - Cloudflare Pages Function
// Proxies requests to Anthropic API - API key stays server-side

export async function onRequest(context) {
  const { request, env } = context;
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await request.json();
    const { password, messages, session_id } = body;

    // Simple auth check
    if (password !== env.LIFE_OS_PASSWORD) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: 'Messages array required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (!env.ANTHROPIC_API_KEY) {
      return new Response(JSON.stringify({ error: 'API key not configured' }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // System prompt with Life OS context
    const now = new Date();
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
- Stack: GitHub + Supabase + Cloudflare (NO Google Drive)
- Smart Router: FREE/ULTRA_CHEAP/BUDGET/PRODUCTION/CRITICAL tiers

Current date: ${now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
Current time FL: ${now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' })} EST`;

    // Call Anthropic API
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
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
      return new Response(JSON.stringify({ error: errorData.error?.message || 'API error' }), {
        status: response.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const data = await response.json();

    // Log to Supabase if we have credentials
    if (env.SUPABASE_SERVICE_KEY && session_id) {
      try {
        const supabaseUrl = env.SUPABASE_URL || 'https://mocerqjnksmhcjzxrewo.supabase.co';
        await fetch(`${supabaseUrl}/rest/v1/chat_sessions`, {
          method: 'POST',
          headers: {
            'apikey': env.SUPABASE_SERVICE_KEY,
            'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`,
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

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Handler error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}
