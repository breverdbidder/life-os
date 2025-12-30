# Z.I.N.O.K Tech Stack Guide
## The Proven Stack for Vibe-Coding

**Philosophy:** Use AI to generate code, modern tools to deploy fast, iterate based on real usage.

**Validated By:** 5 successful SaaS products (Mettrico, Sherlock AI, TrekTrack, Moodlog, Loveable)

---

## 🎯 The Complete Stack

```
Loveable.ai (Code Generation)
    ↓
Cursor AI (Iteration & Refinement)
    ↓
GitHub (Version Control)
    ↓
Vercel (Deployment & Hosting)
    ↓
Supabase (Database + Auth + Realtime)
    ↓
Stripe (Payments)
```

**Cost:** $0-50/month (free tiers cover most MVPs)  
**Setup Time:** 2-4 hours  
**Skill Required:** Basic coding familiarity (AI handles complexity)

---

## 1️⃣ Loveable.ai - AI Code Generation

**What it does:** Generate entire codebase from natural language prompts

**Pricing:**
- Free: 3 projects
- Pro: $20/mo (unlimited projects)

**Setup (10 minutes):**
1. Go to loveable.ai
2. Sign up with GitHub
3. Create new project
4. Describe your MVP in detail

**Prompt Template:**
```
Build a [SaaS/marketplace/dashboard] for [target user] to [solve problem].

Core Features:
1. [Feature 1]: Users can [specific action]
2. [Feature 2]: System automatically [automation]
3. [Feature 3]: Display [data visualization]

Tech Requirements:
- Next.js 14 with App Router
- TypeScript for type safety
- Supabase for database and auth
- Tailwind CSS for styling
- shadcn/ui for components

Pages Needed:
- Landing page with [specific elements]
- Dashboard with [specific sections]
- Settings page with [specific options]

Authentication:
- Email/password login
- Google OAuth (optional)
- Protected routes

Database Schema:
- Users table: [fields]
- [MainEntity] table: [fields]
- [RelatedEntity] table: [fields]

Design Style: [modern/minimal/professional/colorful]
Color Scheme: [primary color] with [accent]
```

**What You Get:**
- Complete Next.js codebase
- Supabase integration
- Responsive design
- Authentication flow
- Working MVP in 1-2 hours

**Pro Tips:**
- Be specific about user flows
- Describe edge cases
- Mention loading states
- Specify error handling
- Request accessibility features

---

## 2️⃣ Cursor AI - Iteration & Refinement

**What it does:** AI pair programming for rapid iteration

**Pricing:**
- Free: 2000 completions/month
- Pro: $20/mo (unlimited)

**Setup (5 minutes):**
1. Download from cursor.sh
2. Open Loveable-generated code
3. Connect to GitHub repo

**Core Commands:**
- `Cmd+K`: AI edit (select code, describe change)
- `Cmd+L`: Chat with AI (ask questions)
- `Cmd+Shift+K`: Generate (write new code)

**Iteration Workflow:**
```
Day 1: Generate with Loveable
Day 2-3: Fix bugs with Cursor (Cmd+K: "Fix this error...")
Day 4-5: Add features (Cmd+K: "Add ability to...")
Day 6-7: Polish UI (Cmd+K: "Make this more...")
```

**Example Edits:**
```
"Add loading spinner when fetching data"
→ Cursor adds loading state + spinner component

"Make this form validate email format"
→ Cursor adds zod validation + error messages

"Add pagination to this table"
→ Cursor implements pagination logic + UI

"Fix this TypeScript error"
→ Cursor resolves type issues
```

**Pro Tips:**
- Always describe desired outcome, not implementation
- Use Cmd+L to understand existing code
- Keep changes small (one feature at a time)
- Test after each change
- Commit frequently to Git

---

## 3️⃣ Vercel - Deployment & Hosting

**What it does:** Auto-deploy from GitHub, handle scaling, provide CDN

**Pricing:**
- Hobby: Free (perfect for MVPs)
- Pro: $20/mo (custom domains, more bandwidth)

**Setup (15 minutes):**
1. Push code to GitHub
2. Go to vercel.com
3. Import GitHub repo
4. Configure:
   - Framework: Next.js (auto-detected)
   - Root directory: ./
   - Build command: npm run build
   - Output directory: .next
5. Add environment variables (from Supabase)
6. Deploy!

**Environment Variables:**
```
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx... (for server-side)
STRIPE_PUBLIC_KEY=pk_xxx... (if using payments)
STRIPE_SECRET_KEY=sk_xxx...
```

**Auto-Deploy Workflow:**
```
1. Make changes locally in Cursor
2. Commit: git commit -m "Add feature X"
3. Push: git push origin main
4. Vercel auto-deploys in 30-60 seconds
5. Visit your-app.vercel.app
```

