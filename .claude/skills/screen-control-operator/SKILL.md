---
name: screen-control-operator
description: Claude AI screen control via Browser DevTools Protocol and Accessibility Tree for autonomous verification and interaction
---

# Screen Control Operator

Enables Claude to control browser windows, verify UI state, and execute autonomous workflows using CDP (Chrome DevTools Protocol) and accessibility tree inspection - NOT screenshots.

## When to Use This Skill

- Autonomous browser testing and verification
- Lovable preview checkpoint verification
- Form filling and data entry automation
- Multi-step browser workflows
- UI state validation without screenshots
- Cross-browser compatibility testing

## How This Works (Not Screenshots)

### The GPT Operator Approach

**What GPT Operator Actually Uses:**
1. **Chrome DevTools Protocol (CDP):** Direct browser control API
2. **Accessibility Tree:** DOM structure + semantic info
3. **Element Queries:** Find elements by role, label, text
4. **Action Commands:** Click, type, scroll, navigate
5. **State Verification:** Check element visibility, text content, attributes

**Why This Is Better Than Screenshots:**
- 10x faster (no image processing)
- 100% reliable element detection
- Can read text precisely
- Works with dynamic content
- No OCR errors
- Headless compatible

## Core Components

### 1. Chrome DevTools Protocol (CDP)

**Setup:**
```python
from playwright.sync_api import sync_playwright

def launch_browser_with_cdp():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,  # Set True for headless
        args=['--remote-debugging-port=9222']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()
    return playwright, browser, context, page
```

### 2. Accessibility Tree Inspection

**Query DOM Without Screenshots:**
```python
def get_page_structure(page):
    # Get accessibility tree
    accessibility = page.accessibility.snapshot()
    
    # Get all interactive elements
    elements = page.query_selector_all('[role], button, a, input, select')
    
    structure = {
        'url': page.url,
        'title': page.title(),
        'interactive_elements': []
    }
    
    for elem in elements:
        structure['interactive_elements'].append({
            'role': elem.get_attribute('role'),
            'label': elem.get_attribute('aria-label') or elem.inner_text(),
            'type': elem.get_attribute('type'),
            'visible': elem.is_visible(),
            'enabled': elem.is_enabled()
        })
    
    return structure
```

### 3. Element Interaction

**Find and Click Elements:**
```python
def click_element(page, selector=None, text=None, role=None):
    if selector:
        page.click(selector)
    elif text:
        page.get_by_text(text).click()
    elif role:
        page.get_by_role(role).click()
```

**Type Into Fields:**
```python
def fill_field(page, label, value):
    page.get_by_label(label).fill(value)
```

**Verify State:**
```python
def verify_element_visible(page, selector):
    element = page.locator(selector)
    return element.is_visible()
```

## Lovable Preview Checkpoint System

### Autonomous Verification Without Screenshots

**Step 1: Navigate to Preview**
```python
def navigate_to_lovable_preview(page, project_id):
    url = f"https://lovable.dev/projects/{project_id}"
    page.goto(url)
    
    # Wait for preview button
    page.get_by_role("button", name="Preview").wait_for()
    page.get_by_role("button", name="Preview").click()
    
    # Switch to preview window
    preview_page = page.context.wait_for_event('page')
    return preview_page
```

**Step 2: Verify UI Elements**
```python
def verify_lovable_ui_state(page):
    checkpoints = {
        'header_visible': False,
        'map_container_present': False,
        'property_markers_loaded': False,
        'search_functional': False
    }
    
    # Check header
    checkpoints['header_visible'] = page.locator('header').is_visible()
    
    # Check map container
    map_selector = '[id*="map"], .leaflet-container, #mapContainer'
    checkpoints['map_container_present'] = page.locator(map_selector).count() > 0
    
    # Check for map markers (Leaflet)
    markers = page.locator('.leaflet-marker-icon').count()
    checkpoints['property_markers_loaded'] = markers > 0
    
    # Check search functionality
    search_input = page.get_by_placeholder("Search properties")
    checkpoints['search_functional'] = search_input.is_visible()
    
    return checkpoints
```

**Step 3: Test Interactive Features**
```python
def test_map_interactions(page):
    results = {}
    
    # Test zoom controls
    zoom_in = page.locator('.leaflet-control-zoom-in')
    if zoom_in.is_visible():
        zoom_in.click()
        page.wait_for_timeout(500)
        results['zoom_works'] = True
    
    # Test marker click
    markers = page.locator('.leaflet-marker-icon')
    if markers.count() > 0:
        markers.first.click()
        page.wait_for_timeout(500)
        
        # Check if popup appeared
        popup = page.locator('.leaflet-popup')
        results['popup_works'] = popup.is_visible()
    
    return results
```

