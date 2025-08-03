"""
Resume parser for extracting text from various resume formats.
"""
import PyPDF2
import requests
from typing import Optional, Dict, Any
import re
from io import BytesIO

class ResumeParser:
    """Parser for resume documents."""
    
    def __init__(self):
        """Initialize the resume parser."""
        self.supported_formats = ['.pdf', '.txt']
    
    def parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return self.clean_text(text)
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def parse_text(self, text_content: str) -> str:
        """Parse plain text resume."""
        return self.clean_text(text_content)
    
    def parse_linkedin_url(self, linkedin_url: str) -> str:
        """
        Parse LinkedIn profile URL (basic implementation).
        Note: This requires LinkedIn API access for full functionality.
        """
        try:
            # Basic URL validation
            if not self.is_valid_linkedin_url(linkedin_url):
                raise Exception("Invalid LinkedIn URL format")
            
            # For demo purposes, return a placeholder
            # In production, you would use LinkedIn API or web scraping
            return f"LinkedIn profile data from: {linkedin_url}\n[This would contain actual profile data in production]"
            
        except Exception as e:
            raise Exception(f"Error parsing LinkedIn URL: {str(e)}")
    
    def is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format."""
        linkedin_pattern = r"https?://(?:www\.)?linkedin\.com/in/[\w-]+"
        return bool(re.match(linkedin_pattern, url))
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\n\-\.\,\;\:\(\)\@]', ' ', text)
        
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract basic contact information from resume text."""
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group()
        
        # Extract phone number
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info["phone"] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact_info["linkedin"] = f"https://{linkedin_match.group()}"
        
        return contact_info
    
    def parse_resume_file(self, file_obj, file_type: str) -> Dict[str, Any]:
        """Parse resume file and return structured data."""
        try:
            if file_type.lower() == 'pdf':
                file_content = file_obj.read()
                text = self.parse_pdf(file_content)
            elif file_type.lower() in ['txt', 'text']:
                text = file_obj.read().decode('utf-8')
                text = self.parse_text(text)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
            
            # Extract basic information
            contact_info = self.extract_contact_info(text)
            
            return {
                "raw_text": text,
                "contact_info": contact_info,
                "word_count": len(text.split()),
                "character_count": len(text),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def validate_resume_content(self, text: str) -> Dict[str, Any]:
        """Validate if the text looks like a resume."""
        validation_result = {
            "is_valid": False,
            "confidence": 0.0,
            "issues": []
        }
        
        if not text or len(text.strip()) < 100:
            validation_result["issues"].append("Text too short to be a resume")
            return validation_result
        
        # Check for resume indicators
        resume_indicators = [
            r'\b(experience|work history|employment)\b',
            r'\b(education|degree|university|college)\b',
            r'\b(skills|expertise|proficient)\b',
            r'\b(contact|email|phone)\b'
        ]
        
        matches = 0
        for pattern in resume_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        confidence = matches / len(resume_indicators)
        validation_result["confidence"] = confidence
        validation_result["is_valid"] = confidence >= 0.5
        
        if confidence < 0.5:
            validation_result["issues"].append("Content doesn't appear to be a resume")
        
        return validation_result