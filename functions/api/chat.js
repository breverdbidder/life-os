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

    if (!env.ANTHROPIC_API_KEY) {
      return new Response(JSON.stringify({ error: 'API key not configured' }), {
        status: 500,
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

YOU HAVE TOOLS TO ACCESS:
- GitHub repositories (read files, check workflows, view code)
- Supabase database (query tables: activities, insights, historical_auctions, daily_metrics, chat_sessions)

USE TOOLS PROACTIVELY when asked about:
- BrevardBidderAI status, code, or data
- Swim times, nutrition logs
- Task history, focus scores
- Any data that might be in the repos or database

REPOS AVAILABLE:
- breverdbidder/life-os (Life OS dashboard, orchestrator)
- breverdbidder/brevard-bidder-scraper (BrevardBidderAI main codebase)
- breverdbidder/brevard-bidder-landing (Landing page)

SUPABASE TABLES:
- insights (category, content, metadata, created_at)
- activities (description, domain, status, created_at)
- historical_auctions (auction data)
- daily_metrics (focus scores, productivity)
- chat_sessions (conversation logs)

Current: ${now.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })} ${now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' })} EST`;

    // Tool definitions
    const tools = [
      {
        name: "github_read_file",
        description: "Read a file from a GitHub repository",
        input_schema: {
          type: "object",
          properties: {
            repo: {
              type: "string",
              description: "Repository in format owner/repo (e.g., breverdbidder/life-os)"
            },
            path: {
              type: "string",
              description: "Path to file (e.g., README.md or src/index.js)"
            }
          },
          required: ["repo", "path"]
        }
      },
      {
        name: "github_list_files",
        description: "List files in a GitHub repository directory",
        input_schema: {
          type: "object",
          properties: {
            repo: {
              type: "string",
              description: "Repository in format owner/repo"
            },
            path: {
              type: "string",
              description: "Directory path (empty string for root)"
            }
          },
          required: ["repo"]
        }
      },
      {
        name: "supabase_query",
        description: "Query data from Supabase database",
        input_schema: {
          type: "object",
          properties: {
            table: {
              type: "string",
              description: "Table name (insights, activities, historical_auctions, daily_metrics, chat_sessions)"
            },
            select: {
              type: "string",
              description: "Columns to select (default: *)"
            },
            filter: {
              type: "string",
              description: "Filter in format: column=eq.value or column=gt.value"
            },
            order: {
              type: "string",
              description: "Order by column (e.g., created_at.desc)"
            },
            limit: {
              type: "number",
              description: "Max rows to return (default: 10)"
            }
          },
          required: ["table"]
        }
      }
    ];

    // Execute tool calls
    async function executeTool(name, input) {
      if (name === "github_read_file") {
        const { repo, path } = input;
        const url = `https://raw.githubusercontent.com/${repo}/main/${path}`;
        const resp = await fetch(url, {
          headers: { 'Authorization': `token ${env.GITHUB_TOKEN}` }
        });
        if (!resp.ok) return { error: `File not found: ${path}` };
        const content = await resp.text();
        return { content: content.substring(0, 8000) }; // Limit size
      }
      
      if (name === "github_list_files") {
        const { repo, path = "" } = input;
        const url = `https://api.github.com/repos/${repo}/contents/${path}`;
        const resp = await fetch(url, {
          headers: { 
            'Authorization': `token ${env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        });
        if (!resp.ok) return { error: `Path not found: ${path}` };
        const files = await resp.json();
        return { files: files.map(f => ({ name: f.name, type: f.type, path: f.path })) };
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
        if (!resp.ok) return { error: `Query failed: ${await resp.text()}` };
        return { data: await resp.json() };
      }
      
      return { error: "Unknown tool" };
    }

    // Initial API call
    let response = await fetch('https://api.anthropic.com/v1/messages', {
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
        messages: messages
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      return new Response(JSON.stringify({ error: errorData.error?.message || 'API error' }), {
        status: response.status,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    let data = await response.json();
    
    // Handle tool use loop (max 5 iterations)
    let iterations = 0;
    while (data.stop_reason === 'tool_use' && iterations < 5) {
      iterations++;
      
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
      
      // Continue conversation with tool results
      const newMessages = [
        ...messages,
        { role: 'assistant', content: data.content },
        { role: 'user', content: toolResults }
      ];
      
      response = await fetch('https://api.anthropic.com/v1/messages', {
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
          messages: newMessages
        })
      });
      
      if (!response.ok) break;
      data = await response.json();
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
            last_response: data.content?.find(b => b.type === 'text')?.text || '',
            updated_at: new Date().toISOString()
          })
        });
      } catch (e) { /* ignore logging errors */ }
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
