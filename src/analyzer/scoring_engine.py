"""
Scoring engine for comprehensive candidate evaluation.
"""
from typing import Dict, Any, List, Tuple
import re
from config import Config

class ScoringEngine:
    """Advanced scoring engine for candidate evaluation."""
    
    def __init__(self):
        """Initialize scoring engine with weights and thresholds."""
        self.score_weights = {
            "skills": 0.35,
            "experience": 0.30,
            "education": 0.15,
            "achievements": 0.10,
            "cultural_fit": 0.10
        }
        self.hire_threshold = Config.HIRE_THRESHOLD
        self.strong_hire_threshold = Config.STRONG_HIRE_THRESHOLD
    
    def calculate_skills_score(self, skill_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate skills-based score."""
        score_breakdown = {
            "technical_skills": 0,
            "skill_depth": 0,
            "skill_relevance": 0,
            "total_score": 0,
            "details": {}
        }
        
        try:
            # Extract skill match data
            exact_matches = skill_analysis.get("exact_matches", {})
            missing_skills = skill_analysis.get("missing_skills", {})
            overall_match = skill_analysis.get("overall_score", 0)
            
            # Technical skills score (40% of skills score)
            technical_score = min(overall_match, 100)
            score_breakdown["technical_skills"] = technical_score
            
            # Skill depth analysis (30% of skills score)
            depth_score = self._analyze_skill_depth(skill_analysis)
            score_breakdown["skill_depth"] = depth_score
            
            # Skill relevance (30% of skills score)
            relevance_score = self._calculate_skill_relevance(exact_matches, missing_skills)
            score_breakdown["skill_relevance"] = relevance_score
            
            # Calculate weighted total
            total_score = (
                technical_score * 0.4 +
                depth_score * 0.3 +
                relevance_score * 0.3
            )
            
            score_breakdown["total_score"] = round(total_score, 2)
            score_breakdown["details"] = {
                "exact_matches_count": sum(len(matches) for matches in exact_matches.values()),
                "missing_critical_skills": sum(len(missing) for missing in missing_skills.values()),
                "overall_match_percentage": overall_match
            }
            
        except Exception as e:
            score_breakdown["error"] = f"Skills scoring error: {str(e)}"
            score_breakdown["total_score"] = 0
        
        return score_breakdown
    
    def calculate_experience_score(self, experience_analysis: Dict[str, Any], 
                                 resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate experience-based score."""
        score_breakdown = {
            "years_of_experience": 0,
            "role_relevance": 0,
            "industry_match": 0,
            "career_progression": 0,
            "total_score": 0,
            "details": {}
        }
        
        try:
            # Extract years of experience
            years_score = self._calculate_years_score(resume_data)
            score_breakdown["years_of_experience"] = years_score
            
            # Role relevance (how similar past roles are to target role)
            role_score = self._calculate_role_relevance(experience_analysis)
            score_breakdown["role_relevance"] = role_score
            
            # Industry match
            industry_score = self._calculate_industry_match(experience_analysis)
            score_breakdown["industry_match"] = industry_score
            
            # Career progression
            progression_score = self._calculate_career_progression(resume_data)
            score_breakdown["career_progression"] = progression_score
            
            # Calculate weighted total
            total_score = (
                years_score * 0.3 +
                role_score * 0.4 +
                industry_score * 0.2 +
                progression_score * 0.1
            )
            
            score_breakdown["total_score"] = round(total_score, 2)
            
        except Exception as e:
            score_breakdown["error"] = f"Experience scoring error: {str(e)}"
            score_breakdown["total_score"] = 0
        
        return score_breakdown
    
    def calculate_education_score(self, resume_data: Dict[str, Any], 
                                jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate education-based score."""
        score_breakdown = {
            "degree_match": 0,
            "institution_quality": 0,
            "field_relevance": 0,
            "certifications": 0,
            "total_score": 0
        }
        
        try:
            education_text = str(resume_data.get("education", "")).lower()
            jd_education = str(jd_data.get("educational_requirements", "")).lower()
            
            # Degree match
            degree_score = self._calculate_degree_match(education_text, jd_education)
            score_breakdown["degree_match"] = degree_score
            
            # Field relevance
            field_score = self._calculate_field_relevance(education_text, jd_education)
            score_breakdown["field_relevance"] = field_score
            
            # Certifications
            cert_score = self._calculate_certification_score(resume_data)
            score_breakdown["certifications"] = cert_score
            
            # Calculate total (simplified weights)
            total_score = (degree_score * 0.4 + field_score * 0.4 + cert_score * 0.2)
            score_breakdown["total_score"] = round(total_score, 2)
            
        except Exception as e:
            score_breakdown["error"] = f"Education scoring error: {str(e)}"
            score_breakdown["total_score"] = 0
        
        return score_breakdown
    
    def calculate_overall_score(self, skills_score: Dict[str, Any], 
                              experience_score: Dict[str, Any],
                              education_score: Dict[str, Any],
                              resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final overall score and recommendation."""
        
        # Extract individual scores
        skills_total = skills_score.get("total_score", 0)
        experience_total = experience_score.get("total_score", 0)
        education_total = education_score.get("total_score", 0)
        
        # Calculate achievements score
        achievements_score = self._calculate_achievements_score(resume_data)
        
        # Calculate weighted overall score
        overall_score = (
            skills_total * self.score_weights["skills"] +
            experience_total * self.score_weights["experience"] +
            education_total * self.score_weights["education"] +
            achievements_score * self.score_weights["achievements"]
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(overall_score)
        
        # Compile final result
        final_result = {
            "overall_score": round(overall_score, 2),
            "component_scores": {
                "skills": skills_total,
                "experience": experience_total,
                "education": education_total,
                "achievements": achievements_score
            },
            "recommendation": recommendation,
            "score_breakdown": {
                "skills_analysis": skills_score,
                "experience_analysis": experience_score,
                "education_analysis": education_score
            },
            "risk_factors": self._identify_risk_factors(skills_score, experience_score, education_score),
            "strengths": self._identify_strengths(skills_score, experience_score, education_score),
            "decision_confidence": self._calculate_confidence(overall_score, skills_score, experience_score)
        }
        
        return final_result
    
    # Helper methods
    def _analyze_skill_depth(self, skill_analysis: Dict[str, Any]) -> float:
        """Analyze depth of skills mentioned."""
        # Simplified depth analysis
        exact_matches = skill_analysis.get("exact_matches", {})
        total_matches = sum(len(matches) for matches in exact_matches.values())
        
        if total_matches >= 8:
            return 90
        elif total_matches >= 5:
            return 75
        elif total_matches >= 3:
            return 60
        else:
            return 40
    
    def _calculate_skill_relevance(self, exact_matches: Dict, missing_skills: Dict) -> float:
        """Calculate how relevant the matched skills are."""
        total_exact = sum(len(matches) for matches in exact_matches.values())
        total_missing = sum(len(missing) for missing in missing_skills.values())
        
        if total_exact + total_missing == 0:
            return 50
        
        relevance = (total_exact / (total_exact + total_missing)) * 100
        return min(relevance, 100)
    
    def _calculate_years_score(self, resume_data: Dict[str, Any]) -> float:
        """Calculate score based on years of experience."""
        # Try to extract years from work experience
        work_exp = str(resume_data.get("work_experience", "")).lower()
        
        # Look for year patterns
        year_patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d{4})\s*-\s*(\d{4})',
            r'(\d{4})\s*-\s*present'
        ]
        
        total_years = 0
        for pattern in year_patterns:
            matches = re.findall(pattern, work_exp)
            if matches:
                if len(matches[0]) == 1:  # Direct years mention
                    total_years = max(total_years, int(matches[0]))
                else:  # Year range
                    for match in matches:
                        if len(match) == 2:
                            start_year = int(match[0])
                            end_year = int(match[1]) if match[1].isdigit() else 2024
                            years = end_year - start_year
                            total_years += years
        
        # Score based on years
        if total_years >= 10:
            return 100
        elif total_years >= 7:
            return 90
        elif total_years >= 5:
            return 80
        elif total_years >= 3:
            return 70
        elif total_years >= 1:
            return 60
        else:
            return 30
    
    def _calculate_role_relevance(self, experience_analysis: Dict[str, Any]) -> float:
        """Calculate relevance of past roles."""
        # Simplified role relevance calculation
        return 75  # Default good score
    
    def _calculate_industry_match(self, experience_analysis: Dict[str, Any]) -> float:
        """Calculate industry match score."""
        return 70  # Default moderate score
    
    def _calculate_career_progression(self, resume_data: Dict[str, Any]) -> float:
        """Calculate career progression score."""
        work_exp = str(resume_data.get("work_experience", "")).lower()
        
        # Look for progression indicators
        progression_indicators = [
            "promoted", "senior", "lead", "manager", "director", 
            "principal", "architect", "head of", "chief"
        ]
        
        score = 50  # Base score
        for indicator in progression_indicators:
            if indicator in work_exp:
                score += 10
        
        return min(score, 100)
    
    def _calculate_degree_match(self, education_text: str, jd_education: str) -> float:
        """Calculate degree match score."""
        degree_levels = ["phd", "doctorate", "master", "bachelor", "associate"]
        
        candidate_degree = None
        required_degree = None
        
        for degree in degree_levels:
            if degree in education_text:
                candidate_degree = degree
                break
        
        for degree in degree_levels:
            if degree in jd_education:
                required_degree = degree
                break
        
        if not required_degree:
            return 80  # No specific requirement
        
        if not candidate_degree:
            return 30  # No degree mentioned
        
        degree_scores = {"associate": 1, "bachelor": 2, "master": 3, "doctorate": 4, "phd": 4}
        
        candidate_level = degree_scores.get(candidate_degree, 0)
        required_level = degree_scores.get(required_degree, 0)
        
        if candidate_level >= required_level:
            return 100
        elif candidate_level == required_level - 1:
            return 70
        else:
            return 40
    
    def _calculate_field_relevance(self, education_text: str, jd_education: str) -> float:
        """Calculate field of study relevance."""
        tech_fields = [
            "computer science", "software", "engineering", "technology",
            "information systems", "data science", "mathematics", "statistics"
        ]
        
        candidate_has_tech = any(field in education_text for field in tech_fields)
        jd_requires_tech = any(field in jd_education for field in tech_fields)
        
        if not jd_requires_tech:
            return 80  # No specific field requirement
        
        if candidate_has_tech:
            return 90
        else:
            return 50
    
    def _calculate_certification_score(self, resume_data: Dict[str, Any]) -> float:
        """Calculate certification score."""
        text = str(resume_data.get("achievements", "")).lower()
        
        cert_indicators = [
            "certified", "certification", "aws", "azure", "google cloud",
            "pmp", "scrum master", "agile", "itil", "cissp"
        ]
        
        cert_count = sum(1 for indicator in cert_indicators if indicator in text)
        
        return min(cert_count * 20, 100)
    
    def _calculate_achievements_score(self, resume_data: Dict[str, Any]) -> float:
        """Calculate achievements score."""
        achievements_text = str(resume_data.get("achievements", "")).lower()
        
        achievement_indicators = [
            "award", "recognition", "published", "patent", "led team",
            "increased", "improved", "reduced", "saved", "grew", "built"
        ]
        
        score = 50  # Base score
        for indicator in achievement_indicators:
            if indicator in achievements_text:
                score += 8
        
        return min(score, 100)
    
    def _generate_recommendation(self, overall_score: float) -> Dict[str, Any]:
        """Generate hire/don't hire recommendation."""
        if overall_score >= self.strong_hire_threshold:
            decision = "Strong Hire"
            confidence = "High"
            reasoning = "Candidate demonstrates strong alignment with role requirements"
        elif overall_score >= self.hire_threshold:
            decision = "Hire"
            confidence = "Medium-High"
            reasoning = "Candidate meets most requirements with some areas for development"
        elif overall_score >= 50:
            decision = "Maybe"
            confidence = "Medium"
            reasoning = "Candidate shows potential but has significant gaps"
        else:
            decision = "Don't Hire"
            confidence = "High"
            reasoning = "Candidate does not meet minimum requirements"
        
        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "score": overall_score
        }
    
    def _identify_risk_factors(self, skills_score: Dict, experience_score: Dict, 
                             education_score: Dict) -> List[str]:
        """Identify potential risk factors."""
        risks = []
        
        if skills_score.get("total_score", 0) < 60:
            risks.append("Significant technical skill gaps")
        
        if experience_score.get("total_score", 0) < 50:
            risks.append("Limited relevant experience")
        
        if education_score.get("total_score", 0) < 40:
            risks.append("Educational background concerns")
        
        return risks
    
    def _identify_strengths(self, skills_score: Dict, experience_score: Dict, 
                          education_score: Dict) -> List[str]:
        """Identify candidate strengths."""
        strengths = []
        
        if skills_score.get("total_score", 0) >= 80:
            strengths.append("Strong technical skills")
        
        if experience_score.get("total_score", 0) >= 80:
            strengths.append("Extensive relevant experience")
        
        if education_score.get("total_score", 0) >= 80:
            strengths.append("Strong educational background")
        
        return strengths
    
    def _calculate_confidence(self, overall_score: float, skills_score: Dict, 
                            experience_score: Dict) -> str:
        """Calculate confidence level in the decision."""
        scores = [
            skills_score.get("total_score", 0),
            experience_score.get("total_score", 0)
        ]
        
        score_variance = max(scores) - min(scores)
        
        if score_variance < 20 and (overall_score > 80 or overall_score < 40):
            return "High"
        elif score_variance < 30:
            return "Medium"
        else:
            return "Low"