**Custom Domain (optional):**
1. Buy domain (Namecheap, GoDaddy: $12/year)
2. In Vercel: Settings → Domains
3. Add domain
4. Update DNS records (Vercel provides)
5. SSL auto-provisions (5-10 minutes)

**Pro Tips:**
- Use preview deployments (auto-created for branches)
- Check build logs if deployment fails
- Enable Web Analytics (free, built-in)
- Use Environment Variables for secrets
- Set up branch protection (main = production)

---

## 4️⃣ Supabase - Database + Auth + Realtime

**What it does:** PostgreSQL database, authentication, real-time subscriptions, file storage

**Pricing:**
- Free: 500MB database, 50K monthly active users
- Pro: $25/mo (8GB database, 100K MAU)

**Setup (20 minutes):**
1. Go to supabase.com
2. Create new project
3. Choose region (closest to users)
4. Note credentials (save to .env.local)

**Database Setup:**

**Option 1: Loveable generates schema**
- Loveable creates tables automatically
- Check in Supabase SQL Editor

**Option 2: Manual SQL**
```sql
-- Users table (handled by Supabase Auth)
-- Just add custom fields if needed

-- Main entity table
create table posts (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  title text not null,
  content text,
  created_at timestamp default now()
);

-- Enable Row Level Security
alter table posts enable row level security;

-- Policy: Users can only see their own posts
create policy "Users can view own posts"
  on posts for select
  using (auth.uid() = user_id);

-- Policy: Users can insert their own posts
create policy "Users can create posts"
  on posts for insert
  with check (auth.uid() = user_id);
```

**Authentication Setup:**
```typescript
// In Next.js app
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
)

// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password'
})

// Get current user
const { data: { user } } = await supabase.auth.getUser()
```

**Row Level Security (RLS) - CRITICAL:**
```sql
-- ALWAYS enable RLS on tables
alter table your_table enable row level security;

-- Policy examples:

-- Public read
create policy "Anyone can read"
  on your_table for select
  using (true);

-- Authenticated users only
create policy "Authenticated users can read"
  on your_table for select
  using (auth.role() = 'authenticated');

-- User owns the row
create policy "Users own their data"
  on your_table for all
  using (auth.uid() = user_id);

-- Admin access
create policy "Admins can do anything"
  on your_table for all
  using (auth.jwt() ->> 'role' = 'admin');
```

**Real-time Subscriptions:**
```typescript
// Subscribe to changes
const channel = supabase
  .channel('posts-changes')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'posts' },
    (payload) => {
      console.log('Change received!', payload)
    }
  )
  .subscribe()

// Use in React
useEffect(() => {
  const channel = supabase
    .channel('posts')
    .on('postgres_changes', { ... }, updateState)
    .subscribe()
    
  return () => supabase.removeChannel(channel)
}, [])
```

**File Storage:**
```typescript
// Create bucket (in Supabase dashboard)
// Then upload files:

const { data, error } = await supabase.storage
  .from('avatars')
  .upload('user-123.png', file)

// Get public URL
const { data } = supabase.storage
  .from('avatars')
  .getPublicUrl('user-123.png')
```

**Pro Tips:**
- Enable RLS on ALL tables (security)
- Use policies for access control (not app logic)
- Index frequently queried columns
- Enable backups (Settings → Database)
- Monitor usage in dashboard
- Use connection pooling for serverless

---

## 5️⃣ Stripe - Payments

**What it does:** Handle subscriptions, one-time payments, invoices

**Pricing:**
- 2.9% + $0.30 per successful charge
- No monthly fees

**Setup (30 minutes):**
1. Go to stripe.com
2. Create account
3. Get API keys (test mode first)
4. Install: `npm install stripe @stripe/stripe-js`

**Subscription Flow:**
```typescript
// 1. Create products in Stripe Dashboard
// Basic: $29/mo
// Pro: $99/mo

// 2. Server-side: Create checkout session
import Stripe from 'stripe'
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

export async function POST(request) {
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    line_items: [{
      price: 'price_xxx', // From Stripe dashboard
      quantity: 1,
    }],
    success_url: `${origin}/success`,
    cancel_url: `${origin}/cancel`,
  })
  
  return Response.json({ url: session.url })
}

// 3. Client-side: Redirect to checkout
const response = await fetch('/api/checkout', { method: 'POST' })
const { url } = await response.json()
window.location.href = url

// 4. Handle webhook (server-side)
export async function POST(request) {
  const sig = request.headers.get('stripe-signature')
  const event = stripe.webhooks.constructEvent(
    await request.text(),
    sig,
    process.env.STRIPE_WEBHOOK_SECRET
  )
  
  if (event.type === 'checkout.session.completed') {
    // User subscribed! Grant access
    const session = event.data.object
    await grantAccess(session.customer, session.subscription)
  }
  
  return Response.json({ received: true })
}
```

