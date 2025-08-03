"""
Prompt templates for LangHire application using LangChain.
"""
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate

# Resume parsing prompt
RESUME_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert resume parser. Extract structured information from the resume text.
    Focus on skills, experience, education, and achievements. Return the information in a clear, structured format."""),
    ("human", """Parse the following resume and extract:
    1. Personal Information (name, contact)
    2. Skills (technical and soft skills)
    3. Work Experience (company, role, duration, responsibilities)
    4. Education (degree, institution, year)
    5. Achievements and Certifications

    Resume Text:
    {resume_text}

    Return the extracted information in a structured format.""")
])

# Job Description analysis prompt
JD_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert HR analyst. Analyze job descriptions to identify key requirements.
    Extract required skills, experience levels, responsibilities, and qualifications."""),
    ("human", """Analyze the following job description and extract:
    1. Required Technical Skills
    2. Required Soft Skills
    3. Experience Requirements (years, specific experience)
    4. Educational Requirements
    5. Key Responsibilities
    6. Nice-to-have Skills
    7. Company Culture Indicators

    Job Description:
    {jd_text}

    Return the analysis in a structured format.""")
])

# Skill matching prompt
SKILL_MATCHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert skills matcher. Compare candidate skills with job requirements.
    Identify exact matches, partial matches, and missing skills. Consider skill synonyms and related technologies."""),
    ("human", """Compare the candidate's skills with job requirements:

    Candidate Skills:
    {candidate_skills}

    Job Requirements:
    {job_requirements}

    Provide:
    1. Exact Skill Matches (skills that directly match)
    2. Partial Matches (related or similar skills)
    3. Missing Critical Skills
    4. Missing Nice-to-have Skills
    5. Skill Gap Score (0-100)
    6. Recommendations for skill development

    Format the response clearly with scores and explanations.""")
])

# Experience matching prompt
EXPERIENCE_MATCHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert experience evaluator. Compare candidate experience with job requirements.
    Consider industry relevance, role similarity, and achievement quality."""),
    ("human", """Evaluate the candidate's experience against job requirements:

    Candidate Experience:
    {candidate_experience}

    Job Experience Requirements:
    {job_experience_requirements}

    Provide:
    1. Relevant Experience Score (0-100)
    2. Industry Match Assessment
    3. Role Responsibility Alignment
    4. Experience Gap Analysis
    5. Notable Achievements Relevance
    6. Years of Experience Match

    Include detailed reasoning for scores.""")
])

# Overall scoring prompt
OVERALL_SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert hiring manager. Provide a comprehensive candidate evaluation.
    Consider skills, experience, cultural fit, and growth potential."""),
    ("human", """Provide an overall candidate evaluation:

    Skill Analysis:
    {skill_analysis}

    Experience Analysis:
    {experience_analysis}

    Candidate Profile:
    {candidate_profile}

    Job Requirements:
    {job_requirements}

    Provide:
    1. Overall Fit Score (0-100)
    2. Strengths (top 3-5)
    3. Areas of Concern (top 3-5)
    4. Cultural Fit Assessment
    5. Growth Potential
    6. Risk Assessment
    7. Final Recommendation (Hire/Don't Hire/Maybe)
    8. Reasoning for recommendation

    Be objective and provide actionable insights.""")
])

# Interview questions prompt
INTERVIEW_QUESTIONS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert interviewer. Generate targeted interview questions based on candidate gaps and strengths.
    Focus on validating skills, assessing problem-solving, and exploring experience depth."""),
    ("human", """Generate interview questions based on:

    Candidate Strengths:
    {strengths}

    Identified Gaps:
    {gaps}

    Job Requirements:
    {job_requirements}

    Generate:
    1. Technical Questions (5-7 questions to assess technical skills)
    2. Behavioral Questions (3-5 questions for experience validation)
    3. Scenario-based Questions (2-3 questions for problem-solving)
    4. Gap-focused Questions (3-4 questions to address identified gaps)
    5. Growth Questions (2-3 questions about learning and development)

    Make questions specific, actionable, and relevant to the role.""")
])

# Few-shot examples for better consistency
SKILL_MATCHING_EXAMPLES = [
    {
        "candidate_skills": "Python, Django, REST APIs, PostgreSQL",
        "job_requirements": "Python, Flask, APIs, MySQL, Docker",
        "analysis": """
        Exact Matches: Python, APIs (REST APIs match API requirement)
        Partial Matches: Django (web framework like Flask), PostgreSQL (database like MySQL)
        Missing Critical: Flask, Docker
        Missing Nice-to-have: MySQL
        Skill Gap Score: 75/100
        """
    }
]

# Create few-shot prompt for skill matching
SKILL_MATCHING_FEW_SHOT = FewShotPromptTemplate(
    examples=SKILL_MATCHING_EXAMPLES,
    example_prompt=PromptTemplate(
        input_variables=["candidate_skills", "job_requirements", "analysis"],
        template="Candidate: {candidate_skills}\nJob: {job_requirements}\nAnalysis: {analysis}"
    ),
    prefix="You are analyzing skill matches. Here's an example:",
    suffix="Now analyze:\nCandidate: {candidate_skills}\nJob: {job_requirements}\nAnalysis:",
    input_variables=["candidate_skills", "job_requirements"]
)