"""
Education Achievement Agent
Michael Shapira D1 Pathway - Specialized Agent

Tracks:
- GPA and academic performance
- NCAA eligibility requirements
- Course planning for D1 qualification
- SAT/ACT scores and improvement
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum


class AcademicTerm(Enum):
    FALL = "fall"
    SPRING = "spring"
    SUMMER = "summer"


class CourseType(Enum):
    CORE = "core"  # NCAA core course
    ELECTIVE = "elective"
    AP = "ap"
    HONORS = "honors"
    DUAL_ENROLLMENT = "dual_enrollment"


@dataclass
class Course:
    """Individual course tracking"""
    name: str
    course_type: CourseType
    credits: float
    grade: str = ""
    grade_points: float = 0.0
    is_ncaa_core: bool = False
    subject_area: str = ""  # English, Math, Science, etc.
    term: AcademicTerm = AcademicTerm.FALL
    year: int = 2024


@dataclass
class TestScore:
    """Standardized test scores"""
    test_type: str  # SAT, ACT
    total_score: int
    section_scores: Dict[str, int] = field(default_factory=dict)
    test_date: date = None
    is_official: bool = True


@dataclass
class NCAACoreRequirements:
    """NCAA D1 core course requirements"""
    english_required: int = 4
    math_required: int = 3  # Algebra 1 or higher
    science_required: int = 2
    social_science_required: int = 2
    additional_english_math_science: int = 1
    additional_core: int = 4
    total_core_courses: int = 16
    minimum_core_gpa: float = 2.3
    
    # D1 Sliding Scale (GPA -> SAT/ACT)
    sliding_scale = {
        2.3: {"SAT": 980, "ACT": 75},
        2.4: {"SAT": 940, "ACT": 72},
        2.5: {"SAT": 900, "ACT": 68},
        2.6: {"SAT": 860, "ACT": 64},
        2.7: {"SAT": 820, "ACT": 61},
        2.8: {"SAT": 780, "ACT": 57},
        2.9: {"SAT": 740, "ACT": 53},
        3.0: {"SAT": 700, "ACT": 49},
        3.1: {"SAT": 660, "ACT": 46},
        3.2: {"SAT": 620, "ACT": 42},
        3.3: {"SAT": 580, "ACT": 39},
        3.4: {"SAT": 540, "ACT": 36},
        3.5: {"SAT": 510, "ACT": 33},
        3.55: {"SAT": 400, "ACT": 37}  # Full qualifier threshold
    }


class EducationAgent:
    """
    Specialized agent for Michael's academic tracking and NCAA eligibility.
    Ensures D1 academic qualification requirements are met.
    """
    
    def __init__(self, student_profile: Dict[str, Any]):
        self.student = student_profile
        self.courses: List[Course] = []
        self.test_scores: List[TestScore] = []
        self.ncaa_reqs = NCAACoreRequirements()
        
    def add_course(self, course: Course) -> None:
        """Add a course to student's record"""
        self.courses.append(course)
        
    def add_test_score(self, score: TestScore) -> None:
        """Add standardized test score"""
        self.test_scores.append(score)
        
    def calculate_gpa(self, weighted: bool = False) -> float:
        """Calculate GPA (weighted or unweighted)"""
        if not self.courses:
            return 0.0
            
        grade_points = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        
        total_points = 0.0
        total_credits = 0.0
        
        for course in self.courses:
            if course.grade:
                points = grade_points.get(course.grade, 0.0)
                
                # Add weight for AP/Honors if weighted GPA
                if weighted:
                    if course.course_type == CourseType.AP:
                        points += 1.0
                    elif course.course_type in [CourseType.HONORS, CourseType.DUAL_ENROLLMENT]:
                        points += 0.5
                
                total_points += points * course.credits
                total_credits += course.credits
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def calculate_ncaa_core_gpa(self) -> float:
        """Calculate GPA using only NCAA core courses"""
        core_courses = [c for c in self.courses if c.is_ncaa_core]
        
        if not core_courses:
            return 0.0
            
        grade_points = {
            "A+": 4.0, "A": 4.0, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        
        total_points = sum(
            grade_points.get(c.grade, 0.0) * c.credits 
            for c in core_courses if c.grade
        )
        total_credits = sum(c.credits for c in core_courses if c.grade)
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0
    
    def get_ncaa_core_progress(self) -> Dict[str, Any]:
        """Track progress toward NCAA core course requirements"""
        core_courses = [c for c in self.courses if c.is_ncaa_core]
        
        progress = {
            "english": {"completed": 0, "required": 4},
            "math": {"completed": 0, "required": 3},
            "science": {"completed": 0, "required": 2},
            "social_science": {"completed": 0, "required": 2},
            "additional": {"completed": 0, "required": 5},  # 1 + 4
            "total": {"completed": len(core_courses), "required": 16}
        }
        
        for course in core_courses:
            area = course.subject_area.lower()
            if "english" in area:
                progress["english"]["completed"] += 1
            elif "math" in area or "algebra" in area or "geometry" in area:
                progress["math"]["completed"] += 1
            elif "science" in area or "biology" in area or "chemistry" in area:
                progress["science"]["completed"] += 1
            elif "history" in area or "social" in area or "government" in area:
                progress["social_science"]["completed"] += 1
            else:
                progress["additional"]["completed"] += 1
        
        return progress
    
    def check_ncaa_eligibility(self) -> Dict[str, Any]:
        """Check if student meets NCAA D1 eligibility requirements"""
        core_gpa = self.calculate_ncaa_core_gpa()
        best_sat = max([s.total_score for s in self.test_scores if s.test_type == "SAT"], default=0)
        best_act = max([s.total_score for s in self.test_scores if s.test_type == "ACT"], default=0)
        
        progress = self.get_ncaa_core_progress()
        
        # Find required SAT/ACT based on GPA
        required_sat = 9999
        required_act = 999
        
        for gpa_threshold in sorted(self.ncaa_reqs.sliding_scale.keys()):
            if core_gpa >= gpa_threshold:
                required_sat = self.ncaa_reqs.sliding_scale[gpa_threshold]["SAT"]
                required_act = self.ncaa_reqs.sliding_scale[gpa_threshold]["ACT"]
        
        eligibility = {
            "core_gpa": core_gpa,
            "core_gpa_met": core_gpa >= self.ncaa_reqs.minimum_core_gpa,
            "best_sat": best_sat,
            "best_act": best_act,
            "required_sat": required_sat,
            "required_act": required_act,
            "sat_met": best_sat >= required_sat if best_sat > 0 else False,
            "act_met": best_act >= required_act if best_act > 0 else False,
            "test_requirement_met": (best_sat >= required_sat) or (best_act >= required_act),
            "core_courses_complete": progress["total"]["completed"] >= 16,
            "is_qualifier": False,
            "status": "In Progress"
        }
        
        # Determine overall status
        if eligibility["core_gpa_met"] and eligibility["test_requirement_met"] and eligibility["core_courses_complete"]:
            eligibility["is_qualifier"] = True
            eligibility["status"] = "Full Qualifier"
        elif not eligibility["core_gpa_met"]:
            eligibility["status"] = "GPA Below Minimum"
        elif not eligibility["test_requirement_met"]:
            eligibility["status"] = f"Need SAT {required_sat} or ACT {required_act}"
        elif not eligibility["core_courses_complete"]:
            remaining = 16 - progress["total"]["completed"]
            eligibility["status"] = f"Need {remaining} more core courses"
        
        return eligibility
    
    def get_recommended_courses(self, current_year: int = 11) -> List[Dict]:
        """Get recommended courses for remaining high school years"""
        progress = self.get_ncaa_core_progress()
        recommendations = []
        
        # Check what's still needed
        if progress["english"]["completed"] < 4:
            needed = 4 - progress["english"]["completed"]
            recommendations.append({
                "subject": "English",
                "courses": ["English 11", "AP English Literature", "English 12"][:needed],
                "priority": "HIGH",
                "reason": f"Need {needed} more English core courses"
            })
        
        if progress["math"]["completed"] < 3:
            needed = 3 - progress["math"]["completed"]
            recommendations.append({
                "subject": "Math",
                "courses": ["Algebra 2", "Pre-Calculus", "AP Calculus"][:needed],
                "priority": "HIGH",
                "reason": f"Need {needed} more Math core courses (Algebra 1+)"
            })
        
        if progress["science"]["completed"] < 2:
            needed = 2 - progress["science"]["completed"]
            recommendations.append({
                "subject": "Science",
                "courses": ["Chemistry", "Physics", "AP Biology"][:needed],
                "priority": "HIGH",
                "reason": f"Need {needed} more Science core courses"
            })
        
        if progress["social_science"]["completed"] < 2:
            needed = 2 - progress["social_science"]["completed"]
            recommendations.append({
                "subject": "Social Science",
                "courses": ["US History", "AP Government", "Economics"][:needed],
                "priority": "MEDIUM",
                "reason": f"Need {needed} more Social Science core courses"
            })
        
        return recommendations
    
    def get_test_prep_recommendations(self) -> Dict:
        """Recommend SAT/ACT prep based on current scores and GPA"""
        core_gpa = self.calculate_ncaa_core_gpa()
        best_sat = max([s.total_score for s in self.test_scores if s.test_type == "SAT"], default=0)
        
        # Find target SAT based on current GPA
        target_sat = 400
        for gpa_threshold in sorted(self.ncaa_reqs.sliding_scale.keys()):
            if core_gpa >= gpa_threshold:
                target_sat = self.ncaa_reqs.sliding_scale[gpa_threshold]["SAT"]
        
        gap = target_sat - best_sat if best_sat > 0 else target_sat
        
        recommendations = {
            "current_sat": best_sat,
            "target_sat": target_sat,
            "gap": gap,
            "priority": "HIGH" if gap > 100 else "MEDIUM" if gap > 0 else "LOW",
            "recommendations": []
        }
        
        if gap > 100:
            recommendations["recommendations"].extend([
                "Consider SAT prep course (Khan Academy is free)",
                "Take at least 2 practice tests per month",
                "Focus on weaker section (Math vs Reading/Writing)",
                "Schedule official SAT for next available date"
            ])
        elif gap > 0:
            recommendations["recommendations"].extend([
                "Practice with official SAT materials",
                "Focus on time management strategies",
                "Consider retake if not at target"
            ])
        else:
            recommendations["recommendations"].append(
                "SAT requirement met! Focus on maintaining GPA"
            )
        
        return recommendations
    
    def generate_academic_report(self) -> Dict:
        """Generate comprehensive academic status report"""
        return {
            "student": self.student,
            "gpa": {
                "unweighted": self.calculate_gpa(weighted=False),
                "weighted": self.calculate_gpa(weighted=True),
                "ncaa_core": self.calculate_ncaa_core_gpa()
            },
            "test_scores": [
                {"type": s.test_type, "score": s.total_score, "date": str(s.test_date)}
                for s in self.test_scores
            ],
            "ncaa_eligibility": self.check_ncaa_eligibility(),
            "core_progress": self.get_ncaa_core_progress(),
            "course_recommendations": self.get_recommended_courses(),
            "test_prep": self.get_test_prep_recommendations(),
            "generated_at": datetime.now().isoformat()
        }


# ============================================================
# MICHAEL SHAPIRA PROFILE
# ============================================================

def load_michael_profile() -> EducationAgent:
    """Load Michael Shapira's academic profile"""
    profile = {
        "name": "Michael Shapira",
        "school": "Satellite Beach High School",
        "graduation_year": 2027,
        "current_grade": 11
    }
    
    agent = EducationAgent(profile)
    
    # Add current test scores
    agent.add_test_score(TestScore(
        test_type="SAT",
        total_score=1280,
        section_scores={"Math": 640, "EBRW": 640},
        test_date=date(2024, 10, 1)
    ))
    
    # Add sample courses (would be populated from transcript)
    sample_courses = [
        Course("English 9", CourseType.CORE, 1.0, "A", is_ncaa_core=True, subject_area="English", year=2023),
        Course("English 10", CourseType.CORE, 1.0, "A-", is_ncaa_core=True, subject_area="English", year=2024),
        Course("Algebra 1", CourseType.CORE, 1.0, "B+", is_ncaa_core=True, subject_area="Math", year=2023),
        Course("Geometry", CourseType.CORE, 1.0, "B", is_ncaa_core=True, subject_area="Math", year=2024),
        Course("Biology", CourseType.CORE, 1.0, "A-", is_ncaa_core=True, subject_area="Science", year=2023),
        Course("Chemistry", CourseType.CORE, 1.0, "B+", is_ncaa_core=True, subject_area="Science", year=2024),
        Course("World History", CourseType.CORE, 1.0, "A", is_ncaa_core=True, subject_area="Social Science", year=2023),
        Course("US History", CourseType.CORE, 1.0, "B+", is_ncaa_core=True, subject_area="Social Science", year=2024),
    ]
    
    for course in sample_courses:
        agent.add_course(course)
    
    return agent


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("📚 Education Achievement Agent - Michael Shapira D1 Pathway")
    print("=" * 60)
    
    agent = load_michael_profile()
    
    # Generate report
    report = agent.generate_academic_report()
    
    print(f"\n👤 Student: {report['student']['name']}")
    print(f"🎓 School: {report['student']['school']}")
    print(f"📅 Graduation: {report['student']['graduation_year']}")
    
    print(f"\n📊 GPA:")
    print(f"   Unweighted: {report['gpa']['unweighted']}")
    print(f"   Weighted: {report['gpa']['weighted']}")
    print(f"   NCAA Core: {report['gpa']['ncaa_core']}")
    
    print(f"\n📝 SAT: {report['test_scores'][0]['score']}")
    
    eligibility = report['ncaa_eligibility']
    print(f"\n🏈 NCAA D1 Eligibility:")
    print(f"   Status: {eligibility['status']}")
    print(f"   Core GPA Met: {'✅' if eligibility['core_gpa_met'] else '❌'}")
    print(f"   Test Requirement: {'✅' if eligibility['test_requirement_met'] else f'❌ Need {eligibility[\"required_sat\"]} SAT'}")
    
    progress = report['core_progress']
    print(f"\n📚 Core Course Progress:")
    for subject, data in progress.items():
        if subject != "total":
            status = "✅" if data["completed"] >= data["required"] else f"Need {data['required'] - data['completed']} more"
            print(f"   {subject.title()}: {data['completed']}/{data['required']} {status}")
    
    print("\n✅ Education Achievement Agent initialized")
