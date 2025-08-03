"""
Basic tests for LangHire components.
Run with: pytest tests/
"""
import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from parsers.resume_parser import ResumeParser
from parsers.jd_parser import JobDescriptionParser
from analyzer.skill_matcher import SkillMatcher
from analyzer.scoring_engine import ScoringEngine

class TestResumeParser:
    """Test resume parsing functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.parser = ResumeParser()
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        dirty_text = "This  is\n\n  a   test\t\ttext with   extra spaces"
        clean_text = self.parser.clean_text(dirty_text)
        
        assert clean_text == "This is a test text with extra spaces"
    
    def test_email_extraction(self):
        """Test email extraction from text."""
        text = "Contact me at john.doe@example.com or call me"
        contact_info = self.parser.extract_contact_info(text)
        
        assert contact_info["email"] == "john.doe@example.com"
    
    def test_resume_validation(self):
        """Test resume content validation."""
        valid_resume = """
        John Doe
        Software Engineer
        Experience: 5 years in Python development
        Education: BS Computer Science
        Skills: Python, JavaScript, React
        Email: john@example.com
        """
        
        validation = self.parser.validate_resume_content(valid_resume)
        assert validation["is_valid"] == True
        assert validation["confidence"] >= 0.5

class TestJobDescriptionParser:
    """Test job description parsing functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.parser = JobDescriptionParser()
    
    def test_url_validation(self):
        """Test URL validation."""
        valid_url = "https://example.com/jobs/software-engineer"
        invalid_url = "not-a-url"
        
        assert self.parser.is_valid_url(valid_url) == True
        assert self.parser.is_valid_url(invalid_url) == False
    
    def test_jd_validation(self):
        """Test job description validation."""
        valid_jd = """
        Software Engineer Position
        We are looking for a skilled developer
        Requirements: Python, 3+ years experience
        Responsibilities: Build web applications
        Qualifications: BS in Computer Science
        """
        
        validation = self.parser.validate_jd_content(valid_jd)
        assert validation["is_valid"] == True
        assert validation["confidence"] >= 0.6

class TestSkillMatcher:
    """Test skill matching functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.matcher = SkillMatcher()
    
    def test_skill_normalization(self):
        """Test skill name normalization."""
        test_cases = [
            ("Expert Python Developer", "python developer"),
            ("React.js (5+ years)", "react.js"),
            ("Advanced JavaScript Skills", "javascript"),
        ]
        
        for input_skill, expected in test_cases:
            result = self.matcher.normalize_skill(input_skill)
            assert expected in result.lower()
    
    def test_skill_extraction(self):
        """Test skill extraction from text."""
        text = "I have experience with Python, React, and PostgreSQL databases"
        skills = self.matcher.extract_skills_from_text(text)
        
        assert "python" in skills.get("programming_languages", [])
        assert "react" in skills.get("web_technologies", [])
        assert "postgresql" in skills.get("databases", [])
    
    def test_skill_matching_score(self):
        """Test skill matching score calculation."""
        candidate_skills = {
            "programming_languages": ["python", "java"],
            "databases": ["postgresql"]
        }
        
        required_skills = {
            "programming_languages": ["python", "javascript"],
            "databases": ["postgresql", "mongodb"]
        }
        
        score = self.matcher.calculate_skill_match_score(candidate_skills, required_skills)
        
        assert score["overall_score"] > 0
        assert "python" in score["exact_matches"]["programming_languages"]
        assert "postgresql" in score["exact_matches"]["databases"]
        assert "javascript" in score["missing_skills"]["programming_languages"]

class TestScoringEngine:
    """Test scoring engine functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.engine = ScoringEngine()
    
    def test_skills_scoring(self):
        """Test skills scoring calculation."""
        skill_analysis = {
            "exact_matches": {
                "programming_languages": ["python", "java"],
                "databases": ["postgresql"]
            },
            "missing_skills": {
                "programming_languages": ["javascript"],
                "web_technologies": ["react"]
            },
            "overall_score": 75
        }
        
        score = self.engine.calculate_skills_score(skill_analysis)
        
        assert "total_score" in score
        assert isinstance(score["total_score"], (int, float))
        assert 0 <= score["total_score"] <= 100
    
    def test_recommendation_generation(self):
        """Test recommendation generation."""
        test_scores = [
            (95, "Strong Hire"),
            (75, "Hire"),
            (60, "Maybe"),
            (30, "Don't Hire")
        ]
        
        for score, expected_decision in test_scores:
            recommendation = self.engine._generate_recommendation(score)
            assert recommendation["decision"] == expected_decision
            assert "reasoning" in recommendation

# Integration Tests
class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    def test_resume_to_skills_pipeline(self):
        """Test complete resume to skills extraction pipeline."""
        resume_parser = ResumeParser()
        skill_matcher = SkillMatcher()
        
        sample_resume = """
        John Doe
        Senior Software Engineer
        
        Experience:
        - 5 years of Python development
        - Built web applications using Django and React
        - Worked with PostgreSQL and Redis databases
        - Experience with AWS cloud services
        
        Skills: Python, JavaScript, React, Django, PostgreSQL, AWS, Git
        """
        
        # Parse resume
        resume_data = {
            "raw_text": sample_resume,
            "status": "success"
        }
        
        # Extract skills
        skills = skill_matcher.extract_skills_from_text(resume_data["raw_text"])
        
        # Verify skill extraction
        assert len(skills) > 0
        assert "programming_languages" in skills
        assert "python" in skills["programming_languages"]
    
    def test_complete_analysis_flow(self):
        """Test the complete analysis flow without API calls."""
        # This test simulates the analysis flow without requiring API keys
        resume_text = "Software Engineer with 5 years Python experience"
        jd_text = "Looking for Python developer with web development skills"
        
        # Initialize components
        skill_matcher = SkillMatcher()
        scoring_engine = ScoringEngine()
        
        # Extract skills
        candidate_skills = skill_matcher.extract_skills_from_text(resume_text)
        jd_skills = skill_matcher.extract_skills_from_text(jd_text)
        
        # Calculate skill match
        skill_match = skill_matcher.calculate_skill_match_score(candidate_skills, jd_skills)
        
        # Calculate scores
        skills_score = scoring_engine.calculate_skills_score(skill_match)
        
        # Verify results
        assert isinstance(skills_score, dict)
        assert "total_score" in skills_score
        assert skills_score["total_score"] >= 0

if __name__ == "__main__":
    pytest.main([__file__])