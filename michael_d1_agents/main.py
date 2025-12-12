#!/usr/bin/env python3
"""
Michael Shapira D1 Pathway - Main Entry Point

Usage:
    python main.py                      # Interactive mode
    python main.py "your query here"    # Single query mode
    python main.py --status             # Show comprehensive status
"""

import sys
import json
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, '.')

from orchestrator.langgraph_orchestrator import MichaelD1Orchestrator


def print_banner():
    """Print application banner"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║  🏊 MICHAEL SHAPIRA D1 PATHWAY - Multi-Agent AI System 🏊    ║
║  ─────────────────────────────────────────────────────────    ║
║  Satellite Beach HS → University of Florida (Class 2027)      ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_help():
    """Print available commands"""
    print("""
📌 Available Commands:
  • Type any question about Michael's D1 pathway
  • "status" - Show comprehensive status across all domains
  • "agents" - List available agents
  • "profile" - Show Michael's current profile
  • "quit" or "exit" - Exit the program

💡 Example Queries:
  • "Help me draft an email to UF swimming"
  • "What should Michael eat before the meet?"
  • "Is Michael NCAA eligible?"
  • "Plan a visit to University of Florida"
  • "Get me the Chabad contact at UF"
    """)


def show_agents(orchestrator: MichaelD1Orchestrator):
    """Show available agents"""
    print("\n🤖 Available Agents:")
    for name, agent in orchestrator.agents.items():
        print(f"   • {name.upper()}: {agent.__class__.__name__}")


def show_profile(orchestrator: MichaelD1Orchestrator):
    """Show Michael's profile"""
    state = orchestrator.base_state
    print(f"""
👤 MICHAEL SHAPIRA PROFILE
═══════════════════════════════════════
Name:        {state['swimmer_name']}
Grade:       {state['current_grade']} (Class of {state['graduation_year']})
GPA:         {state['gpa']}
SAT:         {state['sat_score']}
NCAA Status: {'Eligible ✅' if state['ncaa_eligible'] else 'Review Needed ⚠️'}

🏊 Events: {', '.join(state['events'])}

⏱️ Personal Bests:
   50 Free:   {state['personal_bests']['50 Free']}
   100 Free:  {state['personal_bests']['100 Free']}
   100 Fly:   {state['personal_bests']['100 Fly']}
   100 Back:  {state['personal_bests']['100 Back']}

🎯 Target Schools: {', '.join(state['target_schools'])}

✡️ Observance: Kosher={state['kosher_required']}, Shabbat={state['shabbat_observant']}
═══════════════════════════════════════
    """)


def show_status(orchestrator: MichaelD1Orchestrator):
    """Show comprehensive status"""
    print("\n📊 COMPREHENSIVE STATUS")
    print("═" * 50)
    
    status = orchestrator.get_comprehensive_status()
    
    for domain, data in status['domains'].items():
        print(f"\n🔹 {domain.upper()}")
        output = data.get('output', {})
        if isinstance(output, dict):
            for key, value in list(output.items())[:3]:
                if isinstance(value, (str, int, float, bool)):
                    print(f"   {key}: {value}")
                elif isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"   {key}: {len(value)} fields")


def process_query(orchestrator: MichaelD1Orchestrator, query: str):
    """Process and display query results"""
    result = orchestrator.process_query(query)
    
    print(f"\n🎯 Detected Intent: {result['detected_intent'].upper()}")
    print(f"🤖 Agents Used: {', '.join(result['agents_used'])}")
    print("-" * 50)
    
    # Show primary response
    primary = result['primary_response']
    print(f"\n📋 Action: {primary.get('action', 'N/A')}")
    
    output = primary.get('output', {})
    if isinstance(output, dict):
        for key, value in output.items():
            if isinstance(value, (str, int, float, bool)):
                print(f"   • {key}: {value}")
            elif isinstance(value, list):
                print(f"   • {key}:")
                for item in value[:5]:
                    if isinstance(item, dict):
                        print(f"      - {list(item.values())[0] if item else item}")
                    else:
                        print(f"      - {item}")
            elif isinstance(value, dict):
                print(f"   • {key}:")
                for k, v in list(value.items())[:3]:
                    print(f"      - {k}: {v}")
    
    # Show supplementary if available
    if result.get('supplementary'):
        print("\n📎 Supplementary Info:")
        for agent_name, data in result['supplementary'].items():
            if data:
                print(f"   From {agent_name}: {data.get('action', 'N/A')}")


def interactive_mode():
    """Run in interactive mode"""
    print_banner()
    print_help()
    
    orchestrator = MichaelD1Orchestrator()
    print("✅ Orchestrator initialized\n")
    
    while True:
        try:
            query = input("\n💬 Ask: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Go Gators! 🐊")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            if query.lower() == 'status':
                show_status(orchestrator)
                continue
            
            if query.lower() == 'agents':
                show_agents(orchestrator)
                continue
            
            if query.lower() == 'profile':
                show_profile(orchestrator)
                continue
            
            process_query(orchestrator, query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Go Gators! 🐊")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == '--status':
            orchestrator = MichaelD1Orchestrator()
            show_status(orchestrator)
        elif arg == '--profile':
            orchestrator = MichaelD1Orchestrator()
            show_profile(orchestrator)
        elif arg == '--help' or arg == '-h':
            print_help()
        else:
            # Single query mode
            orchestrator = MichaelD1Orchestrator()
            query = ' '.join(sys.argv[1:])
            process_query(orchestrator, query)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
