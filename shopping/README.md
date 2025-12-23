# Life OS Shopping Integration

Automated shopping list creation with Instacart integration for Life OS.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Life OS Chat                             │
│  life-os-aiy.pages.dev/chat                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  User: "Buy this at Costco via Instacart"           │   │
│  │  - Foilrite pans (5 packs)                          │   │
│  │  - SoftSoap hand soap                               │   │
│  │  - Coffee-mate powder 56oz                          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare Worker API                           │
│  /api/shopping/create                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Parse natural language → structured items        │   │
│  │  2. Apply Costco product mappings                   │   │
│  │  3. Call Instacart Developer Platform API           │   │
│  │  4. Log to Supabase                                 │   │
│  │  5. Return shareable Instacart URL                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Instacart Developer Platform                    │
│  https://connect.instacart.com/idp/v1/products/products_link│
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Creates shopping list page                        │   │
│  │  - Matches products to Costco inventory             │   │
│  │  - Returns deep-link URL                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Instacart App                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  User opens link → selects Costco → reviews items   │   │
│  │  → adds to cart → completes checkout                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### POST /api/shopping/create

Create a shopping list on Instacart.

**Request:**
```json
{
  "title": "Costco Run - Dec 23",
  "items": "Foilrite pans (5 packs)\nSoftSoap hand soap\nCoffee-mate powder 56oz",
  "store": "costco",
  "log_to_supabase": true
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://www.instacart.com/store/costco/...",
  "items": [
    {"name": "Heavy Duty Aluminum Pans", "quantity": 5, "brand": "Foilrite"},
    {"name": "Liquid Hand Soap", "brand": "Softsoap"},
    {"name": "Coffee Creamer Powder", "quantity": 56, "unit": "oz", "brand": "Coffee-mate"}
  ]
}
```

### POST /api/shopping/parse

Parse text into structured items without creating a list.

**Request:**
```json
{
  "text": "Paper towels\nToilet tissue\n2oz cups with lids (50)"
}
```

**Response:**
```json
{
  "success": true,
  "items": [
    {"name": "Paper towels", "quantity": 1},
    {"name": "Toilet tissue", "quantity": 1},
    {"name": "Cups with lids", "quantity": 50, "unit": "oz"}
  ],
  "count": 3
}
```

## Setup

### 1. Get Instacart API Key

1. Apply at https://www.instacart.com/company/business/developers
2. Once approved, get API key from Developer Dashboard
3. Store as `INSTACART_API_KEY` secret

### 2. Configure Secrets

```bash
# Cloudflare Workers secrets
wrangler secret put INSTACART_API_KEY
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_KEY
```

### 3. Deploy

```bash
# Development
npm run deploy:dev

# Production
npm run deploy:prod
```

### 4. Run Supabase Migration

```bash
# Via Supabase CLI
supabase db push

# Or run SQL directly in Supabase Dashboard
```

## Integration with Life OS Chat

Add to `chat.html`:

```javascript
// When user mentions shopping + Instacart
async function createInstacartList(items, store = 'costco') {
  const response = await fetch('/api/shopping/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: `${store} Shopping - ${new Date().toLocaleDateString()}`,
      items: items,
      store: store,
      log_to_supabase: true
    })
  });
  
  const data = await response.json();
  if (data.success) {
    // Show link to user
    return `✅ Shopping list created!\n\n🛒 [Open in Instacart](${data.url})`;
  }
  return `❌ Error: ${data.error}`;
}
```

## MCP Alternative

Instacart also offers direct MCP server integration:

```
Development: https://mcp.dev.instacart.tools/mcp
Production: https://mcp.instacart.com/mcp
```

Tools available:
- `create-recipe` - Create recipe pages
- `create-shopping-list` - Create shopping lists

## Cost Analysis

| Component | Cost |
|-----------|------|
| Instacart API | FREE (affiliate model) |
| Cloudflare Workers | FREE (100K req/day) |
| Supabase | FREE tier / $25 Pro |
| **Total** | **$0-25/month** |

## Files

```
life-os-instacart/
├── src/
│   ├── instacart_client.ts    # Core API client
│   ├── worker.ts              # Cloudflare Worker
│   └── components/
│       └── ShoppingList.tsx   # React component
├── supabase/
│   └── migrations/
│       └── 20241223_create_shopping_lists.sql
├── workflows/
│   └── deploy_shopping.yml    # GitHub Actions
├── package.json
├── tsconfig.json
├── wrangler.toml
└── README.md
```

## Next Steps

1. [ ] Apply for Instacart Developer Platform access
2. [ ] Deploy Worker to Cloudflare
3. [ ] Run Supabase migration
4. [ ] Integrate into Life OS chat.html
5. [ ] Test with real Costco shopping list

---

**Built for Life OS by Claude AI Architect**
