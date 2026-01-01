"""
WhatsApp Hub - Attachment Analyzer Agent
Uses AI to analyze attachment content and determine appropriate skill routing
"""

import os
import asyncio
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from anthropic import Anthropic
from supabase import create_client, Client
import openpyxl
from pypdf import PdfReader
from PIL import Image
import pytesseract

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

@dataclass
class AnalysisResult:
    """AI analysis result for an attachment"""
    attachment_id: str
    detected_file_type: str  # excel, pdf, image, etc.
    detected_purpose: str    # property_analysis, swim_results, etc.
    confidence: float        # 0.0-1.0
    extraction_preview: str  # First-pass content summary
    recommended_skill: Optional[str] = None  # Target skill path
    reasoning: Optional[str] = None  # AI reasoning for routing

class AttachmentAnalyzerAgent:
    """
    Analyzes attachments using AI to determine content and routing
    
    Intelligence Capabilities:
    - Excel: Column detection, data pattern recognition
    - PDF: Text extraction, document classification
    - Image: OCR, visual content analysis
    - Link: Domain categorization, content preview
    
    Routing Logic:
    - Confidence ≥ 0.7 → Route to existing skill
    - Confidence < 0.7 → Manual review
    - Unknown file type → Trigger skill-creator
    """
    
    # Excel patterns for detection
    EXCEL_PATTERNS = {
        "property_analysis": {
            "keywords": ["address", "arv", "repairs", "judgment", "lien", "foreclosure", "auction"],
            "confidence_weight": 0.9
        },
        "swim_results": {
            "keywords": ["event", "time", "swimmer", "meet", "freestyle", "backstroke", "butterfly", "relay"],
            "confidence_weight": 0.95
        },
        "financial_docs": {
            "keywords": ["revenue", "expense", "profit", "account", "debit", "credit", "balance"],
            "confidence_weight": 0.85
        }
    }
    
    # PDF patterns
    PDF_PATTERNS = {
        "construction_plans": {
            "keywords": ["floor plan", "elevation", "site plan", "blueprint", "construction", "sqft", "dimensions"],
            "confidence_weight": 0.9
        },
        "legal_docs": {
            "keywords": ["agreement", "contract", "deed", "lien", "plaintiff", "defendant", "court"],
            "confidence_weight": 0.85
        }
    }
    
    # Image patterns
    IMAGE_PATTERNS = {
        "property_photos": {
            "keywords": ["house", "home", "property", "listing", "bedroom", "bathroom", "kitchen"],
            "confidence_weight": 0.75
        },
        "swim_meet_photos": {
            "keywords": ["swim", "meet", "results", "time", "relay", "freestyle", "event"],
            "confidence_weight": 0.80
        }
    }
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    async def analyze_attachment(self, attachment_id: str) -> AnalysisResult:
        """
        Analyze a single attachment
        
        Steps:
        1. Fetch attachment metadata
        2. Download file from Supabase storage
        3. Extract content preview
        4. AI classification
        5. Determine confidence and routing
        """
        # Fetch attachment
        attachment = self.supabase.table("whatsapp_attachments")\
            .select("*")\
            .eq("id", attachment_id)\
            .single()\
            .execute()
        
        if not attachment.data:
            raise ValueError(f"Attachment {attachment_id} not found")
        
        att_data = attachment.data
        file_type = att_data['file_type']
        storage_path = att_data.get('storage_path')
        
        # Extract content preview based on file type
        if file_type == 'excel':
            preview, purpose, confidence = await self._analyze_excel(storage_path)
        elif file_type == 'pdf':
            preview, purpose, confidence = await self._analyze_pdf(storage_path)
        elif file_type == 'image':
            preview, purpose, confidence = await self._analyze_image(storage_path)
        else:
            preview, purpose, confidence = f"Unsupported file type: {file_type}", "unknown", 0.0
        
        # Determine recommended skill
        recommended_skill = self._match_to_skill(file_type, purpose, confidence)
        
        # Create result
        result = AnalysisResult(
            attachment_id=attachment_id,
            detected_file_type=file_type,
            detected_purpose=purpose,
            confidence=confidence,
            extraction_preview=preview[:500],  # Limit preview length
            recommended_skill=recommended_skill,
            reasoning=f"Detected {purpose} with {confidence:.0%} confidence"
        )
        
        return result
    
    async def _analyze_excel(self, storage_path: str) -> Tuple[str, str, float]:
        """
        Analyze Excel file
        
        Returns:
            (preview_text, detected_purpose, confidence)
        """
        # Download file
        file_data = await self._download_from_storage(storage_path)
        
        # Save to temp file
        temp_path = Path(f"/tmp/{storage_path.split('/')[-1]}")
        with open(temp_path, 'wb') as f:
            f.write(file_data)
        
        try:
            # Load workbook
            wb = openpyxl.load_workbook(temp_path, data_only=True)
            sheet = wb.active
            
            # Extract headers (first row)
            headers = []
            for cell in sheet[1]:
                if cell.value:
                    headers.append(str(cell.value).lower())
            
            # Extract sample data (first 5 rows)
            sample_data = []
            for row in sheet.iter_rows(min_row=2, max_row=6, values_only=True):
                sample_data.append([str(cell) if cell else "" for cell in row])
            
            # Classify based on headers
            best_match = None
            best_score = 0.0
            
            for purpose, pattern in self.EXCEL_PATTERNS.items():
                score = 0
                matches = 0
                for keyword in pattern['keywords']:
                    if any(keyword in header for header in headers):
                        matches += 1
                
                if matches > 0:
                    score = (matches / len(pattern['keywords'])) * pattern['confidence_weight']
                
                if score > best_score:
                    best_score = score
                    best_match = purpose
            
            # Format preview
            preview = f"Headers: {', '.join(headers[:10])}\n"
            preview += f"Rows: {len(list(sheet.rows))}\n"
            preview += f"Sample data: {sample_data[0] if sample_data else 'None'}"
            
            return preview, best_match or "unknown", best_score
            
        finally:
            temp_path.unlink(missing_ok=True)
    
    async def _analyze_pdf(self, storage_path: str) -> Tuple[str, str, float]:
        """
        Analyze PDF file
        
        Returns:
            (preview_text, detected_purpose, confidence)
        """
        # Download file
        file_data = await self._download_from_storage(storage_path)
        
        # Save to temp file
        temp_path = Path(f"/tmp/{storage_path.split('/')[-1]}")
        with open(temp_path, 'wb') as f:
            f.write(file_data)
        
        try:
            # Extract text
            reader = PdfReader(temp_path)
            
            # Get first few pages
            text = ""
            for page in reader.pages[:3]:
                text += page.extract_text() + "\n"
            
            text_lower = text.lower()
            
            # Classify based on keywords
            best_match = None
            best_score = 0.0
            
            for purpose, pattern in self.PDF_PATTERNS.items():
                matches = sum(1 for keyword in pattern['keywords'] if keyword in text_lower)
                
                if matches > 0:
                    score = (matches / len(pattern['keywords'])) * pattern['confidence_weight']
                
                if score > best_score:
                    best_score = score
                    best_match = purpose
            
            # Use AI for final classification if uncertain
            if best_score < 0.6 and len(text) > 100:
                ai_purpose, ai_confidence = await self._ai_classify_text(text[:2000], "pdf")
                if ai_confidence > best_score:
                    best_match = ai_purpose
                    best_score = ai_confidence
            
            preview = text[:500]
            return preview, best_match or "unknown", best_score
            
        finally:
            temp_path.unlink(missing_ok=True)
    
    async def _analyze_image(self, storage_path: str) -> Tuple[str, str, float]:
        """
        Analyze image file using OCR
        
        Returns:
            (preview_text, detected_purpose, confidence)
        """
        # Download file
        file_data = await self._download_from_storage(storage_path)
        
        # Save to temp file
        temp_path = Path(f"/tmp/{storage_path.split('/')[-1]}")
        with open(temp_path, 'wb') as f:
            f.write(file_data)
        
        try:
            # Open image
            img = Image.open(temp_path)
            
            # Perform OCR
            try:
                text = pytesseract.image_to_string(img)
            except Exception as e:
                print(f"OCR failed: {e}")
                text = ""
            
            if text:
                text_lower = text.lower()
                
                # Classify based on keywords
                best_match = None
                best_score = 0.0
                
                for purpose, pattern in self.IMAGE_PATTERNS.items():
                    matches = sum(1 for keyword in pattern['keywords'] if keyword in text_lower)
                    
                    if matches > 0:
                        score = (matches / len(pattern['keywords'])) * pattern['confidence_weight']
                    
                    if score > best_score:
                        best_score = score
                        best_match = purpose
                
                preview = f"OCR Text: {text[:500]}"
                return preview, best_match or "unknown", best_score
            else:
                # No text detected - fallback to generic image
                return "Image file (no text detected)", "unknown", 0.3
            
        finally:
            temp_path.unlink(missing_ok=True)
    
    async def _ai_classify_text(self, text: str, file_type: str) -> Tuple[str, float]:
        """
        Use Claude to classify content when pattern matching is uncertain
        
        Returns:
            (detected_purpose, confidence)
        """
        prompt = f"""Analyze this {file_type} content and classify its purpose.

Content preview:
{text}

Possible purposes:
- property_analysis (real estate, foreclosures, property data)
- swim_results (swimming times, meet results, athlete data)
- financial_docs (P&L, balance sheets, financial statements)
- construction_plans (floor plans, blueprints, site plans)
- legal_docs (contracts, deeds, legal agreements)
- unknown (if none of the above match)

Respond in JSON format:
{{
    "purpose": "detected_purpose",
    "confidence": 0.85,
    "reasoning": "brief explanation"
}}"""
        
        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return result['purpose'], result['confidence']
            
        except Exception as e:
            print(f"AI classification failed: {e}")
            return "unknown", 0.5
    
    def _match_to_skill(self, file_type: str, purpose: str, confidence: float) -> Optional[str]:
        """
        Match detected purpose to a skill
        
        Returns:
            Skill path or None
        """
        # Fetch routing config from database
        config = self.supabase.table("routing_config")\
            .select("*")\
            .eq("file_type", file_type)\
            .eq("purpose", purpose)\
            .eq("enabled", True)\
            .execute()
        
        if config.data and confidence >= config.data[0].get('confidence_threshold', 0.7):
            return config.data[0]['target_skill']
        
        return None
    
    async def _download_from_storage(self, storage_path: str) -> bytes:
        """Download file from Supabase storage"""
        result = self.supabase.storage.from_("whatsapp-attachments").download(storage_path)
        return result
    
    async def save_analysis(self, result: AnalysisResult) -> str:
        """
        Save analysis result to database
        
        Returns:
            Analysis record ID
        """
        data = {
            "attachment_id": result.attachment_id,
            "detected_file_type": result.detected_file_type,
            "detected_purpose": result.detected_purpose,
            "confidence": result.confidence,
            "extraction_preview": result.extraction_preview
        }
        
        response = self.supabase.table("attachment_analysis").insert(data).execute()
        
        return response.data[0]['id']


async def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python attachment_analyzer_agent.py <attachment_id>")
        sys.exit(1)
    
    attachment_id = sys.argv[1]
    
    print(f"🔍 Attachment Analyzer Agent")
    print(f"📎 Analyzing: {attachment_id}")
    
    agent = AttachmentAnalyzerAgent()
    
    # Analyze
    result = await agent.analyze_attachment(attachment_id)
    
    print(f"\n✅ Analysis complete:")
    print(f"   File type: {result.detected_file_type}")
    print(f"   Purpose: {result.detected_purpose}")
    print(f"   Confidence: {result.confidence:.0%}")
    print(f"   Recommended skill: {result.recommended_skill or 'None (manual review)'}")
    print(f"   Preview: {result.extraction_preview[:100]}...")
    
    # Save
    if SUPABASE_KEY:
        analysis_id = await agent.save_analysis(result)
        print(f"\n💾 Saved analysis: {analysis_id}")


if __name__ == "__main__":
    asyncio.run(main())
