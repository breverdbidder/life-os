// Life OS Chat API - Cloudflare Pages Function
// Enhanced with web search + memory tools

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
    const { password, messages, session_id } = body;

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

    const systemPrompt = `You are Claude, integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Family: Wife Mariam, Son Michael (16, D1 swimmer at Satellite Beach HS)
- Style: Direct, no softening language, action-oriented

CURRENT TIME: ${dateStr} | FL: ${flTime} EST | IL: ${ilTime} IST

YOU HAVE 5 TOOLS - USE THEM:
1. github_list_files - List repo directories
2. github_read_file - Read file contents
3. supabase_query - Query database (insights, activities, historical_auctions)
4. web_search - Search the internet for current information
5. memory_search - Search stored insights/knowledge

REPOS: breverdbidder/life-os, breverdbidder/brevard-bidder-scraper, breverdbidder/brevard-bidder-landing

KEY INSIGHT TYPES in Supabase:
- michael_swim: Michael's swimming data, D1 recruiting, college tour plans
- mcp_reference: BrevardBidderAI architecture
- learning: Learning sessions
- ORCHESTRATOR_RUN: System runs

ALWAYS use tools when asked about files, data, current events, or stored information. For Michael's D1 tour, query supabase insights with insight_type=michael_swim.`;

    const tools = [
      {
        name: "github_list_files",
        description: "List files in a GitHub repository directory",
        input_schema: {
          type: "object",
          properties: {
            repo: { type: "string", description: "Repository: breverdbidder/life-os or breverdbidder/brevard-bidder-scraper" },
            path: { type: "string", description: "Directory path, empty for root" }
          },
          required: ["repo"]
        }
      },
      {
        name: "github_read_file",
        description: "Read contents of a file from GitHub repository",
        input_schema: {
          type: "object",
          properties: {
            repo: { type: "string", description: "Repository in format owner/repo" },
            path: { type: "string", description: "File path" }
          },
          required: ["repo", "path"]
        }
      },
      {
        name: "supabase_query",
        description: "Query Supabase database. Tables: insights (michael_swim, mcp_reference, learning), activities, historical_auctions, daily_metrics",
        input_schema: {
          type: "object",
          properties: {
            table: { type: "string", description: "Table name" },
            select: { type: "string", description: "Columns (default: *)" },
            filter: { type: "string", description: "Filter like: insight_type=eq.michael_swim or priority=eq.high" },
            order: { type: "string", description: "Order: created_at.desc" },
            limit: { type: "number", description: "Max rows (default: 10)" }
          },
          required: ["table"]
        }
      },
      {
        name: "web_search",
        description: "Search the web for current information. Use for news, prices, weather, current events.",
        input_schema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" }
          },
          required: ["query"]
        }
      },
      {
        name: "memory_search",
        description: "Search stored insights and knowledge in Supabase. Use for Michael's swim info, BrevardBidderAI details, past decisions.",
        input_schema: {
          type: "object",
          properties: {
            query: { type: "string", description: "What to search for" },
            type: { type: "string", description: "Optional: michael_swim, mcp_reference, learning, ORCHESTRATOR_RUN" }
          },
          required: ["query"]
        }
      }
    ];

    // Execute tool
    async function executeTool(name, input) {
      try {
        if (name === "github_list_files") {
          const { repo, path = "" } = input;
          const url = `https://api.github.com/repos/${repo}/contents/${path}`;
          const resp = await fetch(url, {
            headers: { 
              'Authorization': `token ${env.GITHUB_TOKEN}`,
              'Accept': 'application/vnd.github.v3+json',
              'User-Agent': 'LifeOS-Bot'
            }
          });
          if (!resp.ok) return { error: `Failed: ${resp.status}` };
          const files = await resp.json();
          if (Array.isArray(files)) {
            return { files: files.map(f => ({ name: f.name, type: f.type, path: f.path })) };
          }
          return { error: "Not a directory" };
        }
        
        if (name === "github_read_file") {
          const { repo, path } = input;
          const url = `https://raw.githubusercontent.com/${repo}/main/${path}`;
          const resp = await fetch(url, {
            headers: { 'Authorization': `token ${env.GITHUB_TOKEN}` }
          });
          if (!resp.ok) return { error: `File not found: ${path}` };
          const content = await resp.text();
          return { content: content.substring(0, 8000) };
        }
        
        if (name === "supabase_query") {
          const { table, select = "*", filter, order, limit = 10 } = input;
          let url = `${env.SUPABASE_URL}/rest/v1/${table}?select=${select}&limit=${limit}`;
          if (filter) url += `&${filter}`;
          if (order) url += `&order=${order}`;
          
          const resp = await fetch(url, {
            headers: {
              'apikey': env.SUPABASE_SERVICE_KEY,
              'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`
            }
          });
          if (!resp.ok) return { error: `Query failed: ${resp.status}` };
          const rows = await resp.json();
          return { rows, count: rows.length };
        }

        if (name === "web_search") {
          const { query } = input;
          // Use DuckDuckGo HTML search (no API key needed)
          const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
          const resp = await fetch(searchUrl, {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LifeOS/1.0)' }
          });
          if (!resp.ok) return { error: `Search failed: ${resp.status}` };
          const html = await resp.text();
          
          // Extract results from DuckDuckGo HTML
          const results = [];
          const regex = /<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)<\/a>/gi;
          const snippetRegex = /<a[^>]+class="result__snippet"[^>]*>([^<]+)<\/a>/gi;
          
          let match;
          while ((match = regex.exec(html)) !== null && results.length < 5) {
            results.push({ url: match[1], title: match[2].trim() });
          }
          
          let snippetMatch;
          let i = 0;
          while ((snippetMatch = snippetRegex.exec(html)) !== null && i < results.length) {
            results[i].snippet = snippetMatch[1].trim().substring(0, 200);
            i++;
          }
          
          if (results.length === 0) {
            return { message: "No results found", query };
          }
          return { results, query };
        }

        if (name === "memory_search") {
          const { query, type } = input;
          let url = `${env.SUPABASE_URL}/rest/v1/insights?select=*&order=created_at.desc&limit=5`;
          if (type) {
            url += `&insight_type=eq.${type}`;
          }
          // Search in title and description
          url += `&or=(title.ilike.*${encodeURIComponent(query)}*,description.ilike.*${encodeURIComponent(query)}*)`;
          
          const resp = await fetch(url, {
            headers: {
              'apikey': env.SUPABASE_SERVICE_KEY,
              'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`
            }
          });
          if (!resp.ok) {
            // Fallback: just get recent insights of the type
            const fallbackUrl = `${env.SUPABASE_URL}/rest/v1/insights?select=*&order=created_at.desc&limit=5${type ? `&insight_type=eq.${type}` : ''}`;
            const fallbackResp = await fetch(fallbackUrl, {
              headers: {
                'apikey': env.SUPABASE_SERVICE_KEY,
                'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`
              }
            });
            if (!fallbackResp.ok) return { error: `Search failed` };
            const rows = await fallbackResp.json();
            return { results: rows, query };
          }
          const rows = await resp.json();
          return { results: rows, query };
        }
        
        return { error: "Unknown tool" };
      } catch (e) {
        return { error: `Tool error: ${e.message}` };
      }
    }

    // Call Anthropic API
    async function callAnthropic(msgs) {
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
          tools: tools,
          messages: msgs
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || `API error ${response.status}`);
      }

      return response.json();
    }

    // Tool loop
    let conversationMessages = [...messages];
    let data;
    
    for (let i = 0; i < 6; i++) {
      data = await callAnthropic(conversationMessages);
      
      if (data.stop_reason !== 'tool_use') break;
      
      const toolCalls = data.content.filter(b => b.type === 'tool_use');
      if (toolCalls.length === 0) break;
      
      const toolResults = [];
      for (const tc of toolCalls) {
        const result = await executeTool(tc.name, tc.input);
        toolResults.push({
          type: 'tool_result',
          tool_use_id: tc.id,
          content: JSON.stringify(result)
        });
      }
      
      conversationMessages.push({ role: 'assistant', content: data.content });
      conversationMessages.push({ role: 'user', content: toolResults });
    }

    // Log to Supabase
    if (env.SUPABASE_SERVICE_KEY && session_id) {
      fetch(`${env.SUPABASE_URL}/rest/v1/chat_sessions`, {
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
          last_response: data?.content?.find(b => b.type === 'text')?.text || '',
          updated_at: new Date().toISOString()
        })
      }).catch(() => {});
    }

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message || 'Internal error' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}
