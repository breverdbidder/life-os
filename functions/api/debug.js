export async function onRequest(context) {
  const { request, env } = context;
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const body = await request.json();
    if (body.password !== env.LIFE_OS_PASSWORD) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: corsHeaders });
    }

    // Direct Supabase test
    const url = `${env.SUPABASE_URL}/rest/v1/insights?select=id&limit=1`;
    const resp = await fetch(url, {
      headers: {
        'apikey': env.SUPABASE_SERVICE_KEY,
        'Authorization': `Bearer ${env.SUPABASE_SERVICE_KEY}`
      }
    });
    
    const respText = await resp.text();
    
    return new Response(JSON.stringify({
      supabase_status: resp.status,
      supabase_ok: resp.ok,
      supabase_response: respText.substring(0, 500),
      has_url: !!env.SUPABASE_URL,
      has_key: !!env.SUPABASE_SERVICE_KEY,
      key_length: env.SUPABASE_SERVICE_KEY?.length || 0,
      url_value: env.SUPABASE_URL
    }), { status: 200, headers: corsHeaders });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: corsHeaders });
  }
}
