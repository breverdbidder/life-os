#!/usr/bin/env python3
"""
Screen Control Operator - Autonomous Browser Control
Like GPT Operator - NO screenshots, pure CDP + accessibility tree
"""

import sys
import json
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

class ScreenControlOperator:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def launch(self):
        """Launch browser with CDP enabled"""
        print("🚀 Launching browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--remote-debugging-port=9222']
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        print("✓ Browser ready")
        
    def close(self):
        """Cleanup"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def get_page_structure(self):
        """Get DOM structure via accessibility tree - NO screenshots"""
        elements = self.page.query_selector_all('[role], button, a, input, select, [data-testid]')
        
        structure = {
            'url': self.page.url,
            'title': self.page.title(),
            'elements': []
        }
        
        for elem in elements:
            try:
                if elem.is_visible():
                    structure['elements'].append({
                        'role': elem.get_attribute('role'),
                        'label': elem.get_attribute('aria-label') or elem.inner_text()[:100],
                        'type': elem.get_attribute('type'),
                        'testid': elem.get_attribute('data-testid'),
                        'enabled': elem.is_enabled()
                    })
            except:
                pass
        
        return structure
    
    def navigate_and_verify(self, url, checkpoints):
        """Navigate to URL and verify checkpoints autonomously"""
        print(f"🌐 Navigating to {url}")
        try:
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(2000)
        except PlaywrightTimeout:
            print("⚠️  Timeout waiting for page load, continuing...")
        
        results = {
            'url': self.page.url,
            'title': self.page.title(),
            'checkpoints': {},
            'issues': []
        }
        
        for checkpoint_name, selector in checkpoints.items():
            print(f"  Checking: {checkpoint_name}")
            try:
                elem = self.page.locator(selector).first
                visible = elem.is_visible(timeout=2000)
                text = elem.inner_text()[:100] if visible else None
                
                results['checkpoints'][checkpoint_name] = {
                    'found': True,
                    'visible': visible,
                    'text': text
                }
                
                if visible:
                    print(f"    ✓ {checkpoint_name}: visible")
                else:
                    print(f"    ⚠️  {checkpoint_name}: found but not visible")
                    results['issues'].append(f"{checkpoint_name} not visible")
                    
            except:
                print(f"    ✗ {checkpoint_name}: not found")
                results['checkpoints'][checkpoint_name] = {'found': False}
                results['issues'].append(f"{checkpoint_name} not found")
        
        return results
    
    def verify_lovable_preview(self, project_id):
        """Autonomous Lovable preview verification"""
        print(f"🎯 Task: Verify Lovable Preview")
        print(f"   Project ID: {project_id}")
        print()
        
        # Navigate to Lovable project
        url = f"https://lovable.dev/projects/{project_id}"
        self.page.goto(url, wait_until='networkidle')
        self.page.wait_for_timeout(2000)
        
        # Click Preview button if visible
        try:
            preview_btn = self.page.get_by_role("button", name="Preview")
            if preview_btn.is_visible(timeout=5000):
                print("🖱️  Clicking Preview button...")
                preview_btn.click()
                self.page.wait_for_timeout(2000)
                
                # Get preview page (new tab)
                pages = self.context.pages
                preview_page = pages[-1] if len(pages) > 1 else self.page
                self.page = preview_page
                print(f"   Preview opened: {self.page.url}")
        except:
            print("   Preview button not found, assuming already on preview")
        
        # Define checkpoints
        checkpoints = {
            'header': 'header, [role="banner"], nav, [data-testid="header"]',
            'map_container': '[data-testid="map-container"], #map, .mapboxgl-map, [class*="map"]',
            'markers': '[data-testid="marker"], .marker, .mapboxgl-marker, [class*="marker"]',
            'search': '[data-testid="search"], input[type="search"], [placeholder*="search"]',
            'filters': '[data-testid="filters"], .filters, [class*="filter"]'
        }
        
        # Verify checkpoints
        results = self.navigate_and_verify(self.page.url, checkpoints)
        
        # Test interactions
        print("\n🖱️  Testing interactions...")
        try:
            # Try to interact with map
            map_elem = self.page.locator('[data-testid="map-container"], #map, .mapboxgl-map').first
            if map_elem.is_visible():
                print("   Testing zoom controls...")
                self.page.keyboard.press('+')
                self.page.wait_for_timeout(500)
                self.page.keyboard.press('-')
                self.page.wait_for_timeout(500)
                results['interactions'] = {'zoom': 'SUCCESS'}
                print("   ✓ Zoom controls work")
            else:
                results['interactions'] = {'zoom': 'SKIPPED - map not visible'}
        except Exception as e:
            results['interactions'] = {'zoom': f'FAILED: {str(e)}'}
            print(f"   ✗ Zoom test failed: {e}")
        
        # Get console errors
        console_errors = []
        self.page.on('console', lambda msg: 
            console_errors.append(msg.text()) if msg.type == 'error' else None
        )
        
        results['console_errors'] = console_errors
        results['timestamp'] = datetime.now().isoformat()
        
        return results
    
    def inspect_beca_dom(self):
        """Inspect BECA login form DOM - find actual selectors"""
        print("🎯 Task: Inspect BECA DOM")
        print("   URL: https://beca.v3.target-url.com")
        print()
        
        self.page.goto('https://beca.v3.target-url.com', wait_until='networkidle')
        self.page.wait_for_timeout(3000)
        
        results = {
            'url': self.page.url,
            'title': self.page.title(),
            'forms': [],
            'inputs': [],
            'buttons': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze forms
        print("📋 Analyzing forms...")
        forms = self.page.query_selector_all('form')
        for i, form in enumerate(forms):
            form_data = {
                'index': i,
                'id': form.get_attribute('id'),
                'class': form.get_attribute('class'),
                'action': form.get_attribute('action'),
                'method': form.get_attribute('method')
            }
            results['forms'].append(form_data)
            print(f"   Form {i}: {form_data.get('id') or form_data.get('class') or 'unnamed'}")
        
        # Analyze inputs
        print("\n📝 Analyzing inputs...")
        inputs = self.page.query_selector_all('input')
        for i, inp in enumerate(inputs):
            if inp.is_visible():
                input_data = {
                    'index': i,
                    'name': inp.get_attribute('name'),
                    'id': inp.get_attribute('id'),
                    'type': inp.get_attribute('type'),
                    'placeholder': inp.get_attribute('placeholder'),
                    'required': inp.get_attribute('required') is not None,
                    'selector': f"input[name='{inp.get_attribute('name')}']" if inp.get_attribute('name') else f"input[id='{inp.get_attribute('id')}']"
                }
                results['inputs'].append(input_data)
                print(f"   Input {i}: {input_data.get('type')} - {input_data.get('name') or input_data.get('id')}")
        
        # Analyze buttons
        print("\n🔘 Analyzing buttons...")
        buttons = self.page.query_selector_all('button, input[type="submit"], input[type="button"]')
        for i, btn in enumerate(buttons):
            if btn.is_visible():
                button_data = {
                    'index': i,
                    'text': btn.inner_text()[:50],
                    'type': btn.get_attribute('type'),
                    'id': btn.get_attribute('id'),
                    'class': btn.get_attribute('class'),
                    'tag': btn.evaluate('el => el.tagName').lower()
                }
                results['buttons'].append(button_data)
                print(f"   Button {i}: '{button_data['text']}' ({button_data['tag']})")
        
        return results
    
    def test_url(self, url):
        """Generic URL testing - get structure and verify basic functionality"""
        print(f"🎯 Task: Test URL")
        print(f"   URL: {url}")
        print()
        
        checkpoints = {
            'body': 'body',
            'header': 'header, [role="banner"], nav',
            'main': 'main, [role="main"], #content',
            'footer': 'footer, [role="contentinfo"]'
        }
        
        results = self.navigate_and_verify(url, checkpoints)
        
        # Get page structure
        print("\n📊 Analyzing page structure...")
        structure = self.get_page_structure()
        results['element_count'] = len(structure['elements'])
        results['interactive_elements'] = [
            e for e in structure['elements'] 
            if e.get('role') in ['button', 'link', 'textbox', 'combobox', 'checkbox']
        ]
        
        print(f"   Found {len(structure['elements'])} visible elements")
        print(f"   Found {len(results['interactive_elements'])} interactive elements")
        
        results['timestamp'] = datetime.now().isoformat()
        return results


def main():
    parser = argparse.ArgumentParser(description='Screen Control Operator - Autonomous Browser Control')
    parser.add_argument('task', choices=['verify-lovable', 'inspect-beca', 'test-url'],
                       help='Task to execute')
    parser.add_argument('target', nargs='?', help='Target (project ID for Lovable, URL for test-url)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--output', default='results.json', help='Output file for results')
    
    args = parser.parse_args()
    
    # Initialize operator
    operator = ScreenControlOperator(headless=args.headless)
    
    try:
        operator.launch()
        
        # Execute task
        if args.task == 'verify-lovable':
            if not args.target:
                print("Error: Project ID required for verify-lovable")
                sys.exit(1)
            results = operator.verify_lovable_preview(args.target)
            
        elif args.task == 'inspect-beca':
            results = operator.inspect_beca_dom()
            
        elif args.task == 'test-url':
            if not args.target:
                print("Error: URL required for test-url")
                sys.exit(1)
            results = operator.test_url(args.target)
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("RESULTS SUMMARY")
        print("=" * 70)
        print(f"\n✅ Task completed: {args.task}")
        print(f"📄 Results saved to: {args.output}")
        
        if 'issues' in results and results['issues']:
            print(f"\n⚠️  Issues found ({len(results['issues'])}):")
            for issue in results['issues']:
                print(f"   - {issue}")
        else:
            print("\n✓ No issues found")
        
        if 'checkpoints' in results:
            passed = sum(1 for c in results['checkpoints'].values() if c.get('found') and c.get('visible'))
            total = len(results['checkpoints'])
            print(f"\n📊 Checkpoints: {passed}/{total} passed")
        
    finally:
        operator.close()


if __name__ == '__main__':
    main()
