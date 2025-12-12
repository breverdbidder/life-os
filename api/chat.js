// Life OS Chat API - Smart Router V5
// DEFAULT: gemini-2.5-flash (1M context FREE)
// Fallback: Anthropic API for complex operations
// Author: Ariel Shapira, Solo Founder, Everest Capital USA

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { password, messages, session_id, force_tier } = req.body;
  
  if (password !== process.env.LIFE_OS_PASSWORD) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Messages array required' });
  }

  // Detect complexity to route to appropriate tier
  const lastMessage = messages[messages.length - 1]?.content || '';
  const tier = force_tier || detectTier(lastMessage);

  // System prompt with Life OS context
  const systemPrompt = `You are Claude, integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Dual timezone: FL (America/New_York) | IL (Asia/Jerusalem)
- Family: Wife Mariam, Son Michael (16, D1 swimmer)
- Style: Direct, no softening language, action-oriented

DOMAINS: BUSINESS (Everest Capital, BidDeed.AI), MICHAEL D1 SWIMMING, FAMILY, PERSONAL

SMART ROUTER V5 ACTIVE:
- Current Tier: ${tier}
- Default Model: gemini-2.5-flash (1M context FREE)
- Context Window: 1,000,000 tokens`;

  try {
    let result;
    
    // Route based on tier
    if (tier === 'FREE' && process.env.GOOGLE_API_KEY) {
      // DEFAULT: Use Gemini 2.5 Flash (1M context FREE)
      result = await callGemini(messages, systemPrompt, process.env.GOOGLE_API_KEY);
    } else if (process.env.ANTHROPIC_API_KEY) {
      // Fallback to Anthropic for complex operations
      result = await callAnthropic(messages, systemPrompt, process.env.ANTHROPIC_API_KEY);
    } else {
      return res.status(500).json({ error: 'No API keys configured' });
    }

    return res.status(200).json({
      content: result.content,
      model: result.model,
      tier: tier,
      contextWindow: result.contextWindow,
      cost: result.cost,
      routing: {
        detected_tier: tier,
        model_used: result.model
      }
    });

  } catch (error) {
    console.error('API Error:', error);
    return res.status(500).json({ error: error.message });
  }
}

function detectTier(message) {
  const lower = message.toLowerCase();
  
  // CRITICAL tier - high stakes decisions
  if (/max bid|final approval|lien priority|legal review|high value/.test(lower)) return 'CRITICAL';
  
  // PRODUCTION tier - complex analysis
  if (/analyze|strategy|market|complex|detailed report/.test(lower)) return 'PRODUCTION';
  
  // ULTRA_CHEAP tier - lien/title work
  if (/lien analysis|title search|summarize/.test(lower)) return 'ULTRA_CHEAP';
  
  // DEFAULT: FREE tier (gemini-2.5-flash - 1M context)
  return 'FREE';
}

async function callGemini(messages, systemPrompt, apiKey) {
  const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n');
  const fullPrompt = `${systemPrompt}\n\nConversation:\n${prompt}`;
  
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: fullPrompt }] }],
        generationConfig: { maxOutputTokens: 8192, temperature: 0.7 }
      })
    }
  );
  
  const data = await response.json();
  
  if (data.candidates?.[0]?.content?.parts?.[0]?.text) {
    return {
      content: data.candidates[0].content.parts[0].text,
      model: 'gemini-2.5-flash',
      contextWindow: 1000000,
      cost: 0
    };
  }
  
  throw new Error(data.error?.message || 'Gemini API error');
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
  
  if (data.content?.[0]?.text) {
    return {
      content: data.content[0].text,
      model: 'claude-sonnet-4-20250514',
      contextWindow: 200000,
      cost: 3.0
    };
  }
  
  throw new Error(data.error?.message || 'Anthropic API error');
}
