"""
WhatsApp Hub - Skill Router Agent
Routes analyzed attachments to appropriate skills or triggers skill creator
"""

import os
import asyncio
import json
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from supabase import create_client, Client
import httpx

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class RoutingAction(Enum):
    """Possible routing actions"""
    ROUTE_EXISTING = "route_existing"  # Route to existing skill
    CREATE_SKILL = "create_skill"      # Trigger skill-creator
    MANUAL_REVIEW = "manual_review"    # Human review needed

@dataclass
class RoutingDecision:
    """Routing decision for an attachment"""
    attachment_id: str
    analysis_id: str
    action: str  # RoutingAction value
    target_skill: Optional[str] = None
    processing_workflow: Optional[str] = None
    priority: int = 3  # 1-5
    ecosystem_target: Optional[str] = None
    reasoning: Optional[str] = None

class SkillRouterAgent:
    """
    Routes attachments to skills based on analysis
    
    Routing Logic:
    - Confidence ≥ 0.7 AND skill exists → route_existing
    - Confidence ≥ 0.7 AND skill missing → create_skill
    - Confidence < 0.7 → manual_review
    
    Priority Calculation:
    5 = Critical (property_analysis, construction_plans)
    4 = High (financial_docs, property_photos)
    3 = Medium (swim_results, general tracking)
    2 = Low (personal photos, misc documents)
    1 = Archive only (no immediate action)
    """
    
    # Priority mapping
    PRIORITY_MAP = {
        "property_analysis": 5,      # BidDeed.AI core
        "construction_plans": 5,     # SPD core
        "financial_docs": 4,         # Tax optimization
        "property_photos": 4,        # Real estate intelligence
        "swim_results": 3,           # Michael tracking
        "swim_meet_photos": 3,       # Swim tracking
        "legal_docs": 3,             # Document archive
        "unknown": 1                 # Archive only
    }
    
    # Workflow mapping
    WORKFLOW_MAP = {
        "excel_processor/property_data": "biddeed_foreclosure_pipeline.yml",
        "pdf_processor/construction_plans": "spd_construction_takeoff.yml",
        "excel_processor/swim_results": "michael_d1_tracking.yml",
        "image_processor/swim_meet_photos": "michael_d1_tracking.yml",
        "excel_processor/financial_docs": "tax_insurance_optimizer.yml"
    }
    
    # Ecosystem targets
    ECOSYSTEM_MAP = {
        "property_analysis": "BidDeed.AI",
        "construction_plans": "SPD Site Plan Dev",
        "swim_results": "Life OS - Michael D1",
        "swim_meet_photos": "Life OS - Michael D1",
        "financial_docs": "Tax Insurance Optimizer",
        "property_photos": "BidDeed.AI - Property Intel",
        "legal_docs": "Document Archive"
    }
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.http_client = httpx.AsyncClient()
    
    async def route_attachment(self, attachment_id: str) -> RoutingDecision:
        """
        Route an attachment based on its analysis
        
        Steps:
        1. Fetch analysis result
        2. Check confidence threshold
        3. Verify skill exists
        4. Calculate priority
        5. Determine workflow
        6. Create routing decision
        """
        # Fetch analysis
        analysis = self.supabase.table("attachment_analysis")\
            .select("*")\
            .eq("attachment_id", attachment_id)\
            .order("analyzed_at", desc=True)\
            .limit(1)\
            .execute()
        
        if not analysis.data:
            raise ValueError(f"No analysis found for attachment {attachment_id}")
        
        analysis_data = analysis.data[0]
        analysis_id = analysis_data['id']
        detected_purpose = analysis_data['detected_purpose']
        confidence = analysis_data['confidence']
        
        # Step 1: Check confidence threshold
        if confidence < 0.7:
            return RoutingDecision(
                attachment_id=attachment_id,
                analysis_id=analysis_id,
                action=RoutingAction.MANUAL_REVIEW.value,
                priority=2,
                reasoning=f"Low confidence ({confidence:.0%} < 70%)"
            )
        
        # Step 2: Check if appropriate skill exists
        skill_exists = await self._check_skill_exists(
            analysis_data['detected_file_type'],
            detected_purpose
        )
        
        if skill_exists:
            # Route to existing skill
            target_skill = skill_exists['target_skill']
            workflow = self.WORKFLOW_MAP.get(target_skill, "default_processing.yml")
            priority = self._calculate_priority(detected_purpose)
            ecosystem = self.ECOSYSTEM_MAP.get(detected_purpose, "Archive")
            
            return RoutingDecision(
                attachment_id=attachment_id,
                analysis_id=analysis_id,
                action=RoutingAction.ROUTE_EXISTING.value,
                target_skill=target_skill,
                processing_workflow=workflow,
                priority=priority,
                ecosystem_target=ecosystem,
                reasoning=f"Routing to {target_skill} ({confidence:.0%} confidence)"
            )
        else:
            # Trigger skill creator
            return RoutingDecision(
                attachment_id=attachment_id,
                analysis_id=analysis_id,
                action=RoutingAction.CREATE_SKILL.value,
                processing_workflow="skill_creator.yml",
                priority=3,
                reasoning=f"No skill exists for {detected_purpose}, triggering skill creator"
            )
    
    async def _check_skill_exists(self, file_type: str, purpose: str) -> Optional[Dict]:
        """
        Check if a skill exists for the detected purpose
        
        Returns:
            Skill config or None
        """
        config = self.supabase.table("routing_config")\
            .select("*")\
            .eq("file_type", file_type)\
            .eq("purpose", purpose)\
            .eq("enabled", True)\
            .execute()
        
        if config.data:
            return config.data[0]
        
        return None
    
    def _calculate_priority(self, purpose: str) -> int:
        """
        Calculate priority based on business value
        
        Priority levels:
        5 = Critical (immediate processing)
        4 = High (within hours)
        3 = Medium (within day)
        2 = Low (batch processing)
        1 = Archive (no processing)
        """
        return self.PRIORITY_MAP.get(purpose, 3)
    
    async def save_routing_decision(self, decision: RoutingDecision) -> str:
        """
        Save routing decision to database
        
        Returns:
            Routing decision ID
        """
        data = {
            "attachment_id": decision.attachment_id,
            "analysis_id": decision.analysis_id,
            "action": decision.action,
            "target_skill": decision.target_skill,
            "processing_workflow": decision.processing_workflow,
            "priority": decision.priority,
            "ecosystem_target": decision.ecosystem_target
        }
        
        response = self.supabase.table("routing_decisions").insert(data).execute()
        
        return response.data[0]['id']
    
    async def execute_routing(self, decision: RoutingDecision) -> Dict:
        """
        Execute the routing decision
        
        Actions:
        - route_existing: Trigger workflow for skill
        - create_skill: Trigger skill-creator workflow
        - manual_review: Add to manual review queue
        """
        if decision.action == RoutingAction.ROUTE_EXISTING.value:
            return await self._trigger_workflow(decision)
        
        elif decision.action == RoutingAction.CREATE_SKILL.value:
            return await self._trigger_skill_creator(decision)
        
        elif decision.action == RoutingAction.MANUAL_REVIEW.value:
            return await self._add_to_manual_review(decision)
        
        else:
            raise ValueError(f"Unknown action: {decision.action}")
    
    async def _trigger_workflow(self, decision: RoutingDecision) -> Dict:
        """
        Trigger GitHub Actions workflow for processing
        
        For now, this logs the decision. In production:
        - POST to GitHub Actions API
        - Pass attachment_id and skill parameters
        """
        print(f"🚀 Triggering workflow: {decision.processing_workflow}")
        print(f"   Skill: {decision.target_skill}")
        print(f"   Priority: {decision.priority}")
        
        # Create processing result record (pending)
        result = self.supabase.table("skill_processing_results").insert({
            "routing_decision_id": await self.save_routing_decision(decision),
            "skill_used": decision.target_skill,
            "processing_status": "pending"
        }).execute()
        
        return {
            "status": "triggered",
            "workflow": decision.processing_workflow,
            "result_id": result.data[0]['id']
        }
    
    async def _trigger_skill_creator(self, decision: RoutingDecision) -> Dict:
        """
        Trigger skill-creator to generate new skill
        
        Creates a skill_creator_trigger record
        """
        print(f"🆕 Triggering skill creator")
        
        # Fetch analysis for context
        analysis = self.supabase.table("attachment_analysis")\
            .select("*")\
            .eq("id", decision.analysis_id)\
            .single()\
            .execute()
        
        skill_description = f"""
        Create a processor skill for {analysis.data['detected_file_type']} files 
        with purpose: {analysis.data['detected_purpose']}.
        
        Content preview:
        {analysis.data['extraction_preview']}
        """
        
        # Create trigger record
        trigger = self.supabase.table("skill_creator_triggers").insert({
            "attachment_id": decision.attachment_id,
            "trigger_reason": "new_pattern_detected",
            "skill_description": skill_description
        }).execute()
        
        return {
            "status": "skill_creator_triggered",
            "trigger_id": trigger.data[0]['id']
        }
    
    async def _add_to_manual_review(self, decision: RoutingDecision) -> Dict:
        """
        Add to manual review queue
        
        Low confidence attachments need human review
        """
        print(f"📋 Adding to manual review queue")
        
        # Save decision with manual_review action
        decision_id = await self.save_routing_decision(decision)
        
        return {
            "status": "manual_review_queued",
            "decision_id": decision_id
        }
    
    async def get_priority_queue(self, limit: int = 20) -> List[Dict]:
        """
        Get priority queue of attachments pending processing
        
        Sorted by priority (desc) then routed_at (asc)
        """
        queue = self.supabase.table("priority_queue")\
            .select("*")\
            .limit(limit)\
            .execute()
        
        return queue.data
    
    async def close(self):
        """Cleanup"""
        await self.http_client.aclose()


async def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python skill_router_agent.py <attachment_id>")
        sys.exit(1)
    
    attachment_id = sys.argv[1]
    
    print(f"🎯 Skill Router Agent")
    print(f"📎 Routing: {attachment_id}")
    
    agent = SkillRouterAgent()
    
    try:
        # Route
        decision = await agent.route_attachment(attachment_id)
        
        print(f"\n✅ Routing decision:")
        print(f"   Action: {decision.action}")
        print(f"   Target skill: {decision.target_skill or 'N/A'}")
        print(f"   Workflow: {decision.processing_workflow or 'N/A'}")
        print(f"   Priority: {decision.priority}")
        print(f"   Ecosystem: {decision.ecosystem_target or 'N/A'}")
        print(f"   Reasoning: {decision.reasoning}")
        
        # Save decision
        if SUPABASE_KEY:
            decision_id = await agent.save_routing_decision(decision)
            print(f"\n💾 Saved decision: {decision_id}")
            
            # Execute routing
            result = await agent.execute_routing(decision)
            print(f"🚀 Execution result: {result}")
    
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
