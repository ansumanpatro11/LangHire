"""
LangHire - JD-Aware Resume Analyzer
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import json
import time

# Import our modules
from config import Config
from src.parsers.resume_parser import ResumeParser
from src.parsers.jd_parser import JobDescriptionParser
from src.langchain_utils.chains import LangHireChains
from src.analyzer.skill_matcher import SkillMatcher
from src.analyzer.scoring_engine import ScoringEngine

# Configure Streamlit page
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

class LangHireApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.resume_parser = ResumeParser()
        self.jd_parser = JobDescriptionParser()
        self.skill_matcher = SkillMatcher()
        self.scoring_engine = ScoringEngine()
        
        # Initialize LangChain chains (with error handling)
        try:
            if Config.validate_config():
                self.chains = LangHireChains()
            else:
                self.chains = None
                st.error("⚠️ Google API key not configured. Please set GOOGLE_API_KEY environment variable.")
        except Exception as e:
            self.chains = None
            st.error(f"⚠️ Error initializing LangChain: {str(e)}")
    
    def render_header(self):
        """Render application header."""
        st.title(f"{Config.APP_ICON} {Config.APP_TITLE}")
        st.markdown("""
        **Analyze resumes against job descriptions using AI-powered insights**
        
        Upload a resume and job description to get:
        - 📊 Skills gap analysis
        - 🎯 Candidate fit scoring  
        - 💡 Interview question suggestions
        - ✅ Hire/Don't Hire recommendations
        """)
        st.divider()
    
    def render_sidebar(self):
        """Render sidebar with configuration options."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # API Status
            if self.chains:
                st.success("✅ API Connected")
            else:
                st.error("❌ API Not Connected")
            
            st.divider()
            
            # Scoring Configuration
            st.subheader("Scoring Thresholds")
            hire_threshold = st.slider(
                "Hire Threshold", 
                min_value=50, 
                max_value=90, 
                value=Config.HIRE_THRESHOLD,
                help="Minimum score for hire recommendation"
            )
            
            strong_hire_threshold = st.slider(
                "Strong Hire Threshold", 
                min_value=70, 
                max_value=100, 
                value=Config.STRONG_HIRE_THRESHOLD,
                help="Minimum score for strong hire recommendation"
            )
            
            # Update config if changed
            Config.HIRE_THRESHOLD = hire_threshold
            Config.STRONG_HIRE_THRESHOLD = strong_hire_threshold
            
            st.divider()
            
            # Analysis Options
            st.subheader("Analysis Options")
            detailed_analysis = st.checkbox("Detailed Analysis", value=True)
            include_interview_questions = st.checkbox("Generate Interview Questions", value=True)
            
            return {
                "detailed_analysis": detailed_analysis,
                "include_interview_questions": include_interview_questions
            }
    
    def render_input_section(self):
        """Render resume and job description input section."""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Resume Input")
            
            resume_input_type = st.selectbox(
                "Input Type",
                ["Upload PDF", "Upload Text", "Paste Text", "LinkedIn URL"],
                key="resume_type"
            )
            
            resume_data = None
            
            if resume_input_type == "Upload PDF":
                uploaded_file = st.file_uploader(
                    "Upload Resume PDF",
                    type=['pdf'],
                    help="Upload a PDF resume file"
                )
                if uploaded_file:
                    resume_data = self.resume_parser.parse_resume_file(uploaded_file, 'pdf')
            
            elif resume_input_type == "Upload Text":
                uploaded_file = st.file_uploader(
                    "Upload Resume Text",
                    type=['txt'],
                    help="Upload a text resume file"
                )
                if uploaded_file:
                    resume_data = self.resume_parser.parse_resume_file(uploaded_file, 'txt')
            
            elif resume_input_type == "Paste Text":
                resume_text = st.text_area(
                    "Paste Resume Text",
                    height=300,
                    placeholder="Paste the resume content here..."
                )
                if resume_text:
                    resume_data = {
                        "raw_text": resume_text,
                        "contact_info": self.resume_parser.extract_contact_info(resume_text),
                        "status": "success"
                    }
            
            elif resume_input_type == "LinkedIn URL":
                linkedin_url = st.text_input(
                    "LinkedIn Profile URL",
                    placeholder="https://linkedin.com/in/username"
                )
                if linkedin_url:
                    try:
                        text = self.resume_parser.parse_linkedin_url(linkedin_url)
                        resume_data = {
                            "raw_text": text,
                            "contact_info": {},
                            "status": "success"
                        }
                    except Exception as e:
                        st.error(f"Error parsing LinkedIn URL: {str(e)}")
        
        with col2:
            st.subheader("💼 Job Description Input")
            
            jd_input_type = st.selectbox(
                "Input Type",
                ["Paste Text", "URL"],
                key="jd_type"
            )
            
            jd_data = None
            
            if jd_input_type == "Paste Text":
                jd_text = st.text_area(
                    "Paste Job Description",
                    height=300,
                    placeholder="Paste the job description here..."
                )
                if jd_text:
                    jd_data = self.jd_parser.parse_job_description(jd_text, "text")
            
            elif jd_input_type == "URL":
                jd_url = st.text_input(
                    "Job Description URL",
                    placeholder="https://company.com/jobs/position"
                )
                if jd_url:
                    with st.spinner("Fetching job description from URL..."):
                        jd_data = self.jd_parser.parse_job_description(jd_url, "url")
        
        return resume_data, jd_data
    
    def render_analysis_section(self, resume_data: Dict, jd_data: Dict, options: Dict):
        """Render analysis section."""
        if not resume_data or not jd_data:
            st.info("👆 Please provide both resume and job description to start analysis.")
            return None
        
        if resume_data.get("status") != "success" or jd_data.get("status") != "success":
            st.error("❌ Error processing input data. Please check your inputs.")
            return None
        
        # Validate content
        resume_validation = self.resume_parser.validate_resume_content(resume_data["raw_text"])
        jd_validation = self.jd_parser.validate_jd_content(jd_data["raw_text"])
        
        if not resume_validation["is_valid"] or not jd_validation["is_valid"]:
            st.warning("⚠️ Input validation warnings detected:")
            if not resume_validation["is_valid"]:
                st.write("Resume issues:", resume_validation["issues"])
            if not jd_validation["is_valid"]:
                st.write("Job description issues:", jd_validation["issues"])
        
        # Analysis button
        if st.button("🚀 Analyze Candidate", type="primary", use_container_width=True):
            if not self.chains:
                st.error("❌ Cannot perform analysis without API connection.")
                return None
            
            return self.run_analysis(resume_data, jd_data, options)
        
        return None
    
    def run_analysis(self, resume_data: Dict, jd_data: Dict, options: Dict) -> Dict:
        """Run the complete analysis pipeline."""
        with st.spinner("🔍 Analyzing candidate... This may take a moment."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: LangChain Analysis
                status_text.text("🤖 Running AI analysis...")
                progress_bar.progress(20)
                
                results = self.chains.run_complete_analysis(
                    resume_data["raw_text"],
                    jd_data["raw_text"]
                )
                
                if "error" in results:
                    st.error(f"Analysis failed: {results['error']}")
                    return None
                
                progress_bar.progress(50)
                
                # Step 2: Skill Matching
                status_text.text("🎯 Matching skills...")
                
                candidate_skills = self.skill_matcher.extract_skills_from_text(resume_data["raw_text"])
                jd_skills = self.skill_matcher.extract_skills_from_text(jd_data["raw_text"])
                skill_match_score = self.skill_matcher.calculate_skill_match_score(candidate_skills, jd_skills)
                
                progress_bar.progress(70)
                
                # Step 3: Comprehensive Scoring
                status_text.text("📊 Calculating scores...")
                
                skills_score = self.scoring_engine.calculate_skills_score(skill_match_score)
                experience_score = self.scoring_engine.calculate_experience_score(
                    results.get("experience_match", {}), 
                    results.get("resume_analysis", {})
                )
                education_score = self.scoring_engine.calculate_education_score(
                    results.get("resume_analysis", {}),
                    results.get("jd_analysis", {})
                )
                
                overall_result = self.scoring_engine.calculate_overall_score(
                    skills_score, experience_score, education_score, results.get("resume_analysis", {})
                )
                
                progress_bar.progress(90)
                
                # Compile final results
                final_results = {
                    "langchain_analysis": results,
                    "skill_matching": {
                        "candidate_skills": candidate_skills,
                        "jd_skills": jd_skills,
                        "match_score": skill_match_score
                    },
                    "scoring": {
                        "skills": skills_score,
                        "experience": experience_score,
                        "education": education_score,
                        "overall": overall_result
                    },
                    "metadata": {
                        "resume_info": resume_data.get("contact_info", {}),
                        "jd_info": jd_data.get("company_info", {}),
                        "analysis_timestamp": time.time()
                    }
                }
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Store in session state
                st.session_state.analysis_results = final_results
                st.session_state.analysis_complete = True
                
                # Clear progress indicators
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                return final_results
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return None
    
    def render_results(self, results: Dict):
        """Render analysis results."""
        if not results:
            return
        
        st.header("📊 Analysis Results")
        
        # Overall Score and Recommendation
        overall_score = results["scoring"]["overall"]["overall_score"]
        recommendation = results["scoring"]["overall"]["recommendation"]
        
        col1, col2, col3 = st.columns([2, 2, 3])
        
        with col1:
            # Score gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = overall_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 70], 'color': "yellow"},
                        {'range': [70, 85], 'color': "lightgreen"},
                        {'range': [85, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': Config.HIRE_THRESHOLD
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.metric("Decision", recommendation["decision"])
            st.metric("Confidence", recommendation["confidence"])
            st.write(f"**Reasoning:** {recommendation['reasoning']}")
        
        with col3:
            # Component scores
            component_scores = results["scoring"]["overall"]["component_scores"]
            
            fig_bar = px.bar(
                x=list(component_scores.keys()),
                y=list(component_scores.values()),
                title="Component Scores",
                labels={'x': 'Component', 'y': 'Score'},
                color=list(component_scores.values()),
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.divider()
        
        # Detailed Analysis Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Skills Analysis", "💼 Experience", "🎓 Education", "❓ Interview Questions"])
        
        with tab1:
            self.render_skills_analysis(results)
        
        with tab2:
            self.render_experience_analysis(results)
        
        with tab3:
            self.render_education_analysis(results)
        
        with tab4:
            self.render_interview_questions(results)
    
    def render_skills_analysis(self, results: Dict):
        """Render detailed skills analysis."""
        skill_data = results["skill_matching"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Skill Matches")
            exact_matches = skill_data["match_score"]["exact_matches"]
            
            for category, skills in exact_matches.items():
                if skills:
                    st.write(f"**{category.replace('_', ' ').title()}:**")
                    for skill in skills:
                        st.write(f"  • {skill}")
        
        with col2:
            st.subheader("❌ Missing Skills")
            missing_skills = skill_data["match_score"]["missing_skills"]
            
            for category, skills in missing_skills.items():
                if skills:
                    st.write(f"**{category.replace('_', ' ').title()}:**")
                    for skill in skills:
                        st.write(f"  • {skill}")
        
        # Skills match visualization
        if skill_data["match_score"]["category_scores"]:
            st.subheader("📊 Category-wise Match Scores")
            
            categories = list(skill_data["match_score"]["category_scores"].keys())
            scores = list(skill_data["match_score"]["category_scores"].values())
            
            fig = px.bar(
                x=categories,
                y=scores,
                title="Skill Match by Category",
                labels={'x': 'Skill Category', 'y': 'Match Score (%)'},
                color=scores,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    def render_experience_analysis(self, results: Dict):
        """Render experience analysis."""
        exp_data = results["scoring"]["experience"]
        
        st.subheader("💼 Experience Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Years of Experience Score", f"{exp_data['years_of_experience']:.1f}/100")
            st.metric("Role Relevance Score", f"{exp_data['role_relevance']:.1f}/100")
        
        with col2:
            st.metric("Industry Match Score", f"{exp_data['industry_match']:.1f}/100")
            st.metric("Career Progression Score", f"{exp_data['career_progression']:.1f}/100")
        
        # Experience component visualization
        exp_components = {
            "Years": exp_data["years_of_experience"],
            "Relevance": exp_data["role_relevance"],
            "Industry": exp_data["industry_match"],
            "Progression": exp_data["career_progression"]
        }
        
        # Create radar chart using graph_objects
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=list(exp_components.values()),
            theta=list(exp_components.keys()),
            fill='toself',
            name='Experience Scores',
            line_color='blue'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Experience Analysis Radar",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_education_analysis(self, results: Dict):
        """Render education analysis."""
        edu_data = results["scoring"]["education"]
        
        st.subheader("🎓 Education Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Degree Match", f"{edu_data['degree_match']:.1f}/100")
        
        with col2:
            st.metric("Field Relevance", f"{edu_data['field_relevance']:.1f}/100")
        
        with col3:
            st.metric("Certifications", f"{edu_data['certifications']:.1f}/100")
        
        # Education breakdown chart
        edu_scores = {
            "Degree Match": edu_data["degree_match"],
            "Field Relevance": edu_data["field_relevance"],
            "Certifications": edu_data["certifications"]
        }
        
        fig = px.pie(
            values=list(edu_scores.values()),
            names=list(edu_scores.keys()),
            title="Education Score Breakdown"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_interview_questions(self, results: Dict):
        """Render suggested interview questions."""
        st.subheader("❓ Suggested Interview Questions")
        
        try:
            questions_data = results["langchain_analysis"]["interview_questions"]
            
            if isinstance(questions_data, dict):
                for category, questions in questions_data.items():
                    if questions and category != "error":
                        st.write(f"**{category.replace('_', ' ').title()}:**")
                        
                        if isinstance(questions, str):
                            # Parse string into list
                            question_list = questions.split('\n')
                            for q in question_list:
                                q = q.strip()
                                if q and not q.startswith('#'):
                                    st.write(f"• {q}")
                        elif isinstance(questions, list):
                            for q in questions:
                                st.write(f"• {q}")
                        
                        st.write("")
            else:
                st.write(str(questions_data))
                
        except Exception as e:
            st.error(f"Error displaying interview questions: {str(e)}")
            
            # Fallback: Generate basic questions
            st.subheader("Basic Interview Questions")
            basic_questions = [
                "Tell me about your experience with the technologies mentioned in your resume.",
                "How would you approach a challenging technical problem?",
                "Describe a time when you had to learn a new technology quickly.",
                "What interests you most about this role?",
                "How do you stay updated with industry trends?"
            ]
            
            for q in basic_questions:
                st.write(f"• {q}")
    
    def run(self):
        """Run the main application."""
        self.render_header()
        
        # Sidebar configuration
        options = self.render_sidebar()
        
        # Main content
        resume_data, jd_data = self.render_input_section()
        
        # Analysis section
        if not st.session_state.analysis_complete:
            analysis_results = self.render_analysis_section(resume_data, jd_data, options)
            if analysis_results:
                self.render_results(analysis_results)
        else:
            # Show existing results
            st.success("✅ Analysis completed successfully!")
            if st.button("🔄 Run New Analysis"):
                st.session_state.analysis_complete = False
                st.session_state.analysis_results = None
                st.rerun()
            
            if st.session_state.analysis_results:
                self.render_results(st.session_state.analysis_results)

# Run the application
if __name__ == "__main__":
    app = LangHireApp()
    app.run()