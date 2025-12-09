// Life OS Chat API - Cloudflare Pages Function
// Proxies requests to Anthropic API with GitHub + Supabase tools

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
    const systemPrompt = `You are Claude, integrated with Ariel Shapira's Life OS - an ADHD-optimized productivity system.

CORE IDENTITY:
- User: Ariel Shapira (Managing Member, Everest Capital of Brevard LLC)
- Dual timezone: FL (America/New_York) | IL (Asia/Jerusalem)  
- Family: Wife Mariam, Son Michael (16, D1 swimmer)
- Style: Direct, no softening language, action-oriented

YOU HAVE TOOLS - USE THEM:
- github_list_files: List files in any repo directory
- github_read_file: Read any file from repos
- supabase_query: Query database tables

ALWAYS use tools when asked about code, files, data, or status. Do not say you cannot access systems.

REPOS: breverdbidder/life-os, breverdbidder/brevard-bidder-scraper, breverdbidder/brevard-bidder-landing

SUPABASE TABLES: insights, activities, historical_auctions, daily_metrics, chat_sessions

Current: ${now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })} ${now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' })} EST`;

    const tools = [
      {
        name: "github_list_files",
        description: "List files in a GitHub repository directory. Use this to explore repo structure.",
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
            path: { type: "string", description: "File path (e.g., README.md)" }
          },
          required: ["repo", "path"]
        }
      },
      {
        name: "supabase_query",
        description: "Query Supabase database. Tables: insights, activities, historical_auctions, daily_metrics",
        input_schema: {
          type: "object",
          properties: {
            table: { type: "string", description: "Table name" },
            select: { type: "string", description: "Columns (default: *)" },
            filter: { type: "string", description: "Filter: column=eq.value" },
            order: { type: "string", description: "Order: column.desc" },
            limit: { type: "number", description: "Max rows (default: 10)" }
          },
          required: ["table"]
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
          return { content: content.substring(0, 6000) };
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
          return { data: await resp.json() };
        }
        
        return { error: "Unknown tool" };
      } catch (e) {
        return { error: `Tool error: ${e.message}` };
      }
    }

    // Build conversation messages
    let conversationMessages = [...messages];
    let data;
    let iterations = 0;
    const maxIterations = 5;

    while (iterations < maxIterations) {
      iterations++;
      
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
          messages: conversationMessages
        })
      });

      if (!response.ok) {
        const err = await response.json();
        return new Response(JSON.stringify({ error: err.error?.message || 'API error' }), {
          status: response.status,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      data = await response.json();
      
      // If no tool use, we're done
      if (data.stop_reason !== 'tool_use') {
        break;
      }
      
      // Execute all tool calls
      const toolUseBlocks = data.content.filter(b => b.type === 'tool_use');
      const toolResults = [];
      
      for (const toolUse of toolUseBlocks) {
        const result = await executeTool(toolUse.name, toolUse.input);
        toolResults.push({
          type: 'tool_result',
          tool_use_id: toolUse.id,
          content: JSON.stringify(result)
        });
      }
      
      // Add assistant response and tool results to conversation
      conversationMessages.push({ role: 'assistant', content: data.content });
      conversationMessages.push({ role: 'user', content: toolResults });
    }

    // Log to Supabase
    if (env.SUPABASE_SERVICE_KEY && session_id) {
      try {
        await fetch(`${env.SUPABASE_URL}/rest/v1/chat_sessions`, {
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
        });
      } catch (e) { /* ignore */ }
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