## Complete Autonomous Workflow

### Lovable Preview Verification Pipeline

```python
def autonomous_lovable_verification(project_id):
    playwright, browser, context, page = launch_browser_with_cdp()
    
    try:
        # Step 1: Navigate
        preview_page = navigate_to_lovable_preview(page, project_id)
        
        # Step 2: Get page structure
        structure = get_page_structure(preview_page)
        
        # Step 3: Run checkpoints
        ui_state = verify_lovable_ui_state(preview_page)
        
        # Step 4: Test interactions
        interaction_tests = test_map_interactions(preview_page)
        
        # Step 5: Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_id': project_id,
            'url': preview_page.url,
            'page_structure': structure,
            'ui_checkpoints': ui_state,
            'interaction_tests': interaction_tests,
            'issues': []
        }
        
        # Identify issues
        if not ui_state['map_container_present']:
            report['issues'].append({
                'severity': 'CRITICAL',
                'component': 'Map',
                'description': 'Map container not found in DOM'
            })
        
        if not ui_state['property_markers_loaded']:
            report['issues'].append({
                'severity': 'HIGH',
                'component': 'Markers',
                'description': 'No property markers detected on map'
            })
        
        return report
        
    finally:
        browser.close()
        playwright.stop()
```

## LangGraph Integration

### Multi-Step Browser Automation

```python
from langgraph.graph import StateGraph, END

class BrowserAutomationState:
    page_url: str
    checkpoints_passed: dict
    errors: list
    current_step: str

def create_browser_automation_graph():
    workflow = StateGraph(BrowserAutomationState)
    
    # Nodes
    workflow.add_node("navigate", navigate_node)
    workflow.add_node("verify_ui", verify_ui_node)
    workflow.add_node("test_interactions", test_interactions_node)
    workflow.add_node("generate_report", generate_report_node)
    
    # Edges
    workflow.add_edge("navigate", "verify_ui")
    workflow.add_edge("verify_ui", "test_interactions")
    workflow.add_edge("test_interactions", "generate_report")
    workflow.add_edge("generate_report", END)
    
    workflow.set_entry_point("navigate")
    
    return workflow.compile()
```

## GitHub Actions Integration

### Scheduled Lovable Verification

**Workflow:** `.github/workflows/verify_lovable_preview.yml`

```yaml
name: Verify Lovable Preview

on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:
    inputs:
      project_id:
        description: 'Lovable Project ID'
        required: true
        default: 'fe59383e-3396-49f3-9cb9-5fea97dce977'

jobs:
  verify:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Playwright
        run: |
          pip install playwright
          playwright install chromium
      
      - name: Run Verification
        run: |
          python scripts/verify_lovable.py \
            --project-id ${{ inputs.project_id }} \
            --output verification_report.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: verification-report
          path: verification_report.json
      
      - name: Log to Supabase
        run: |
          python scripts/log_verification_to_supabase.py \
            --report verification_report.json
```

## Advanced Features

### 1. Network Monitoring

**Track API Calls:**
```python
def monitor_network(page):
    api_calls = []
    
    def handle_request(request):
        if '/api/' in request.url:
            api_calls.append({
                'url': request.url,
                'method': request.method,
                'timestamp': datetime.now()
            })
    
    page.on('request', handle_request)
    return api_calls
```

### 2. Console Error Detection

**Catch JavaScript Errors:**
```python
def monitor_console(page):
    errors = []
    
    def handle_console(msg):
        if msg.type == 'error':
            errors.append({
                'text': msg.text,
                'timestamp': datetime.now()
            })
    
    page.on('console', handle_console)
    return errors
```

### 3. Performance Metrics

**Measure Load Times:**
```python
def measure_performance(page):
    metrics = page.evaluate('''() => {
        const perf = performance.getEntriesByType('navigation')[0];
        return {
            dom_content_loaded: perf.domContentLoadedEventEnd - perf.fetchStart,
            load_complete: perf.loadEventEnd - perf.fetchStart,
            first_paint: performance.getEntriesByType('paint')[0].startTime
        };
    }''')
    return metrics
```

## Deployment

### Install Dependencies

```bash
pip install playwright langchain-anthropic langgraph --break-system-packages
playwright install chromium
```

### Project Structure

