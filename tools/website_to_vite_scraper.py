#!/usr/bin/env python3
"""
Website to Vite Scraper v1.0
Converts any website into a deployable Vite project with all assets.

Usage:
    python website_to_vite_scraper.py https://example.com output-dir
    
Or as module:
    from website_to_vite_scraper import WebsiteToViteScraper
    scraper = WebsiteToViteScraper("https://example.com", "output-dir")
    scraper.scrape()
"""

import os
import re
import sys
import json
import hashlib
import argparse
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup


class WebsiteToViteScraper:
    """Scrapes a website and converts it to a Vite-ready project structure."""
    
    def __init__(self, base_url: str, output_dir: str = "vite-project", 
                 max_workers: int = 5, timeout: int = 30):
        """
        Initialize the scraper.
        
        Args:
            base_url: The website URL to scrape
            output_dir: Output directory for the Vite project
            max_workers: Number of parallel download threads
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.timeout = timeout
        
        # Track assets by type
        self.assets: Dict[str, List[str]] = {
            'images': [],
            'css': [],
            'js': [],
            'fonts': []
        }
        
        # Track scraped pages to avoid duplicates
        self.scraped_pages: Set[str] = set()
        
        # Track downloaded assets to avoid duplicates
        self.downloaded_assets: Set[str] = set()
        
        # HTTP session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
    def scrape(self, pages: Optional[List[str]] = None) -> None:
        """
        Main scraping method.
        
        Args:
            pages: Optional list of specific pages to scrape. 
                   If None, scrapes only the base URL.
        """
        print(f"\n🚀 Starting scrape of {self.base_url}")
        print(f"📁 Output directory: {self.output_dir}\n")
        
        # Create Vite project structure
        self.create_vite_structure()
        
        # Scrape pages
        pages_to_scrape = pages or [self.base_url]
        for page in pages_to_scrape:
            self.scrape_page(page)
        
        # Create project files
        self.create_package_json()
        self.create_vite_config()
        self.create_main_js()
        self.create_readme()
        self.create_gitignore()
        
        print(f"\n✅ Scraping complete!")
        print(f"📊 Stats:")
        print(f"   - Pages: {len(self.scraped_pages)}")
        print(f"   - Images: {len(self.assets['images'])}")
        print(f"   - CSS files: {len(self.assets['css'])}")
        print(f"   - JS files: {len(self.assets['js'])}")
        print(f"   - Fonts: {len(self.assets['fonts'])}")
        print(f"\n📌 Next steps:")
        print(f"   cd {self.output_dir}")
        print(f"   npm install")
        print(f"   npm run dev")
        
    def create_vite_structure(self) -> None:
        """Create the Vite project directory structure."""
        directories = [
            self.output_dir,
            f"{self.output_dir}/src",
            f"{self.output_dir}/src/assets",
            f"{self.output_dir}/src/assets/images",
            f"{self.output_dir}/src/assets/css",
            f"{self.output_dir}/src/assets/js",
            f"{self.output_dir}/src/assets/fonts",
            f"{self.output_dir}/src/pages",
            f"{self.output_dir}/public",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        print("📂 Created Vite project structure")
        
    def scrape_page(self, url: str) -> None:
        """
        Scrape a single page and its assets.
        
        Args:
            url: The page URL to scrape
        """
        # Normalize URL
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
            
        # Skip if already scraped
        if url in self.scraped_pages:
            return
            
        self.scraped_pages.add(url)
        print(f"📄 Scraping page: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"   ❌ Error fetching page: {e}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Download and process assets
        self._process_images(soup)
        self._process_stylesheets(soup, url)
        self._process_scripts(soup)
        self._process_inline_styles(soup, url)
        
        # Generate HTML file
        self._save_html(soup, url)
        
    def _process_images(self, soup: BeautifulSoup) -> None:
        """Download all images from the page."""
        images = []
        
        # Find all img tags
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                images.append((img, 'src', src))
                
        # Find all picture source tags
        for source in soup.find_all('source'):
            srcset = source.get('srcset')
            if srcset:
                # Handle srcset with multiple images
                for src in srcset.split(','):
                    src = src.strip().split()[0]
                    images.append((source, 'srcset', src))
                    
        # Download images in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for element, attr, src in images:
                if src and not src.startswith('data:'):
                    future = executor.submit(self.download_asset, src, 'images')
                    futures[future] = (element, attr, src)
                    
            for future in as_completed(futures):
                element, attr, original_src = futures[future]
                try:
                    new_path = future.result()
                    if new_path != original_src:
                        element[attr] = new_path
                except Exception as e:
                    print(f"   ⚠️ Error processing image: {e}")
                    
    def _process_stylesheets(self, soup: BeautifulSoup, page_url: str) -> None:
        """Download and process all stylesheets."""
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                new_path = self._download_and_process_css(href, page_url)
                if new_path:
                    link['href'] = new_path
                    
    def _download_and_process_css(self, css_url: str, page_url: str) -> Optional[str]:
        """Download CSS file and process its internal URLs."""
        full_url = urljoin(page_url, css_url)
        
        if full_url in self.downloaded_assets:
            # Return existing path
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path) or 'style.css'
            return f"/src/assets/css/{filename}"
            
        try:
            response = self.session.get(full_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Process CSS content to download referenced assets
            css_content = self.process_css(response.text, full_url)
            
            # Generate filename
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path) or 'style.css'
            if not filename.endswith('.css'):
                filename += '.css'
                
            # Make filename unique if needed
            filename = self._get_unique_filename(filename, 'css')
            
            # Save CSS file
            css_path = f"{self.output_dir}/src/assets/css/{filename}"
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
                
            self.assets['css'].append(filename)
            self.downloaded_assets.add(full_url)
            print(f"   📝 Downloaded CSS: {filename}")
            
            return f"/src/assets/css/{filename}"
            
        except Exception as e:
            print(f"   ⚠️ Error downloading CSS {css_url}: {e}")
            return None
            
    def _process_scripts(self, soup: BeautifulSoup) -> None:
        """Download all external scripts."""
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src and not src.startswith('data:'):
                new_path = self.download_asset(src, 'js')
                if new_path != src:
                    script['src'] = new_path
                    
    def _process_inline_styles(self, soup: BeautifulSoup, page_url: str) -> None:
        """Process inline style tags for URLs."""
        for style in soup.find_all('style'):
            if style.string:
                style.string = self.process_css(style.string, page_url)
                
        # Process style attributes
        for element in soup.find_all(style=True):
            element['style'] = self.process_css(element['style'], page_url)
            
    def _save_html(self, soup: BeautifulSoup, url: str) -> None:
        """Save the processed HTML page."""
        # Determine filename
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path or path == self.base_url.strip('/'):
            filename = 'index.html'
        else:
            # Convert path to filename
            filename = path.replace('/', '-')
            if not filename.endswith('.html'):
                filename += '.html'
                
        # Create HTML template with Vite integration
        html_template = self._create_html_template(soup, filename)
        
        # Save to appropriate location
        if filename == 'index.html':
            html_path = f"{self.output_dir}/index.html"
        else:
            html_path = f"{self.output_dir}/src/pages/{filename}"
            
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
            
        print(f"   💾 Saved: {filename}")
        
    def _create_html_template(self, soup: BeautifulSoup, filename: str) -> str:
        """Create Vite-compatible HTML template."""
        # Get or create head
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
                
        # Add Vite module script if this is index.html
        if filename == 'index.html':
            # Check if main.js script already exists
            existing_main = soup.find('script', {'src': '/src/main.js'})
            if not existing_main:
                main_script = soup.new_tag('script', type='module', src='/src/main.js')
                body = soup.find('body')
                if body:
                    body.append(main_script)
                    
        # Pretty print HTML
        return soup.prettify()
        
    def download_asset(self, url: str, asset_type: str) -> str:
        """
        Download asset (image, css, js, font, etc.)
        
        Args:
            url: Asset URL (can be relative or absolute)
            asset_type: Type of asset (images, css, js, fonts)
            
        Returns:
            New local path to the asset, or original URL if download failed
        """
        # Skip data URLs
        if url.startswith('data:'):
            return url
            
        full_url = urljoin(self.base_url, url)
        
        # Skip if already downloaded
        if full_url in self.downloaded_assets:
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path) or 'asset'
            return f"/src/assets/{asset_type}/{filename}"
            
        try:
            response = self.session.get(full_url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Check file size (skip files > 50MB)
            content_length = int(response.headers.get('content-length', 0))
            if content_length > 50_000_000:
                print(f"   ⚠️ File too large, skipping: {url}")
                return url
                
            # Generate filename
            parsed = urlparse(full_url)
            filename = os.path.basename(parsed.path) or 'asset'
            
            # Ensure proper extension
            if not os.path.splitext(filename)[1]:
                ext_map = {
                    'images': self._guess_image_extension(response),
                    'css': '.css',
                    'js': '.js',
                    'fonts': '.woff2'
                }
                filename += ext_map.get(asset_type, '')
                
            # Make filename unique if needed
            filename = self._get_unique_filename(filename, asset_type)
            
            # Save file
            asset_path = f"{self.output_dir}/src/assets/{asset_type}/{filename}"
            
            with open(asset_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.assets[asset_type].append(filename)
            self.downloaded_assets.add(full_url)
            
            return f"/src/assets/{asset_type}/{filename}"
            
        except Exception as e:
            print(f"   ⚠️ Error downloading {url}: {e}")
            return url
            
    def _guess_image_extension(self, response: requests.Response) -> str:
        """Guess image extension from content type."""
        content_type = response.headers.get('content-type', '').lower()
        ext_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            'image/x-icon': '.ico',
        }
        return ext_map.get(content_type, '.jpg')
        
    def _get_unique_filename(self, filename: str, asset_type: str) -> str:
        """Generate unique filename to avoid collisions."""
        base, ext = os.path.splitext(filename)
        counter = 1
        original = filename
        
        while filename in self.assets[asset_type]:
            filename = f"{base}_{counter}{ext}"
            counter += 1
            
        return filename
        
    def process_css(self, css_content: str, base_url: str) -> str:
        """
        Process CSS and download referenced assets.
        
        Args:
            css_content: The CSS content to process
            base_url: Base URL for resolving relative paths
            
        Returns:
            Processed CSS with updated asset paths
        """
        # Find URLs in CSS (background images, fonts, etc.)
        url_pattern = r'url\(["\']?([^"\')]+)["\']?\)'
        
        def replace_url(match):
            url = match.group(1)
            
            # Skip data URLs
            if url.startswith('data:'):
                return match.group(0)
                
            full_url = urljoin(base_url, url)
            
            # Determine asset type
            url_lower = url.lower()
            if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
                new_path = self.download_asset(full_url, 'images')
            elif any(ext in url_lower for ext in ['.woff', '.woff2', '.ttf', '.eot', '.otf']):
                new_path = self.download_asset(full_url, 'fonts')
            else:
                # Default to images for unknown
                new_path = self.download_asset(full_url, 'images')
                
            return f'url("{new_path}")'
            
        return re.sub(url_pattern, replace_url, css_content)
        
    def create_package_json(self) -> None:
        """Create package.json for the Vite project."""
        # Extract domain for project name
        parsed = urlparse(self.base_url)
        project_name = parsed.netloc.replace('.', '-').replace(':', '-')
        
        package_json = {
            "name": project_name,
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "devDependencies": {
                "vite": "^5.0.0"
            }
        }
        
        with open(f"{self.output_dir}/package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
            
        print("📦 Created package.json")
        
    def create_vite_config(self) -> None:
        """Create vite.config.js."""
        vite_config = '''import { defineConfig } from 'vite'

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    minify: 'terser',
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      }
    }
  },
  server: {
    port: 3000,
    open: true
  }
})
'''
        with open(f"{self.output_dir}/vite.config.js", 'w') as f:
            f.write(vite_config)
            
        print("⚙️ Created vite.config.js")
        
    def create_main_js(self) -> None:
        """Create src/main.js entry point."""
        # Import all CSS files
        css_imports = '\n'.join([
            f"import './assets/css/{css}'"
            for css in self.assets['css']
        ])
        
        main_js = f'''// Main entry point for Vite
{css_imports}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {{
  console.log('Site loaded via Vite')
}})
'''
        with open(f"{self.output_dir}/src/main.js", 'w') as f:
            f.write(main_js)
            
        print("📝 Created src/main.js")
        
    def create_readme(self) -> None:
        """Create README.md with project info."""
        readme = f'''# {self.base_url} - Vite Project

This project was scraped from [{self.base_url}]({self.base_url}) and converted to a Vite project.

## Quick Start

```bash
npm install
npm run dev
```

## Build for Production

```bash
npm run build
npm run preview
```

## Project Stats

- **Source URL:** {self.base_url}
- **Pages scraped:** {len(self.scraped_pages)}
- **Images:** {len(self.assets['images'])}
- **CSS files:** {len(self.assets['css'])}
- **JS files:** {len(self.assets['js'])}
- **Fonts:** {len(self.assets['fonts'])}

## Project Structure

```
{self.output_dir}/
├── index.html          # Main entry point
├── package.json        # npm dependencies
├── vite.config.js      # Vite configuration
├── public/             # Static assets (copied as-is)
└── src/
    ├── main.js         # JS entry point
    ├── assets/
    │   ├── css/        # Stylesheets
    │   ├── images/     # Images
    │   ├── js/         # Scripts
    │   └── fonts/      # Web fonts
    └── pages/          # Additional HTML pages
```

## Deployment

### Cloudflare Pages
```bash
npm run build
# Upload dist/ folder to Cloudflare Pages
```

### GitHub Pages
```bash
npm run build
# Push dist/ folder to gh-pages branch
```

---
Generated by WebsiteToViteScraper v1.0
'''
        with open(f"{self.output_dir}/README.md", 'w') as f:
            f.write(readme)
            
        print("📄 Created README.md")
        
    def create_gitignore(self) -> None:
        """Create .gitignore file."""
        gitignore = '''# Dependencies
node_modules/

# Build output
dist/

# Local env files
.env
.env.local
.env.*.local

# Editor directories
.idea/
.vscode/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
'''
        with open(f"{self.output_dir}/.gitignore", 'w') as f:
            f.write(gitignore)
            
        print("🙈 Created .gitignore")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape a website and convert it to a Vite project'
    )
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument(
        '-o', '--output', 
        default='vite-project',
        help='Output directory (default: vite-project)'
    )
    parser.add_argument(
        '-p', '--pages',
        nargs='*',
        help='Additional pages to scrape (relative or absolute URLs)'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=5,
        help='Number of parallel download workers (default: 5)'
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    scraper = WebsiteToViteScraper(
        base_url=args.url,
        output_dir=args.output,
        max_workers=args.workers,
        timeout=args.timeout
    )
    
    pages = [args.url]
    if args.pages:
        pages.extend(args.pages)
        
    scraper.scrape(pages)


if __name__ == '__main__':
    main()
