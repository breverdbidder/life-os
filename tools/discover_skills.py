#!/usr/bin/env python3
"""
Discover Skills Tool
Allows agents to discover and select appropriate skills before executing workflows.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import json

class SkillDiscovery:
    """Tool for discovering available skills in /mnt/skills/"""
    
    SKILLS_BASE = Path("/mnt/skills")
    
    def __init__(self):
        self.skills = []
        self._scan_skills()
    
    def _scan_skills(self):
        """Scan all skill directories and extract metadata"""
        if not self.SKILLS_BASE.exists():
            return
        
        # Scan public, examples, and user skills
        for category in ['public', 'examples', 'user', 'private']:
            category_path = self.SKILLS_BASE / category
            if not category_path.exists():
                continue
            
            for skill_dir in category_path.iterdir():
                if not skill_dir.is_dir():
                    continue
                
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    metadata = self._parse_skill_metadata(skill_md, category, skill_dir.name)
                    if metadata:
                        self.skills.append(metadata)
    
    def _parse_skill_metadata(self, skill_file: Path, category: str, skill_name: str) -> Optional[Dict]:
        """Parse SKILL.md to extract name and description"""
        try:
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract name (first # heading)
            name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            name = name_match.group(1).strip() if name_match else skill_name
            
            # Extract description (content between name and first ##)
            desc_match = re.search(r'^#\s+.+\n\n(.+?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else "No description available"
            
            # Clean up description (first 200 chars)
            description = ' '.join(description.split())[:200]
            
            return {
                'name': name,
                'skill_id': skill_name,
                'category': category,
                'description': description,
                'path': str(skill_file.parent),
                'skill_file': str(skill_file)
            }
        except Exception as e:
            print(f"Warning: Failed to parse {skill_file}: {e}")
            return None
    
    def list_all(self) -> List[Dict]:
        """List all available skills"""
        return self.skills
    
    def search(self, query: str) -> List[Dict]:
        """Search skills by name or description"""
        query_lower = query.lower()
        return [
            skill for skill in self.skills
            if query_lower in skill['name'].lower() 
            or query_lower in skill['description'].lower()
            or query_lower in skill['skill_id'].lower()
        ]
    
    def get_by_id(self, skill_id: str) -> Optional[Dict]:
        """Get specific skill by ID"""
        for skill in self.skills:
            if skill['skill_id'] == skill_id:
                return skill
        return None
    
    def format_for_agent(self, skills: List[Dict] = None) -> str:
        """Format skills list for agent consumption"""
        if skills is None:
            skills = self.skills
        
        if not skills:
            return "No skills found."
        
        output = f"Found {len(skills)} skill(s):\n\n"
        
        for i, skill in enumerate(skills, 1):
            output += f"{i}. **{skill['name']}** ({skill['category']})\n"
            output += f"   ID: {skill['skill_id']}\n"
            output += f"   Description: {skill['description']}\n"
            output += f"   Path: {skill['path']}\n\n"
        
        return output
    
    def to_json(self, skills: List[Dict] = None) -> str:
        """Return skills as JSON"""
        if skills is None:
            skills = self.skills
        return json.dumps(skills, indent=2)


def discover_skills(query: Optional[str] = None, format: str = "text") -> str:
    """
    Main entry point for skill discovery.
    
    Args:
        query: Optional search query to filter skills
        format: Output format - 'text' or 'json'
    
    Returns:
        Formatted string of available skills
    """
    discovery = SkillDiscovery()
    
    if query:
        results = discovery.search(query)
        prefix = f"Skills matching '{query}':\n\n"
    else:
        results = discovery.list_all()
        prefix = "All available skills:\n\n"
    
    if format == "json":
        return discovery.to_json(results)
    else:
        return prefix + discovery.format_for_agent(results)


if __name__ == "__main__":
    import sys
    
    # Command-line usage
    query = sys.argv[1] if len(sys.argv) > 1 else None
    format_type = sys.argv[2] if len(sys.argv) > 2 else "text"
    
    print(discover_skills(query, format_type))
