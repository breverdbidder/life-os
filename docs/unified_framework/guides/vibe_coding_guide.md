# Vibe-Coding Best Practices
## The 70/30 Philosophy for Rapid Development

**Core Principle:** Ship at 70% done, iterate to 100% based on real usage, not assumptions.

**Origin:** Z.I.N.O.K Methodology (5 successful SaaS products)

---

## 🎯 What is Vibe-Coding?

**Traditional Development:**
```
Plan (2 weeks) → Design (2 weeks) → Code (8 weeks) → Test (2 weeks) → Ship
= 14 weeks to launch
= Perfect product, zero users
```

**Vibe-Coding:**
```
Prompt AI (1 hour) → Ship (1 day) → Learn (1 week) → Iterate
= 1 week to launch
= 70% product, real users, real feedback
```

**Key Insight:** You can't know what users want until they use it. So ship fast, learn fast, improve fast.

---

## 📏 The 70/30 Rule Explained

### What is 70%?

**Must Have:**
- ✅ Core workflow works (main feature functional)
- ✅ Happy path succeeds (primary use case completes)
- ✅ Basic error handling (doesn't crash)
- ✅ Mobile responsive (works on phone)
- ✅ Secure (authentication, RLS enabled)

**Nice to Have (Can Wait):**
- ⏸️ Perfect design (stock photos OK)
- ⏸️ Edge case handling (fix when reported)
- ⏸️ Performance optimization (scale when needed)
- ⏸️ Advanced features (add based on requests)
- ⏸️ Comprehensive docs (iterate with users)

### The 30% You Skip Initially

**Polish:**
- Custom graphics
- Animations
- Dark mode
- Accessibility improvements
- SEO optimization

**Edge Cases:**
- Rare error scenarios
- Complex validation
- Advanced permissions
- Multi-language support

**Performance:**
- Query optimization
- Caching layers
- Image optimization
- Code splitting

**Features Nobody Asked For:**
- "Cool" features you think users want
- Integrations with 10 different tools
- Complex settings pages
- Anything not validated

---

## 🚀 Vibe-Coding Workflow

### Phase 1: AI Generation (Day 1)

**Use Loveable.ai:**
```
Input: Detailed prompt (30 minutes to write)
Output: Working MVP (1-2 hours to generate)
Result: Deployable codebase at 50-60%
```

**Prompt Quality = Output Quality:**
- Be specific about user flows
- Describe happy path in detail
- Mention data relationships
- Specify authentication needs
- Request error states

### Phase 2: Quick Fixes (Day 2-3)

**Use Cursor AI:**
- Fix obvious bugs
- Adjust styling
- Add missing validations
- Improve error messages

**Don't:**
- Rebuild from scratch
- Add features nobody requested
- Optimize prematurely
- Perfect every detail

### Phase 3: Deploy & Observe (Day 4-5)

**Ship to Vercel:**
- Push to GitHub
- Auto-deploy
- Share with 5-10 beta users
- Watch them use it (Hotjar, screen share)

**Collect:**
- Where do they get stuck?
- What do they ask for?
- What do they ignore?
- What breaks?

### Phase 4: Iterate (Week 2+)

**Priority Order:**
1. Critical bugs (blocking usage)
2. Confusion points (users get lost)
3. Requested features (users ask for)
4. Performance issues (if slow)
5. Polish (only when above are done)

**Iteration Speed:**
- Daily: Bug fixes
- Weekly: Small features
- Bi-weekly: Bigger features
- Monthly: Refactoring

---

## ⚠️ Common Pitfalls

### 1. "I'll just polish this one thing..."

**Symptom:** Spending days on design before any user feedback  
**Cure:** Set a timer. 2 hours max on polish. Ship.

### 2. "What if users encounter error X?"

**Symptom:** Building elaborate error handling for rare cases  
**Cure:** Handle happy path. Add error handling when error occurs.

### 3. "This code is ugly/messy"

**Symptom:** Refactoring before user validation  
**Cure:** Ugly code that works > beautiful code nobody uses. Refactor at 100 users.

### 4. "I need to add feature Y before launching"

**Symptom:** Feature creep before launch  
**Cure:** Launch with one feature. Add Y when users ask for Y.

### 5. "It's not perfect yet"

**Symptom:** Perfectionism, fear of judgment  
**Cure:** Perfect is the enemy of good. Launched beats perfect.

---

## ✅ Checklist: Is It 70%?

Before shipping, verify these only:

**Functionality:**
- [ ] Main feature works end-to-end
- [ ] User can sign up/login
- [ ] User can complete primary action
- [ ] Data saves correctly
- [ ] User can access their data

**Security:**
- [ ] Authentication required for protected routes
- [ ] RLS enabled on database tables
- [ ] No API keys in frontend code
- [ ] HTTPS enabled (Vercel default)

**Usability:**
- [ ] Desktop works
- [ ] Mobile works (doesn't need to be perfect)
- [ ] Loading states exist (even if just "Loading...")
- [ ] Error messages exist (even if generic)
- [ ] User knows what to do next

**That's it.** If these check out, you're at 70%. Ship.

---

## 📊 70% vs 100%: Time Comparison

| Task | 70% Time | 100% Time | Ratio |
|------|----------|-----------|-------|
| **Landing Page** | 2 hours | 2 days | 12× |
| **Authentication** | 1 hour (Supabase) | 1 week (custom) | 40× |
| **Database** | 2 hours (generated) | 3 days (designed) | 12× |
| **UI Design** | 3 hours (templates) | 2 weeks (custom) | 35× |
| **Error Handling** | 2 hours (basics) | 1 week (comprehensive) | 20× |
| **Testing** | 1 hour (manual) | 3 days (automated) | 24× |
| **Documentation** | 0 hours | 2 days | ∞ |
| **TOTAL** | **1 week** | **6-8 weeks** | **6-8×** |

**With real users, 70% improves to 100% in 2-3 weeks based on feedback.**  
**Without users, 100% is just guesswork.**

---

## 🎓 Learning to Vibe-Code

### Week 1: Pure AI
- Use Loveable for everything
- Deploy generated code as-is
- Learn by observing what it creates

### Week 2: Small Tweaks
- Use Cursor to change colors
- Fix obvious typos
- Adjust spacing
- Learn: "Oh, that's how buttons work"

### Week 3: Feature Additions
- Use Cursor to add simple features
- Copy patterns from generated code
- Learn: "I can do this myself now"

### Week 4: Understanding
- Read the generated code
- Understand component structure
- Learn: "I see how this fits together"

### Month 2+: Confident Coding
- Generate with AI, modify yourself
- Mix AI and manual coding
- Learn: "I can build this traditionally too"

**You're learning by shipping, not by courses.** That's faster and more effective.

---

## 🛠️ Handling Technical Debt

### When to Refactor

**Don't Refactor:**
- Before launch (premature)
- At 10 users (too early)
- When adding features is faster (velocity matters)

**Do Refactor:**
- At 100+ paying customers (revenue justifies it)
- When bugs slow you down (if fix rate < bug rate)
- When onboarding new developer (if relevant)
- When tech limits growth (if scaling blocked)

### Refactoring Strategy

**Phase 1 (10-20 users): Tolerate debt**
- Ship fast
- Learn what matters
- Don't optimize

**Phase 2 (20-100 users): Selective fixes**
- Fix painful bugs only
- Improve critical paths
- Document major hacks

**Phase 3 (100-500 users): Systematic cleanup**
- Dedicate 1 week/month to refactoring
- Test coverage on core features
- Improve code quality gradually

**Phase 4 (500+ users): Consider rebuild**
- Evaluate: Refactor vs rewrite vs migrate
- If vibe-coded MVP works, maybe keep it
- If scaling blocked, plan 2.0

---

## 🎯 Success Metrics for Vibe-Coding

**Speed:**
- Idea → deployed: <1 week ✅
- Feature request → shipped: <3 days ✅
- Bug report → fixed: <24 hours ✅

**Learning:**
- User interviews/week: 3+ ✅
- Feature iterations/week: 5+ ✅
- "I should have built X instead" realizations: Many ✅

**Business:**
- First paying customer: <4 weeks ✅
- Product-market fit: <6 months ✅
- Sustainable growth: <12 months ✅

**Code Quality (honestly doesn't matter until scale):**
- Test coverage: 0% (add at 100+ users)
- Code reviews: None (solo is fine)
- Documentation: Minimal (iterate with users)

---

## 💡 Vibe-Coding Mantras

**"Perfect is the enemy of shipped."**  
Launch at 70%, iterate to 100%.

**"Users don't care about your code quality."**  
They care if it solves their problem.

**"The best feature is the one users requested."**  
Don't guess, ask.

**"Fast feedback > slow perfection."**  
Ship weekly, learn quickly.

**"Technical debt is fine if you're learning."**  
You can't refactor zero users.

**"AI writes code, users write requirements."**  
Use AI for speed, users for direction.

**"Ugly code that works > beautiful code nobody uses."**  
Launch always wins.

---

## 🚀 Case Study: Mettrico (Z.I.N.O.K Success)

**What it does:** Restaurant metrics dashboard  
**Time to MVP:** 5 days  
**Built with:** Loveable + Cursor + Vercel + Supabase  

**Timeline:**
- Day 1: Loveable generated MVP
- Day 2-3: Cursor fixed bugs, adjusted UI
- Day 4: Deployed, shared with 3 restaurants
- Day 5: Collected feedback, made changes
- Week 2: 10 restaurants using it
- Week 4: First paying customer
- Month 3: 50 customers, $5K MRR

**Key Insight:**
- Launched at 60% (barely worked)
- Iterated daily based on real usage
- Reached 100% by Month 2
- Would have taken 3+ months traditional way

**70/30 in Action:**
- Generated auth (didn't build custom)
- Used stock icons (didn't design)
- Basic charts (didn't perfect viz)
- Shipped daily (didn't wait for perfect)

**Result:** Speed to market = competitive advantage

---

## 📚 Recommended Stack for Vibe-Coding

**Generation:**
- Loveable.ai (full stack)
- v0.dev (UI components)
- Bolt.new (alternative)

**Iteration:**
- Cursor AI (best for code)
- GitHub Copilot (good alternative)
- Codeium (free option)

**Deployment:**
- Vercel (Next.js)
- Netlify (alternative)
- Railway (backend)

**Database:**
- Supabase (PostgreSQL)
- Neon (PostgreSQL alternative)
- PlanetScale (MySQL)

**Why These:**
- Generous free tiers
- AI-friendly
- Fast deployment
- Minimal DevOps

---

## 🎬 Final Thoughts on Vibe-Coding

**It's not about coding less.**  
It's about learning faster.

**It's not about AI replacing you.**  
It's about AI amplifying you.

**It's not about low quality.**  
It's about right quality at right time.

**It's not about avoiding best practices.**  
It's about earning the right to use them.

**You can't optimize for 1000 users when you have 0.**  
You can't refactor for scale before product-market fit.  
You can't perfect features nobody validated.

**Ship at 70%. Learn. Iterate. Win.** 🚀

---

**Created by:** Z.I.N.O.K Methodology  
**Updated:** 2025-12-30  
**License:** MIT
