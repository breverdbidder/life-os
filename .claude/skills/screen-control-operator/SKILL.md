---
name: screen-control-operator
description: Autonomous browser control and verification using Chrome DevTools Protocol and Accessibility Tree (NO screenshots). Use this skill when the user requests screen control, browser automation, Lovable preview verification, scraper debugging, DOM inspection, or autonomous UI testing. Triggers include "control my screen", "verify Lovable preview", "test the frontend", "debug the scraper", "inspect DOM elements", "autonomous browser testing", or when acting like GPT Operator.
---

# Screen Control Operator

Autonomous browser control using Chrome DevTools Protocol (CDP) and Accessibility Tree inspection - **NO screenshots required**. Acts like GPT Operator with full screen control, element interaction, and state verification.

## Core Capabilities

1. **Browser Control**: Navigate, click, type, scroll via CDP
2. **DOM Inspection**: Read accessibility tree for element discovery  
3. **State Verification**: Check visibility, text, attributes autonomously
4. **Scraper Debugging**: Inspect actual DOM selectors for failed scrapers
5. **Lovable Preview Testing**: Verify UI components, interactions, responsiveness
6. **Multi-step Workflows**: Execute complex browser automation sequences

## Quick Start

```bash
# Install dependencies
pip install playwright --break-system-packages
playwright install chromium

# Run autonomous verification
python scripts/autonomous_browser_control.py \
  --url "https://brevard-bidder-landing.pages.dev" \
  --tests "navigation,map,markers,search"
```

## Workflows

### 1. Lovable Preview Verification

Verify BidDeed.AI Metrix map autonomously:
- Map rendering with Mapbox
- Property markers with $ amounts
- County dropdown functionality
- 12-stage pipeline visibility
- Mobile responsiveness (375px)

### 2. Scraper Debugging  

Get actual DOM selectors for failed scrapers:
- BECA login form elements
- BCPAO search inputs
- AcclaimWeb navigation
- Anti-bot detection
- Session cookies

### 3. Frontend QA

Test deployed Cloudflare Pages sites:
- DOM inspection
- Console error monitoring
- Network request tracking
- Performance metrics

## DOM Inspection (No Screenshots)

```python
# Find by semantic role
page.get_by_role("button", name="Preview")

# Check visibility
assert page.locator('#map-container').is_visible()

# Monitor console errors  
errors = page.evaluate('() => window.__errors || []')
```

## Integration

Add to GitHub Actions:

```yaml
- run: pip install playwright
- run: playwright install chromium
- run: python scripts/autonomous_browser_control.py
```

## When to Use

- Lovable preview verification without screenshots
- Scraper debugging (get real DOM selectors)
- Frontend QA on deployed sites  
- Multi-step browser automation
- Headless CI/CD testing

See `scripts/autonomous_browser_control.py` for implementation and `references/playwright_api.md` for complete API documentation.
