"""
Skill matching and analysis utilities.
"""
from typing import Dict, List, Set, Any, Tuple
import re
from collections import defaultdict

class SkillMatcher:
    """Advanced skill matching and analysis."""
    
    def __init__(self):
        """Initialize skill matcher with predefined skill categories and synonyms."""
        self.skill_categories = self._load_skill_categories()
        self.skill_synonyms = self._load_skill_synonyms()
        self.programming_languages = self._load_programming_languages()
        self.frameworks = self._load_frameworks()
        self.databases = self._load_databases()
        self.tools = self._load_tools()
    
    def _load_skill_categories(self) -> Dict[str, List[str]]:
        """Load predefined skill categories."""
        return {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "go", 
                "rust", "swift", "kotlin", "scala", "ruby", "php", "r", "matlab"
            ],
            "web_technologies": [
                "html", "css", "react", "angular", "vue", "node.js", "express",
                "django", "flask", "spring", "asp.net", "laravel", "rails"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
                "oracle", "sql server", "sqlite", "cassandra", "dynamodb"
            ],
            "cloud_platforms": [
                "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
                "terraform", "ansible", "jenkins", "gitlab", "github actions"
            ],
            "data_science": [
                "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
                "spark", "hadoop", "tableau", "power bi", "jupyter"
            ],
            "soft_skills": [
                "leadership", "communication", "problem solving", "teamwork",
                "project management", "analytical thinking", "creativity"
            ]
        }
    
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Load skill synonyms and variations."""
        return {
            "javascript": ["js", "node", "nodejs", "node.js"],
            "typescript": ["ts"],
            "python": ["py"],
            "postgresql": ["postgres", "psql"],
            "mongodb": ["mongo"],
            "kubernetes": ["k8s"],
            "amazon web services": ["aws"],
            "google cloud platform": ["gcp", "google cloud"],
            "microsoft azure": ["azure"],
            "machine learning": ["ml", "artificial intelligence", "ai"],
            "deep learning": ["dl", "neural networks"],
            "natural language processing": ["nlp"],
            "computer vision": ["cv"],
            "user interface": ["ui"],
            "user experience": ["ux"],
            "application programming interface": ["api", "rest api", "restful"],
            "structured query language": ["sql"],
            "nosql": ["no-sql", "document database"],
            "continuous integration": ["ci", "ci/cd"],
            "continuous deployment": ["cd"],
            "test driven development": ["tdd"],
            "behavior driven development": ["bdd"],
            "object oriented programming": ["oop"],
            "functional programming": ["fp"]
        }
    
    def _load_programming_languages(self) -> Set[str]:
        """Load programming languages list."""
        return {
            "python", "java", "javascript", "typescript", "c++", "c#", "c",
            "go", "rust", "swift", "kotlin", "scala", "ruby", "php", "r",
            "matlab", "perl", "shell", "bash", "powershell", "dart", "lua"
        }
    
    def _load_frameworks(self) -> Set[str]:
        """Load frameworks and libraries."""
        return {
            "react", "angular", "vue", "svelte", "jquery", "bootstrap",
            "django", "flask", "fastapi", "spring", "express", "koa",
            "rails", "laravel", "symfony", "asp.net", "xamarin", "flutter",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas"
        }
    
    def _load_databases(self) -> Set[str]:
        """Load database technologies."""
        return {
            "mysql", "postgresql", "sqlite", "oracle", "sql server",
            "mongodb", "cassandra", "redis", "elasticsearch", "dynamodb",
            "couchdb", "neo4j", "influxdb", "mariadb"
        }
    
    def _load_tools(self) -> Set[str]:
        """Load development tools and platforms."""
        return {
            "git", "github", "gitlab", "bitbucket", "docker", "kubernetes",
            "jenkins", "travis", "circleci", "terraform", "ansible",
            "vagrant", "jira", "confluence", "slack", "vscode", "intellij"
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name for better matching."""
        skill = skill.lower().strip()
        
        # Remove common prefixes/suffixes
        skill = re.sub(r'(^(expert|advanced|proficient|experienced)\s+)', '', skill)
        skill = re.sub(r'(\s+(experience|skills?)$)', '', skill)
        
        # Handle parentheses and versions
        skill = re.sub(r'\s*\([^)]*\)', '', skill)
        skill = re.sub(r'\s+\d+(\.\d+)?(\+)?$', '', skill)  # Remove version numbers
        
        return skill.strip()
    
    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from text and categorize them."""
        text_lower = text.lower()
        found_skills = defaultdict(list)
        
        # Check each category
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if self._skill_mentioned(skill, text_lower):
                    found_skills[category].append(skill)
        
        # Check for synonyms
        for main_skill, synonyms in self.skill_synonyms.items():
            for synonym in synonyms:
                if self._skill_mentioned(synonym, text_lower):
                    # Find the category for the main skill
                    for category, skills in self.skill_categories.items():
                        if main_skill in skills:
                            if main_skill not in found_skills[category]:
                                found_skills[category].append(main_skill)
                            break
        
        return dict(found_skills)
    
    def _skill_mentioned(self, skill: str, text: str) -> bool:
        """Check if a skill is mentioned in text."""
        # Create word boundary pattern
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        return bool(re.search(pattern, text))
    
    def calculate_skill_match_score(self, candidate_skills: Dict[str, List[str]], 
                                  required_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate detailed skill matching score."""
        match_result = {
            "exact_matches": defaultdict(list),
            "partial_matches": defaultdict(list),
            "missing_skills": defaultdict(list),
            "category_scores": {},
            "overall_score": 0.0,
            "total_required": 0,
            "total_matched": 0
        }
        
        total_required_count = 0
        total_matched_count = 0
        category_scores = {}
        
        # Analyze each category
        for category in set(list(candidate_skills.keys()) + list(required_skills.keys())):
            candidate_cat_skills = set(candidate_skills.get(category, []))
            required_cat_skills = set(required_skills.get(category, []))
            
            if not required_cat_skills:
                continue
            
            # Exact matches
            exact_matches = candidate_cat_skills.intersection(required_cat_skills)
            match_result["exact_matches"][category] = list(exact_matches)
            
            # Missing skills
            missing_skills = required_cat_skills - candidate_cat_skills
            match_result["missing_skills"][category] = list(missing_skills)
            
            # Calculate category score
            if required_cat_skills:
                category_score = len(exact_matches) / len(required_cat_skills) * 100
                category_scores[category] = category_score
                
                total_required_count += len(required_cat_skills)
                total_matched_count += len(exact_matches)
        
        match_result["category_scores"] = category_scores
        match_result["total_required"] = total_required_count
        match_result["total_matched"] = total_matched_count
        
        # Calculate overall score
        if total_required_count > 0:
            match_result["overall_score"] = (total_matched_count / total_required_count) * 100
        
        return match_result
    
    def get_skill_recommendations(self, missing_skills: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Generate skill development recommendations."""
        recommendations = {}
        
        for category, skills in missing_skills.items():
            if not skills:
                continue
                
            category_recommendations = []
            
            if category == "programming_languages":
                category_recommendations.extend([
                    "Consider online coding bootcamps or courses",
                    "Practice with coding challenges on platforms like LeetCode or HackerRank",
                    "Build personal projects to demonstrate proficiency"
                ])
            
            elif category == "web_technologies":
                category_recommendations.extend([
                    "Complete framework-specific tutorials and documentation",
                    "Build full-stack web applications",
                    "Contribute to open-source projects"
                ])
            
            elif category == "cloud_platforms":
                category_recommendations.extend([
                    "Obtain cloud certifications (AWS, Azure, GCP)",
                    "Practice with free tier cloud services",
                    "Deploy personal projects to cloud platforms"
                ])
            
            elif category == "data_science":
                category_recommendations.extend([
                    "Complete data science courses or bootcamps",
                    "Work on Kaggle competitions",
                    "Build and showcase data analysis projects"
                ])
            
            else:
                category_recommendations.append(f"Develop {category} skills through relevant courses and practice")
            
            recommendations[category] = category_recommendations
        
        return recommendations
    
    def analyze_skill_depth(self, text: str, skills: List[str]) -> Dict[str, str]:
        """Analyze the depth of experience for mentioned skills."""
        skill_depth = {}
        
        experience_indicators = {
            "expert": ["expert", "lead", "senior", "architect", "advanced", "10+ years", "extensive"],
            "proficient": ["proficient", "experienced", "solid", "strong", "5+ years", "commercial"],
            "intermediate": ["intermediate", "working knowledge", "familiar", "some experience", "2+ years"],
            "beginner": ["basic", "beginner", "learning", "exposure", "introduction", "started"]
        }
        
        text_lower = text.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            depth = "mentioned"  # default
            
            # Look for experience indicators near the skill mention
            for level, indicators in experience_indicators.items():
                for indicator in indicators:
                    # Check if indicator appears within 50 characters of skill mention
                    skill_pos = text_lower.find(skill_lower)
                    if skill_pos != -1:
                        surrounding_text = text_lower[max(0, skill_pos-50):skill_pos+50]
                        if indicator in surrounding_text:
                            depth = level
                            break
                if depth != "mentioned":
                    break
            
            skill_depth[skill] = depth
        
        return skill_depth