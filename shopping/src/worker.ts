/**
 * Life OS Shopping Worker
 * Cloudflare Worker that integrates with Instacart API
 * 
 * Endpoints:
 * POST /api/shopping/create - Create shopping list from items
 * POST /api/shopping/parse - Parse text into structured items
 */

import InstacartClient from './instacart_client';

interface Env {
  INSTACART_API_KEY: string;
  INSTACART_DEV_MODE?: string;
  SUPABASE_URL: string;
  SUPABASE_KEY: string;
}

interface CreateListRequest {
  title: string;
  items?: string;  // Raw text list
  structured_items?: Array<{
    name: string;
    quantity?: number;
    unit?: string;
    brand?: string;
  }>;
  store?: 'costco' | 'walmart' | 'any';
  log_to_supabase?: boolean;
}

interface ParseRequest {
  text: string;
}

// CORS headers for Life OS chat
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

async function logToSupabase(
  env: Env, 
  data: {
    title: string;
    items: any[];
    instacart_url: string;
    store?: string;
  }
) {
  try {
    const response = await fetch(`${env.SUPABASE_URL}/rest/v1/shopping_lists`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': env.SUPABASE_KEY,
        'Authorization': `Bearer ${env.SUPABASE_KEY}`,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({
        title: data.title,
        items: data.items,
        instacart_url: data.instacart_url,
        store: data.store || 'any',
        created_at: new Date().toISOString()
      })
    });

    if (!response.ok) {
      console.error('Supabase log failed:', await response.text());
    }
  } catch (error) {
    console.error('Supabase error:', error);
  }
}

async function handleCreateList(request: Request, env: Env): Promise<Response> {
  const body: CreateListRequest = await request.json();
  
  if (!body.title) {
    return new Response(JSON.stringify({ error: 'Title is required' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  if (!body.items && !body.structured_items) {
    return new Response(JSON.stringify({ error: 'Items (text or structured) required' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  const isDev = env.INSTACART_DEV_MODE === 'true';
  const client = new InstacartClient(env.INSTACART_API_KEY, isDev);

  try {
    let result;
    
    if (body.items) {
      // Parse from raw text
      result = await client.createFromText(body.title, body.items, {
        enablePantry: true
      });
    } else if (body.structured_items) {
      // Use structured items directly
      result = await client.createShoppingList(
        body.title,
        body.structured_items,
        { enablePantry: true }
      );
    }

    // Log to Supabase if requested
    if (body.log_to_supabase && result) {
      await logToSupabase(env, {
        title: body.title,
        items: result.items || body.structured_items || [],
        instacart_url: result.url || (result as any).products_link_url,
        store: body.store
      });
    }

    return new Response(JSON.stringify({
      success: true,
      url: result?.url || (result as any)?.products_link_url,
      items: result?.items || body.structured_items,
      expires_at: result?.expiresAt
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Instacart API error:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to create shopping list',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

async function handleParse(request: Request, env: Env): Promise<Response> {
  const body: ParseRequest = await request.json();
  
  if (!body.text) {
    return new Response(JSON.stringify({ error: 'Text is required' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  const client = new InstacartClient(env.INSTACART_API_KEY);
  const items = client.parseShoppingList(body.text);

  return new Response(JSON.stringify({
    success: true,
    items,
    count: items.length
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Health check
    if (path === '/health' || path === '/') {
      return new Response(JSON.stringify({ 
        status: 'ok',
        service: 'life-os-shopping',
        version: '1.0.0'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // API Routes
    if (request.method === 'POST') {
      if (path === '/api/shopping/create') {
        return handleCreateList(request, env);
      }
      if (path === '/api/shopping/parse') {
        return handleParse(request, env);
      }
    }

    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
};
