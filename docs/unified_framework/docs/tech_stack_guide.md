# Z.I.N.O.K Tech Stack Guide
## Modern AI-First Development Stack

**Last Updated:** 2025-12-30  
**Difficulty:** Beginner-Friendly  
**Cost:** $0-50/month  

---

## 🎯 Philosophy: Vibe-Coding

**Traditional Coding:**
```
Learn syntax → Study frameworks → Write code → Debug → Deploy
Timeline: 3-6 months for junior dev
```

**Vibe-Coding:**
```
Describe what you want → AI generates code → Iterate with AI → Deploy
Timeline: 1-2 weeks for non-technical founder
```

**This is not "no-code" - it's AI-assisted coding.**

---

## 🛠️ The Complete Stack

### 1. Loveable.ai - Initial Code Generation

**What it does:** Generates full applications from natural language prompts  
**Cost:** Free tier available  
**Best for:** Getting 0 → 1 (initial prototype)  

**Setup (5 minutes):**
1. Go to loveable.ai
2. Sign up with GitHub
3. Create new project
4. Describe your app

**Example Prompt:**
```
Build a SaaS tool for [ICP] that helps them [solve problem].

Features:
1. User authentication (email/password)
2. Dashboard with [key metrics]
3. [Core feature 1 description]
4. [Core feature 2 description]
5. Settings page

Tech stack: Next.js 14, Supabase, Tailwind CSS
Design: Modern, clean, professional
Colors: Blue primary, gray secondary
```

**Output:** Working codebase in 10-30 minutes

**What Loveable Creates:**
- ✅ Full Next.js application
- ✅ Supabase integration
- ✅ Authentication setup
- ✅ Database schema
- ✅ Responsive UI
- ✅ Deployment-ready

---

### 2. Cursor AI - Iterative Development

**What it does:** AI pair programmer for editing/improving code  
**Cost:** $20/month (Pro plan recommended)  
**Best for:** Iteration after initial generation  

**Setup (10 minutes):**
1. Download from cursor.sh
2. Install (it's VS Code fork)
3. Sign in with GitHub
4. Import your Loveable project

**Key Commands:**
- `Cmd/Ctrl + K` - AI chat inline
- `Cmd/Ctrl + L` - AI chat sidebar
- `Cmd/Ctrl + I` - AI terminal

**Example Iteration:**
```
You: "Add a search bar to filter the dashboard table"
AI: [generates code, shows diff]
You: Accept or modify

You: "Make the search case-insensitive and search all columns"
AI: [updates code]
You: Accept

You: "Add loading spinner while searching"
AI: [adds spinner component]
```

**Pro Tips:**
- Reference files with `@filename`
- Use `/edit` for precise changes
- Use `/ask` for questions about code
- Use `/fix` for bug fixes

---

### 3. Supabase - Backend Infrastructure

**What it does:** PostgreSQL database + Auth + Realtime + Storage  
**Cost:** Free tier (50K monthly active users)  
**Best for:** Complete backend without DevOps  

**What You Get:**
- PostgreSQL database (Postgres 15)
- Authentication (email, OAuth, magic links)
- Realtime subscriptions (WebSocket)
- File storage (images, PDFs, etc.)
- Edge Functions (serverless)
- Auto-generated APIs

**Setup (15 minutes):**
1. Go to supabase.com
2. Create new project
3. Get your API keys
4. Add to `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx... # Keep secret!
```

**Critical: Row Level Security (RLS)**

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);

-- Policy: Users can only update their own data
CREATE POLICY "Users can update own data"
ON users FOR UPDATE
USING (auth.uid() = id);
```

**Never skip RLS - it's your security.**

---

### 4. Vercel - Deployment & Hosting

**What it does:** Zero-config deployment with CDN  
**Cost:** Free tier (generous limits)  
**Best for:** Next.js apps (built by Vercel)  

**Setup (5 minutes):**
1. Go to vercel.com
2. Import from GitHub
3. Configure environment variables
4. Deploy

**Auto-Deploy Flow:**
```
Push to GitHub main branch
    ↓
Vercel detects changes
    ↓
Builds your app (2-3 min)
    ↓
Deploys to CDN globally
    ↓
LIVE at yourapp.vercel.app
```

**Custom Domain (10 minutes):**
1. Buy domain (Namecheap, $12/year)
2. Add to Vercel project
3. Update nameservers
4. SSL auto-provisions (5-10 min)
5. Live at yourdomain.com

**Features:**
- ✅ Automatic HTTPS
- ✅ Edge network (fast globally)
- ✅ Preview deployments (every PR)
- ✅ Rollback (one click)
- ✅ Analytics (Core Web Vitals)

---

### 5. Stripe - Payments

**What it does:** Payment processing for SaaS  
**Cost:** 2.9% + $0.30 per transaction  
**Best for:** Subscription billing  

**Setup (30 minutes):**
1. Sign up at stripe.com
2. Get API keys (test + live)
3. Install Stripe SDK:

```bash
npm install stripe @stripe/stripe-js
```

4. Create products in Stripe dashboard
5. Implement checkout flow

**Basic Implementation:**

```javascript
// Create checkout session
const session = await stripe.checkout.sessions.create({
  line_items: [{
    price: 'price_xxx', // From Stripe dashboard
    quantity: 1,
  }],
  mode: 'subscription',
  success_url: `${YOUR_DOMAIN}/success`,
  cancel_url: `${YOUR_DOMAIN}/cancel`,
});

