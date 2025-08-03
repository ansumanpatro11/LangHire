"""
LangChain chains for LangHire application.
"""
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import BaseOutputParser
from typing import Dict, Any, List
import json
import re

from config import Config
from .prompts import (
    RESUME_EXTRACTION_PROMPT,
    JD_ANALYSIS_PROMPT,
    SKILL_MATCHING_PROMPT,
    EXPERIENCE_MATCHING_PROMPT,
    OVERALL_SCORING_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT
)

class StructuredOutputParser(BaseOutputParser):
    """Custom output parser for structured responses."""
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse LLM output into structured format."""
        try:
            # Try to extract JSON if present
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback to section-based parsing
            sections = {}
            current_section = None
            current_content = []
            
            for line in text.split('\n'):
                line = line.strip()
                if line.endswith(':') and len(line.split()) <= 3:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line[:-1].lower().replace(' ', '_')
                    current_content = []
                elif line and current_section:
                    current_content.append(line)
            
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            return sections
        except Exception as e:
            return {"raw_text": text, "error": str(e)}

class LangHireChains:
    """Main chains class for LangHire application."""
    
    def __init__(self):
        """Initialize chains with Gemini model."""
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            temperature=Config.MODEL_TEMPERATURE,
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.output_parser = StructuredOutputParser()
        self._setup_chains()
    
    def _setup_chains(self):
        """Setup all LangChain chains."""
        
        # Resume extraction chain
        self.resume_chain = LLMChain(
            llm=self.llm,
            prompt=RESUME_EXTRACTION_PROMPT,
            output_key="resume_analysis",
            verbose=True
        )
        
        # Job description analysis chain
        self.jd_chain = LLMChain(
            llm=self.llm,
            prompt=JD_ANALYSIS_PROMPT,
            output_key="jd_analysis",
            verbose=True
        )
        
        # Skill matching chain
        self.skill_matching_chain = LLMChain(
            llm=self.llm,
            prompt=SKILL_MATCHING_PROMPT,
            output_key="skill_analysis",
            verbose=True
        )
        
        # Experience matching chain
        self.experience_chain = LLMChain(
            llm=self.llm,
            prompt=EXPERIENCE_MATCHING_PROMPT,
            output_key="experience_analysis",
            verbose=True
        )
        
        # Overall scoring chain
        self.scoring_chain = LLMChain(
            llm=self.llm,
            prompt=OVERALL_SCORING_PROMPT,
            output_key="overall_score",
            verbose=True
        )
        
        # Interview questions chain
        self.interview_chain = LLMChain(
            llm=self.llm,
            prompt=INTERVIEW_QUESTIONS_PROMPT,
            output_key="interview_questions",
            verbose=True
        )
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume and extract structured information."""
        try:
            result = self.resume_chain.run(resume_text=resume_text)
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"Resume analysis failed: {str(e)}"}
    
    def analyze_job_description(self, jd_text: str) -> Dict[str, Any]:
        """Analyze job description and extract requirements."""
        try:
            result = self.jd_chain.run(jd_text=jd_text)
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"JD analysis failed: {str(e)}"}
    
    def match_skills(self, candidate_skills: str, job_requirements: str) -> Dict[str, Any]:
        """Match candidate skills with job requirements."""
        try:
            result = self.skill_matching_chain.run(
                candidate_skills=candidate_skills,
                job_requirements=job_requirements
            )
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"Skill matching failed: {str(e)}"}
    
    def analyze_experience(self, candidate_experience: str, job_experience_requirements: str) -> Dict[str, Any]:
        """Analyze candidate experience against job requirements."""
        try:
            result = self.experience_chain.run(
                candidate_experience=candidate_experience,
                job_experience_requirements=job_experience_requirements
            )
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"Experience analysis failed: {str(e)}"}
    
    def generate_overall_score(self, skill_analysis: str, experience_analysis: str, 
                             candidate_profile: str, job_requirements: str) -> Dict[str, Any]:
        """Generate overall candidate score and recommendation."""
        try:
            result = self.scoring_chain.run(
                skill_analysis=skill_analysis,
                experience_analysis=experience_analysis,
                candidate_profile=candidate_profile,
                job_requirements=job_requirements
            )
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"Scoring failed: {str(e)}"}
    
    def generate_interview_questions(self, strengths: str, gaps: str, job_requirements: str) -> Dict[str, Any]:
        """Generate targeted interview questions."""
        try:
            result = self.interview_chain.run(
                strengths=strengths,
                gaps=gaps,
                job_requirements=job_requirements
            )
            return self.output_parser.parse(result)
        except Exception as e:
            return {"error": f"Interview questions generation failed: {str(e)}"}
    
    def run_complete_analysis(self, resume_text: str, jd_text: str) -> Dict[str, Any]:
        """Run complete candidate analysis pipeline."""
        try:
            # Step 1: Analyze resume and JD
            resume_analysis = self.analyze_resume(resume_text)
            jd_analysis = self.analyze_job_description(jd_text)
            
            if "error" in resume_analysis or "error" in jd_analysis:
                return {
                    "error": "Failed to analyze resume or job description",
                    "resume_error": resume_analysis.get("error"),
                    "jd_error": jd_analysis.get("error")
                }
            
            # Step 2: Extract relevant information for matching
            candidate_skills = str(resume_analysis.get("skills", ""))
            candidate_experience = str(resume_analysis.get("work_experience", ""))
            job_requirements = str(jd_analysis.get("required_technical_skills", ""))
            job_experience_req = str(jd_analysis.get("experience_requirements", ""))
            
            # Step 3: Perform skill and experience matching
            skill_match = self.match_skills(candidate_skills, job_requirements)
            experience_match = self.analyze_experience(candidate_experience, job_experience_req)
            
            # Step 4: Generate overall score
            overall_score = self.generate_overall_score(
                str(skill_match), 
                str(experience_match),
                str(resume_analysis),
                str(jd_analysis)
            )
            
            # Step 5: Generate interview questions
            strengths = overall_score.get("strengths", "")
            gaps = overall_score.get("areas_of_concern", "")
            interview_questions = self.generate_interview_questions(
                str(strengths), 
                str(gaps), 
                str(jd_analysis)
            )
            
            return {
                "resume_analysis": resume_analysis,
                "jd_analysis": jd_analysis,
                "skill_match": skill_match,
                "experience_match": experience_match,
                "overall_score": overall_score,
                "interview_questions": interview_questions,
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Complete analysis failed: {str(e)}"}