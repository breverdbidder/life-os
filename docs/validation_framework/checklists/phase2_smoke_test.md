# Phase 2: Smoke Test Build (Days 11-15)

## Deliverables
1. Landing Page (live URL)
2. Analytics Dashboard
3. Wizard of Oz Demo

## 3-Tier CTA Strategy

### Primary CTA: "Get Early Access"
- **Commitment:** High (email + questionnaire)
- **Target Conversion:** 3-5%
- **Indicates:** Strong intent

### Secondary CTA: "Join Waitlist"  
- **Commitment:** Medium (email only)
- **Target Conversion:** 8-12%
- **Indicates:** Interested but cautious

### Tertiary CTA: "Schedule Demo"
- **Commitment:** Low (calendar link)
- **Target Conversion:** 15-20%
- **Indicates:** Curious, needs convincing

## Landing Page Structure

1. **Hero** (above fold)
   - Headline: Outcome-focused (not feature-focused)
   - Subhead: Clarify who it's for
   - Primary CTA button

2. **Problem Section**
   - "You're struggling with X because Y"
   - Use EXACT words from interviews

3. **Solution**  
   - 3 key features (not 10)
   - Benefit-driven bullets

4. **Social Proof** (if available)
   - Beta user quotes
   - Logos (with permission)

5. **Demo**
   - Loom video (3-5 min) OR
   - Figma prototype embed OR  
   - Screenshot carousel

6. **Final CTA**
   - Repeat primary + secondary CTAs

## Analytics Stack

### Google Analytics 4
```html
<!-- Add to <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
```

**Track Events:**
- `primary_cta_click`
- `secondary_cta_click`
- `tertiary_cta_click`
- `demo_video_play`
- `form_submit`

### Hotjar (Heatmaps)
- Watch where users click
- See scroll depth
- Session replays

### PostHog (Optional)
- Funnel analysis
- Feature flags for A/B tests

## A/B Testing Plan

### Test 1: Headline
- **A:** Feature-focused ("AI-Powered X")
- **B:** Outcome-focused ("Save 10 Hours/Week on X")
- **Metric:** Time on page + Primary CTA clicks

### Test 2: CTA Copy
- **A:** "Get Early Access"
- **B:** "Start Free Trial"  
- **Metric:** Click-through rate

**Run tests for 100 visitors each before declaring winner**

## Decision Gate
- [ ] Landing page live with SSL
- [ ] All 3 CTAs functional
- [ ] Analytics tracking verified (test yourself)
- [ ] Demo video/prototype embedded
- [ ] Mobile responsive (test on phone)

**→ Proceed to Phase 3**