// Redirect to Stripe Checkout
window.location.href = session.url;
```

**Webhook for fulfillment:**

```javascript
// Handle successful payment
stripe.webhooks.constructEvent(
  request.body,
  signature,
  webhookSecret
);

if (event.type === 'checkout.session.completed') {
  // Grant access to product
  await grantAccess(session.customer);
}
```

---

## 🔧 Complete Setup Checklist

### Step 1: Initial Generation (Day 1)
- [ ] Sign up for Loveable.ai
- [ ] Write detailed app description
- [ ] Generate initial codebase
- [ ] Review generated code

### Step 2: Development Setup (Day 1)
- [ ] Install Cursor AI
- [ ] Clone generated repo
- [ ] Install dependencies: `npm install`
- [ ] Run locally: `npm run dev`

### Step 3: Backend Setup (Day 2)
- [ ] Create Supabase project
- [ ] Configure database schema
- [ ] Enable RLS on all tables
- [ ] Test authentication flow
- [ ] Add API keys to `.env.local`

### Step 4: Deployment (Day 2)
- [ ] Push code to GitHub
- [ ] Import to Vercel
- [ ] Configure environment variables
- [ ] Deploy
- [ ] Test live site

### Step 5: Payments (Day 3-4)
- [ ] Sign up for Stripe
- [ ] Create products/prices
- [ ] Implement checkout flow
- [ ] Setup webhooks
- [ ] Test subscription flow

### Step 6: Polish (Day 5-7)
- [ ] Add analytics (Vercel Analytics)
- [ ] Error tracking (Sentry)
- [ ] Customer support (Crisp/Intercom)
- [ ] Optimize performance
- [ ] Security audit

---

## 💰 Cost Breakdown

### Free Tier Limits

**Loveable:**
- Free: 3 projects
- Paid: $20/mo for unlimited

**Cursor:**
- Free: 2 weeks trial
- Pro: $20/mo (recommended)

**Supabase:**
- Free: 50K MAU, 500MB database, 1GB storage
- Pro: $25/mo (2GB database, 100GB storage)

**Vercel:**
- Free: 100GB bandwidth, unlimited deployments
- Pro: $20/mo (1TB bandwidth, advanced features)

**Stripe:**
- Free: No monthly fee
- Transaction: 2.9% + $0.30

### Monthly Cost Projection

**Months 1-3 (Beta):** $0-20/mo
- Loveable: $0 (free tier)
- Cursor: $20/mo
- Supabase: $0 (free tier)
- Vercel: $0 (free tier)

**Months 4-6 (Early Paid Users):** $45-65/mo
- Loveable: $20/mo (if still iterating)
- Cursor: $20/mo
- Supabase: $25/mo (if >50K users)
- Vercel: $0 (still free)

**Months 7-12 (Growth):** $65-200/mo
- Cursor: $20/mo
- Supabase: $25/mo
- Vercel: $20/mo
- Additional tools: $0-135/mo

**Much cheaper than traditional development ($5K-15K/mo for developers)**

---

## ⚠️ Common Pitfalls

### 1. Skipping RLS (Row Level Security)

**Problem:** Anyone can access any data  
**Solution:** Enable RLS from day 1

```sql
-- Check which tables lack RLS
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename NOT IN (
  SELECT tablename FROM pg_policies
);
```

### 2. Committing Secrets to Git

**Problem:** API keys exposed publicly  
**Solution:** Use `.env.local` (gitignored)

```bash
# .gitignore
.env.local
.env*.local
```

### 3. Not Testing Locally First

**Problem:** Deploy broken code  
**Solution:** Always run `npm run dev` and test

### 4. Ignoring Errors

**Problem:** Silent failures in production  
**Solution:** Add error tracking

```bash
npm install @sentry/nextjs
```

### 5. No Database Backups

**Problem:** Data loss  
**Solution:** Enable Supabase backups (Settings → Database)

---

## 🚀 Advanced Features

### When to Add These

**Month 1-2:** Focus on core features  
**Month 3-4:** Add if users request  
**Month 5+:** Scale infrastructure  

### Email Sending (Resend)

```bash
npm install resend
```

**Use cases:** Welcome emails, notifications, digests

### Background Jobs (Inngest)

```bash
npm install inngest
```

**Use cases:** Scheduled tasks, async processing

### Feature Flags (PostHog)

```bash
npm install posthog-js
```

**Use cases:** A/B testing, gradual rollouts

### Search (Algolia)

```bash
npm install algoliasearch
```

**Use cases:** Fast search, autocomplete

---

## 📚 Learning Resources

### Official Docs
- Next.js: nextjs.org/docs
- Supabase: supabase.com/docs
- Vercel: vercel.com/docs
- Stripe: stripe.com/docs

### Video Tutorials
- Loveable: YouTube channel
- Cursor: Documentation site
- Full Stack Next.js: Vercel YouTube

### Communities
- Supabase Discord
- Vercel Discord
- Indie Hackers
- r/SaaS

---

## ✅ Ready to Build?

**You now have:**
- Complete tech stack understanding
- Setup instructions
- Cost projections
- Security best practices
- Troubleshooting guide

**Next steps:**
1. Complete Week 6 (Pre-Build Preparation)
2. Write your Loveable prompt
3. Generate initial codebase
4. Start iterating with Cursor

**Remember the 70/30 rule:** Ship at 70%, iterate based on feedback.

---

**Questions?** Join the community Discord (link in main framework docs)
