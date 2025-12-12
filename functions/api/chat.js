// Life OS Chat API - Smart Router V5
// DEFAULT: Gemini 2.5 Flash (1M context FREE)
// Author: Ariel Shapira, Solo Founder, Everest Capital USA

export async function onRequest(context) {
  const { request, env } = context;
  
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
      status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await request.json();
    const { password, messages, session_id, force_anthropic } = body;

    if (password !== env.LIFE_OS_PASSWORD) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    if (!messages || !Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: 'Messages array required' }), {
        status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const now = new Date();
    const flTime = now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' });
    const ilTime = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });

    const systemPrompt = `You are an AI assistant integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Family: Wife Mariam, Son Michael (16, D1 swimmer at Satellite Beach HS)
- Style: Direct, no softening language, action-oriented

CURRENT TIME: ${dateStr} | FL: ${flTime} EST | IL: ${ilTime} IST

SMART ROUTER V5 ACTIVE:
- Model: Gemini 2.5 Flash (1M context FREE)
- Context Window: 1,000,000 tokens
- Cost: $0

DOMAINS: BUSINESS (Everest Capital, BidDeed.AI), MICHAEL D1 SWIMMING, FAMILY, PERSONAL

Be helpful, direct, and action-oriented. Minimize human-in-the-loop - execute tasks autonomously when possible.`;

    // DEFAULT: Use Gemini 2.5 Flash (1M context FREE)
    // Only use Anthropic if explicitly forced
    let result;
    
    if (force_anthropic && env.ANTHROPIC_API_KEY) {
      result = await callAnthropic(messages, systemPrompt, env.ANTHROPIC_API_KEY);
    } else {
      // DEFAULT: Gemini 2.5 Flash
      result = await callGemini(messages, systemPrompt, env.GOOGLE_API_KEY);
    }

    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    return new Response(JSON.stringify({ 
      error: error.message,
      model: 'error',
      fallback: 'Check GOOGLE_API_KEY in Cloudflare env'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

async function callGemini(messages, systemPrompt, apiKey) {
  if (!apiKey) {
    throw new Error('GOOGLE_API_KEY not configured');
  }

  // Convert messages to Gemini format
  const conversationHistory = messages.map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`).join('\n\n');
  const fullPrompt = `${systemPrompt}\n\n---\nCONVERSATION:\n${conversationHistory}\n\nAssistant:`;

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: fullPrompt }] }],
        generationConfig: { 
          maxOutputTokens: 8192, 
          temperature: 0.7 
        }
      })
    }
  );

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error.message || 'Gemini API error');
  }

  if (data.candidates?.[0]?.content?.parts?.[0]?.text) {
    const text = data.candidates[0].content.parts[0].text;
    const usage = data.usageMetadata || {};
    
    return {
      model: 'gemini-2.5-flash',
      tier: 'FREE',
      contextWindow: 1000000,
      cost: 0,
      content: [{ type: 'text', text: text }],
      usage: {
        input_tokens: usage.promptTokenCount || 0,
        output_tokens: usage.candidatesTokenCount || 0
      },
      routing: {
        model_used: 'gemini-2.5-flash',
        context_window: '1M tokens (FREE)',
        tier: 'FREE'
      }
    };
  }

  throw new Error('No response from Gemini');
}

async function callAnthropic(messages, systemPrompt, apiKey) {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 8192,
      system: systemPrompt,
      messages: messages
    })
  });

  const data = await response.json();
  
  return {
    ...data,
    tier: 'PRODUCTION',
    contextWindow: 200000,
    cost: 3.0,
    routing: {
      model_used: 'claude-sonnet-4-20250514',
      context_window: '200K tokens',
      tier: 'PRODUCTION (forced)'
    }
  };
}
