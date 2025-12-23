#!/usr/bin/env python3
"""
Generate API library updates using Claude AI
Formats new APIs into proper markdown tables for the library
"""

import argparse
import json
import os
import re
from datetime import datetime

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

def format_api_entry(api: dict) -> str:
    """Format a single API entry as markdown table row"""
    name = api.get("name") or api.get("title", "Unknown")
    url = api.get("url", "#")
    description = api.get("description", "")[:100]
    
    # Clean up description
    description = description.replace("|", "-").replace("\n", " ").strip()
    
    return f"| [{name}]({url}) | {description} |"

def generate_section_with_claude(apis: list, category: str) -> str:
    """Use Claude to generate properly formatted section"""
    if not HAS_ANTHROPIC or not os.environ.get("ANTHROPIC_API_KEY"):
        # Fallback to simple formatting
        return generate_simple_section(apis, category)
    
    client = anthropic.Anthropic()
    
    prompt = f"""Generate a markdown table section for these new APIs in category "{category}".

APIs to add:
{json.dumps(apis, indent=2)}

Format as a markdown table with columns: | API | Description | Cost/Notes |
Keep descriptions concise (under 80 chars).
Add appropriate emoji to section header.
Return ONLY the markdown, no explanation."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Claude API error: {e}")
        return generate_simple_section(apis, category)

def generate_simple_section(apis: list, category: str) -> str:
    """Generate section without Claude"""
    emoji_map = {
        "real-estate": "🏠",
        "e-commerce": "🛒",
        "mcp": "🔌",
        "automation": "🤖",
        "ai": "🧠",
        "social": "📱",
        "data": "📊"
    }
    
    emoji = emoji_map.get(category, "📌")
    
    lines = [
        f"\n### {emoji} New {category.title()} APIs (Auto-discovered {datetime.now().strftime('%Y-%m-%d')})\n",
        "| API | Description |",
        "|-----|-------------|"
    ]
    
    for api in apis:
        lines.append(format_api_entry(api))
    
    return "\n".join(lines)

def update_library(library_path: str, new_apis: list, output_path: str):
    """Update the library with new APIs"""
    
    # Read existing library
    with open(library_path, "r") as f:
        content = f.read()
    
    # Group new APIs by category
    by_category = {}
    for api in new_apis:
        cat = api.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(api)
    
    # Generate new sections
    new_sections = []
    for category, apis in by_category.items():
        if apis:
            section = generate_section_with_claude(apis, category)
            new_sections.append(section)
    
    if new_sections:
        # Find insertion point (before the last ---)
        insertion_point = content.rfind("\n---\n")
        if insertion_point == -1:
            insertion_point = len(content)
        
        # Insert new sections
        new_content = (
            content[:insertion_point] + 
            "\n\n" + 
            "\n".join(new_sections) + 
            "\n" +
            content[insertion_point:]
        )
        
        # Update the "Last Updated" line
        new_content = re.sub(
            r'\*Last Updated:.*\*',
            f'*Last Updated: {datetime.now().strftime("%B %Y")}*',
            new_content
        )
        
        # Write updated library
        with open(output_path, "w") as f:
            f.write(new_content)
        
        print(f"Library updated with {len(new_apis)} new APIs")
    else:
        print("No new APIs to add")
        # Copy existing to output
        with open(output_path, "w") as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Generate library update with Claude")
    parser.add_argument("--new-apis", type=str, required=True, help="New APIs JSON file")
    parser.add_argument("--library", type=str, required=True, help="Existing library path")
    parser.add_argument("--output", type=str, required=True, help="Output library path")
    args = parser.parse_args()
    
    # Load new APIs
    with open(args.new_apis, "r") as f:
        data = json.load(f)
    
    new_apis = data.get("apis", [])
    
    if new_apis:
        update_library(args.library, new_apis, args.output)
    else:
        print("No new APIs found")

if __name__ == "__main__":
    main()
