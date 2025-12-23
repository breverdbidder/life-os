---
name: website-to-vite-scraper
description: Scrape any website and convert it to a deployable Vite project with proper asset handling, CSS processing, and GitHub/Cloudflare deployment. Triggers on requests to clone, reverse-engineer, or convert websites to modern frameworks.
---

# Website-to-Vite Scraper Skill

Converts any website into a clean, deployable Vite project with proper asset organization.

## When to Use

- Reverse engineering website designs
- Converting legacy sites to modern frameworks
- Creating templates from existing sites
- Backing up website assets and structure

## Quick Start

```python
from website_scraper import WebsiteToViteScraper

scraper = WebsiteToViteScraper("https://example.com", "my-project")
scraper.scrape()
```

## Output Structure

```
my-project/
├── index.html           # Main entry point
├── package.json         # npm dependencies
├── vite.config.js       # Vite configuration
├── .gitignore
├── README.md
└── src/
    ├── main.js          # Entry script
    ├── style.css        # Compiled styles
    ├── pages/           # Scraped HTML pages
    │   ├── index.html
    │   ├── about.html
    │   └── contact.html
    └── assets/
        ├── images/      # Downloaded images
        ├── css/         # External stylesheets
        ├── js/          # External scripts
        └── fonts/       # Web fonts
```

## Full Implementation

See `website_scraper.py` in this skill folder for the complete implementation.

## Features

- **Smart Asset Detection**: Identifies and downloads images, CSS, JS, fonts
- **CSS Processing**: Resolves and downloads assets referenced in stylesheets
- **Relative Path Fixing**: Converts all paths to work in Vite structure
- **Rate Limiting**: Respectful crawling with configurable delays
- **Error Recovery**: Continues on individual asset failures
- **Parallel Downloads**: ThreadPoolExecutor for faster asset retrieval

## Deployment Automation

```bash
# After scraping, deploy to Cloudflare Pages
cd my-project
npm install
npm run build
npx wrangler pages deploy dist --project-name=my-project
```

## GitHub Actions Workflow

```yaml
name: Deploy Scraped Site
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm run build
      - uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: my-project
          directory: dist
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `timeout` | 10s | Request timeout |
| `max_workers` | 5 | Parallel download threads |
| `rate_limit` | 0.5s | Delay between requests |
| `user_agent` | Chrome | Browser identification |
| `verify_ssl` | True | SSL certificate validation |

## Troubleshooting

### SSL Errors
```python
# Disable SSL verification (not recommended for production)
response = requests.get(url, verify=False)
```

### Blocked by WAF
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}
```

### Large Files
```python
# Skip files larger than 10MB
if int(response.headers.get('content-length', 0)) > 10_000_000:
    return url  # Keep original URL
```
