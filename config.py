"""
Configuration settings for LangHire application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    MODEL_NAME = "gemini-1.5-flash"
    MODEL_TEMPERATURE = 0.3
    MAX_TOKENS = 4000
    
    # Application Settings
    APP_TITLE = "LangHire - JD-Aware Resume Analyzer"
    APP_ICON = "🎯"
    
    # Scoring Thresholds
    HIRE_THRESHOLD = 70  # Minimum score for hire recommendation
    STRONG_HIRE_THRESHOLD = 85  # Threshold for strong hire
    
    # File Upload Settings
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = ['.pdf', '.txt']
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            return False
        return True
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration dictionary."""
        return {
            "model": cls.MODEL_NAME,
            "temperature": cls.MODEL_TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS
        }