**Testing:**
- Test cards: 4242 4242 4242 4242 (success)
- Expiry: Any future date
- CVC: Any 3 digits
- Use test mode until ready for production

**Pro Tips:**
- Set up webhooks (critical for subscriptions)
- Handle failed payments (email users)
- Implement customer portal (self-service)
- Test cancellation flow
- Monitor in Stripe dashboard

---

## 🔧 Complete Setup Checklist

### Pre-Development (1 hour)
- [ ] Sign up for Loveable.ai
- [ ] Sign up for Vercel
- [ ] Sign up for Supabase
- [ ] Sign up for Stripe (optional, can add later)
- [ ] Create GitHub account (if needed)

### Initial Build (2-4 hours)
- [ ] Generate code with Loveable
- [ ] Test locally: `npm install && npm run dev`
- [ ] Push to GitHub: `git init && git add . && git commit && git push`
- [ ] Deploy to Vercel (connect GitHub repo)
- [ ] Add environment variables to Vercel
- [ ] Test live deployment

### Database Setup (30 minutes)
- [ ] Create Supabase project
- [ ] Run schema SQL or let Loveable handle it
- [ ] Enable RLS on all tables
- [ ] Create policies (who can access what)
- [ ] Test authentication flow

### Polish (1-2 days)
- [ ] Download Cursor AI
- [ ] Clone repo locally
- [ ] Fix bugs with Cursor (Cmd+K)
- [ ] Add missing features
- [ ] Improve UI/UX
- [ ] Test edge cases

### Launch Prep (1 day)
- [ ] Add custom domain (optional)
- [ ] Set up Stripe products
- [ ] Test payment flow
- [ ] Configure webhook endpoint
- [ ] Set up error tracking (Sentry)
- [ ] Add analytics (Vercel Analytics free)

**Total Time:** 4-6 days to working MVP  
**Total Cost:** $0-50 (free tiers sufficient)

---

## 🚨 Common Pitfalls & Solutions

### "Loveable generated buggy code"
**Solution:** That's expected at 70%! Use Cursor to fix bugs iteratively. Describe the bug, Cursor fixes it.

### "I don't know how to code"
**Solution:** This stack is designed for that! Loveable generates, Cursor fixes. You learn by doing. Start simple.

### "Build failed on Vercel"
**Solution:** Check build logs. Usually:
- Missing environment variables
- TypeScript errors (Cursor can fix)
- Package version conflicts (update package.json)

### "Database queries not working"
**Solution:** Check RLS policies. Supabase blocks by default. Create policies to allow access.

### "Stripe webhooks not firing"
**Solution:** Use Stripe CLI for local testing: `stripe listen --forward-to localhost:3000/api/webhooks`

### "App is slow"
**Solution:** 
- Add database indexes
- Implement caching
- Optimize images
- Use Vercel Edge Functions
- Consider Pro tier if needed

---

## 📚 Learning Resources

**Loveable:**
- Official docs: loveable.ai/docs
- Example prompts: loveable.ai/examples

**Cursor:**
- Docs: cursor.sh/docs
- Video tutorials: YouTube "Cursor AI tutorial"

**Next.js:**
- Official tutorial: nextjs.org/learn
- App Router docs: nextjs.org/docs

**Supabase:**
- Getting started: supabase.com/docs
- Auth guide: supabase.com/docs/guides/auth
- RLS patterns: supabase.com/docs/guides/auth/row-level-security

**Stripe:**
- Quick start: stripe.com/docs/payments/quickstart
- Subscriptions: stripe.com/docs/billing/subscriptions/build-subscriptions

---

## 🎓 Progressive Learning Path

### Week 1: Generated Code
- Use Loveable completely
- Deploy as-is
- Learn by observing generated code

### Week 2-3: Small Edits
- Use Cursor for bug fixes
- Change colors, text, styling
- Add simple features

### Week 4-6: Feature Development
- Add new pages
- Modify database schema
- Implement user requests

### Month 2-3: Advanced Features
- Real-time updates
- Complex queries
- Payment flows
- Admin dashboards

### Month 4+: Scale Optimization
- Performance tuning
- Advanced caching
- Custom infrastructure
- Consider traditional dev if needed

**You'll learn by building, not by studying.** That's the vibe-coding way.

---

**Created by:** Z.I.N.O.K Methodology (Dolev) + Claude AI  
**Updated:** 2025-12-30  
**License:** MIT