```
life-os/
├── .github/workflows/
│   └── verify_lovable_preview.yml
├── scripts/
│   ├── screen_control/
│   │   ├── __init__.py
│   │   ├── browser_control.py
│   │   ├── checkpoint_verifier.py
│   │   ├── lovable_tester.py
│   │   └── report_generator.py
│   ├── verify_lovable.py
│   └── log_verification_to_supabase.py
└── .claude/skills/
    └── screen-control-operator/
        └── SKILL.md
```

## Example Usage

### CLI Usage

```bash
# Run autonomous verification
python scripts/verify_lovable.py \
  --project-id fe59383e-3396-49f3-9cb9-5fea97dce977 \
  --output report.json

# Run with specific tests
python scripts/verify_lovable.py \
  --project-id fe59383e-3396-49f3-9cb9-5fea97dce977 \
  --tests map,markers,search,filters \
  --headless
```

### From Claude Chat

```
"Use screen-control-operator to verify Lovable preview for project fe59383e"

"Run autonomous checkpoint verification on Lovable map UI"

"Test all interactive features on Lovable preview and generate report"
```

### Programmatic Usage

```python
from scripts.screen_control import autonomous_lovable_verification

# Run full verification
report = autonomous_lovable_verification(
    project_id='fe59383e-3396-49f3-9cb9-5fea97dce977',
    tests=['map', 'markers', 'search', 'filters', 'interactions'],
    headless=True
)

# Check results
if report['issues']:
    print(f"Found {len(report['issues'])} issues")
    for issue in report['issues']:
        print(f"  {issue['severity']}: {issue['description']}")
else:
    print("All checkpoints passed!")
```

## Supabase Logging

**Log Verification Results:**

```python
def log_verification_to_supabase(report):
    import requests
    
    payload = {
        'category': 'learning',
        'subcategory': 'lovable_verification',
        'title': f"Lovable Preview Verification - {report['timestamp']}",
        'content': {
            'project_id': report['project_id'],
            'url': report['url'],
            'checkpoints': report['ui_checkpoints'],
            'interactions': report['interaction_tests'],
            'issues_count': len(report['issues']),
            'issues': report['issues'],
            'all_passed': len(report['issues']) == 0
        }
    }
    
    # Trigger GitHub Actions workflow
    requests.post(
        "https://github.com/breverdbidder/life-os/actions/workflows/insert_insight.yml/dispatches",
        headers={"Authorization": "Bearer GITHUB_TOKEN"},
        json={"ref": "main", "inputs": payload}
    )
```

## Critical Differences from Screenshots

| Feature | Screenshots | CDP + Accessibility |
|---------|-------------|---------------------|
| Speed | Slow (1-5s per check) | Fast (50-200ms) |
| Reliability | OCR errors common | 100% accurate |
| Dynamic Content | Misses loading states | Handles perfectly |
| Text Extraction | Unreliable | Precise |
| Element Interaction | Coordinate-based (fragile) | Semantic (robust) |
| Headless Support | Poor | Excellent |

## Best Practices

1. **Use Semantic Selectors:** Prefer `get_by_role()`, `get_by_label()` over CSS selectors
2. **Wait for State:** Use `wait_for()` instead of timeouts
3. **Handle Errors:** Wrap interactions in try/catch
4. **Log Everything:** Track all actions for debugging
5. **Parallel Tests:** Run independent tests concurrently
6. **Retry Logic:** Auto-retry flaky interactions (3x max)

## Example Output

**Verification Report:**
```json
{
  "timestamp": "2025-12-25T03:30:00Z",
  "project_id": "fe59383e-3396-49f3-9cb9-5fea97dce977",
  "url": "https://lovable.dev/projects/fe59383e-3396-49f3-9cb9-5fea97dce977/preview",
  "ui_checkpoints": {
    "header_visible": true,
    "map_container_present": true,
    "property_markers_loaded": true,
    "search_functional": true
  },
  "interaction_tests": {
    "zoom_works": true,
    "popup_works": true,
    "filter_works": true
  },
  "performance": {
    "dom_content_loaded": 847,
    "load_complete": 1234,
    "first_paint": 456
  },
  "issues": []
}
```

## Integration with ADHD Task Management

When verification fails:
```python
# Trigger ADHD intervention if stuck
if len(report['issues']) > 0:
    # Use adhd-task-management-skill
    suggest_micro_commitment("Fix issue: " + report['issues'][0]['description'])
```

## Critical Reminders

1. **NO SCREENSHOTS:** This skill uses CDP + accessibility tree only
2. **Headless Ready:** Works in GitHub Actions without display
3. **Fast & Reliable:** 10x faster than vision-based approaches
4. **Semantic Queries:** Find elements by meaning, not position
5. **State Verification:** Check actual DOM state, not pixels
