// Cloudflare Worker: proxies AI assurance review requests to Claude API
// Deploy: npx wrangler deploy
// Set secret: npx wrangler secret put ANTHROPIC_API_KEY

export default {
  async fetch(request, env) {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
          'Access-Control-Max-Age': '86400',
        },
      });
    }

    if (request.method !== 'POST') {
      return corsResponse(JSON.stringify({ error: 'Method not allowed' }), 405);
    }

    const apiKey = env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return corsResponse(JSON.stringify({ error: 'API key not configured' }), 500);
    }

    try {
      const body = await request.json();

      if (!body.system || !body.messages) {
        return corsResponse(JSON.stringify({ error: 'Missing system or messages' }), 400);
      }

      const resp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
        },
        body: JSON.stringify({
          model: body.model || 'claude-sonnet-4-20250514',
          max_tokens: body.max_tokens || 1000,
          system: body.system,
          messages: body.messages,
        }),
      });

      const data = await resp.json();

      if (!resp.ok) {
        return corsResponse(
          JSON.stringify({ error: data?.error?.message || `API error ${resp.status}` }),
          resp.status
        );
      }

      return corsResponse(JSON.stringify(data), 200);
    } catch (err) {
      return corsResponse(JSON.stringify({ error: err.message }), 500);
    }
  },
};

function corsResponse(body, status) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
