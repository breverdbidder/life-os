// Life OS Chat API - Cloudflare Pages Function
// Enhanced with Web Search, Memory, and GitHub tools

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
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await request.json();
    const { password, messages, session_id } = body;

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

    const now = new Date();
    const flTime = now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' });
    const ilTime = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });

    const systemPrompt = `You are Claude, integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Family: Wife Mariam, Son Michael (16, D1 swimmer at Satellite Beach HS)
- Style: Direct, no softening language, action-oriented
- Current Time: 🕐 FL: ${flTime} EST | IL: ${ilTime} IST
- Date: ${dateStr}

YOU HAVE POWERFUL TOOLS - USE THEM:

1. **web_search** - Search the internet for current information, news, research
2. **memory_search** - Search Ariel's stored insights, tasks, Michael's swim data
3. **github_list_files** - List files in repos (life-os, brevard-bidder-scraper, brevard-bidder-landing)
4. **github_read_file** - Read file contents from repos
5. **supabase_query** - Query database directly

MEMORY CATEGORIES (insight_type values):
- michael_swim: D1 recruiting, times, nutrition, college tours
- learning: Research, articles, insights saved
- business: Foreclosure auctions, BrevardBidderAI, deals
- health_log: Sleep, energy, focus tracking
- claude_performance: AI performance metrics

ALWAYS search memory first for questions about Michael, past research, or saved information.
Use web_search for current events, prices, news, or anything requiring fresh data.

REPOS: breverdbidder/life-os, breverdbidder/brevard-bidder-scraper, breverdbidder/brevard-bidder-landing`;

    // Custom tools (executed locally)
    const customTools = [
      {
        name: "memory_search",
        description: "Search Ariel's stored insights and memory. Categories: michael_swim (D1 recruiting, times, nutrition), learning (research, articles), business (foreclosures, BrevardBidderAI), health_log, claude_performance. Use this FIRST for questions about Michael, past research, or saved information.",
        input_schema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search term or topic" },
            category: { type: "string", description: "Optional: michael_swim, learning, business, health_log, claude_performance" },
            limit: { type: "number", description: "Max results (default 10)" }
          },
          required: ["query"]
        }
      },
      {
        name: "github_list_files",
        description: "List files in a GitHub repository directory.",
        input_schema: {
          type: "object",
          properties: {
            repo: { type: "string", description: "Repository: breverdbidder/life-os, breverdbidder/brevard-bidder-scraper, or breverdbidder/brevard-bidder-landing" },
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
            path: { type: "string", description: "File path (e.g., README.md)" }
          },
          required: ["repo", "path"]
        }
      },
      {
        name: "supabase_query",
        description: "Query Supabase database directly. Tables: insights, activities, historical_auctions, daily_metrics, chat_sessions",
        input_schema: {
          type: "object",
          properties: {
            table: { type: "string", description: "Table name" },
            select: { type: "string", description: "Columns (default: *)" },
            filter: { type: "string", description: "Filter: column=eq.value or column=ilike.*search*" },
            order: { type: "string", description: "Order: column.desc" },
            limit: { type: "number", description: "Max rows (default: 10)" }
          },
          required: ["table"]
        }
      }
    ];

    // Anthropic's server-side web search tool
    const serverTools = [
      {
        type: "web_search_20250305",
        name: "web_search",
        max_uses: 5
      }
    ];

    // Execute custom tool
    async function executeCustomTool(name, input) {
      try {
        if (name === "memory_search") {
          const { query, category, limit = 10 } = input;
          let url = `${env.SUPABASE_URL}/rest/v1/insights?select=*&limit=${limit}&order=created_at.desc`;
          
          // Search in title and description
          url += `&or=(title.ilike.*${encodeURIComponent(query)}*,description.ilike.*${encodeURIComponent(query)}*)`;
          
          if (category) {
            url += `&insight_type=eq.${category}`;
          }
          
          const resp = await fetch(url, {
            headers: {
              'apikey': env.SUPABASE_SERVICE_KEY,
              'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`
            }
          });
          if (!resp.ok) return { error: `Memory search failed: ${resp.status}` };
          const rows = await resp.json();
          return { 
            results: rows.map(r => ({
              title: r.title,
              description: r.description,
              category: r.insight_type,
              date: r.created_at,
              priority: r.priority
            })),
            count: rows.length 
          };
        }

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
          if (!resp.ok) return { error: `Failed to list: ${resp.status}` };
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
        
        return null; // Not a custom tool
      } catch (e) {
        return { error: `Tool error: ${e.message}` };
      }
    }

    // Call Anthropic API with both custom and server tools
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
          tools: [...customTools, ...serverTools],
          messages: msgs
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || `API error ${response.status}`);
      }

      return response.json();
    }

    // Build conversation with tool loop
    let conversationMessages = [...messages];
    let data;
    
    for (let i = 0; i < 8; i++) { // Allow more iterations for complex queries
      data = await callAnthropic(conversationMessages);
      
      // If not a tool call, we're done
      if (data.stop_reason !== 'tool_use') {
        break;
      }
      
      // Extract tool calls
      const toolCalls = data.content.filter(b => b.type === 'tool_use');
      if (toolCalls.length === 0) break;
      
      // Execute each tool
      const toolResults = [];
      for (const tc of toolCalls) {
        // Try custom tool first
        const customResult = await executeCustomTool(tc.name, tc.input);
        
        if (customResult !== null) {
          // It's a custom tool we handle
          toolResults.push({
            type: 'tool_result',
            tool_use_id: tc.id,
            content: JSON.stringify(customResult)
          });
        }
        // web_search is handled server-side by Anthropic, no need to execute
      }
      
      // If we have results to add
      if (toolResults.length > 0 || toolCalls.some(tc => tc.name === 'web_search')) {
        conversationMessages.push({ role: 'assistant', content: data.content });
        if (toolResults.length > 0) {
          conversationMessages.push({ role: 'user', content: toolResults });
        }
      }
    }

    // Log to Supabase (fire and forget)
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
