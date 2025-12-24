#!/usr/bin/env python3
"""
Discover Skills Tool - List available skills for AI agents

This tool scans /mnt/skills/ directories and extracts skill metadata
(name, description, location) to help agents find relevant skills.

Usage:
    python discover_skills.py [--category CATEGORY] [--search TERM]

Examples:
    python discover_skills.py                    # List all skills
    python discover_skills.py --category docx    # Filter by category
    python discover_skills.py --search "create"  # Search descriptions
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional


class SkillDiscovery:
    """Discover and catalog available skills for AI agents."""
    
    SKILLS_BASE = Path("/mnt/skills")
    SKILL_DIRS = ["public", "examples", "private", "user"]
    
    def __init__(self):
        self.skills = []
    
    def parse_skill_md(self, skill_path: Path) -> Optional[Dict[str, str]]:
        """Extract name and description from SKILL.md file."""
        try:
            content = skill_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            name = None
            description = None
            
            # Parse markdown structure
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Look for <name> tag or # Name header
                if line.startswith('<name>'):
                    name = line.replace('<name>', '').replace('</name>', '').strip()
                elif line.startswith('# ') and not name:
                    name = line[2:].strip()
                
                # Look for <description> tag or description paragraph
                if line.startswith('<description>'):
                    description = line.replace('<description>', '').replace('</description>', '').strip()
                elif name and not description and line and not line.startswith('#') and not line.startswith('<'):
                    # First non-empty, non-header line after name
                    description = line
                
                if name and description:
                    break
            
            return {
                'name': name or skill_path.parent.name,
                'description': description or 'No description available',
                'path': str(skill_path.parent),
                'skill_file': str(skill_path)
            }
        except Exception as e:
            return None
    
    def scan_directory(self, category: str) -> List[Dict[str, str]]:
        """Scan a skills category directory for SKILL.md files."""
        category_path = self.SKILLS_BASE / category
        
        if not category_path.exists():
            return []
        
        skills = []
        
        # Walk through directory looking for SKILL.md files
        for skill_dir in category_path.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill_info = self.parse_skill_md(skill_file)
                if skill_info:
                    skill_info['category'] = category
                    skills.append(skill_info)
        
        return skills
    
    def discover_all(self) -> List[Dict[str, str]]:
        """Discover all skills across all categories."""
        all_skills = []
        
        for category in self.SKILL_DIRS:
            skills = self.scan_directory(category)
            all_skills.extend(skills)
        
        return all_skills
    
    def filter_skills(
        self, 
        category: Optional[str] = None,
        search_term: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Filter skills by category and/or search term."""
        skills = self.discover_all()
        
        if category:
            skills = [s for s in skills if s['category'] == category]
        
        if search_term:
            search_lower = search_term.lower()
            skills = [
                s for s in skills 
                if search_lower in s['name'].lower() 
                or search_lower in s['description'].lower()
            ]
        
        return skills
    
    def format_output(self, skills: List[Dict[str, str]], format: str = 'text') -> str:
        """Format skills list for output."""
        if format == 'json':
            return json.dumps(skills, indent=2)
        
        # Text format
        if not skills:
            return "No skills found."
        
        output = []
        output.append("=" * 70)
        output.append(f"AVAILABLE SKILLS ({len(skills)} found)")
        output.append("=" * 70)
        output.append("")
        
        for skill in sorted(skills, key=lambda x: (x['category'], x['name'])):
            output.append(f"📦 {skill['name']}")
            output.append(f"   Category: {skill['category']}")
            output.append(f"   Location: {skill['path']}")
            output.append(f"   Description: {skill['description']}")
            output.append("")
        
        output.append(f"Total: {len(skills)} skills available")
        output.append("")
        output.append("To use a skill: view {skill_file}")
        
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Discover available AI agent skills',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          List all skills
  %(prog)s --category public        Filter by category
  %(prog)s --search "create pdf"    Search by keyword
  %(prog)s --format json            Output as JSON
        """
    )
    
    parser.add_argument(
        '--category',
        choices=['public', 'examples', 'private', 'user'],
        help='Filter by skill category'
    )
    
    parser.add_argument(
        '--search',
        help='Search skills by name or description'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Discover skills
    discovery = SkillDiscovery()
    skills = discovery.filter_skills(
        category=args.category,
        search_term=args.search
    )
    
    # Output results
    output = discovery.format_output(skills, format=args.format)
    print(output)
    
    return 0 if skills else 1


if __name__ == '__main__':
    sys.exit(main())
