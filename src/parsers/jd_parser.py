"""
Job Description parser for extracting content from text and URLs.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import re
from urllib.parse import urlparse

class JobDescriptionParser:
    """Parser for job descriptions from various sources."""
    
    def __init__(self):
        """Initialize the JD parser."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 30
    
    def parse_url(self, url: str) -> str:
        """Extract job description from URL."""
        try:
            if not self.is_valid_url(url):
                raise Exception("Invalid URL format")
            
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find job description specific content
            job_content = self.extract_job_content(soup)
            
            if not job_content:
                # Fallback to general text extraction
                job_content = soup.get_text()
            
            return self.clean_text(job_content)
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing URL content: {str(e)}")
    
    def extract_job_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job-specific content from HTML."""
        # Common selectors for job descriptions
        job_selectors = [
            '[class*="job-description"]',
            '[class*="job-details"]',
            '[class*="description"]',
            '[id*="job-description"]',
            '[id*="description"]',
            '.job-content',
            '.posting-description',
            '.job-posting-description',
            'main',
            'article'
        ]
        
        for selector in job_selectors:
            elements = soup.select(selector)
            if elements:
                return ' '.join([elem.get_text() for elem in elements])
        
        return None
    
    def parse_text(self, text: str) -> str:
        """Parse job description from plain text."""
        return self.clean_text(text)
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove common website navigation text
        navigation_patterns = [
            r'home\s+about\s+contact\s+careers',
            r'privacy\s+policy\s+terms\s+of\s+service',
            r'cookie\s+policy',
            r'all\s+rights\s+reserved',
            r'copyright\s+\d{4}',
            r'menu\s+toggle',
            r'skip\s+to\s+content'
        ]
        
        for pattern in navigation_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_company_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract basic company information from JD text."""
        company_info = {
            "company_name": None,
            "location": None,
            "industry": None
        }
        
        # Try to extract company name (basic patterns)
        company_patterns = [
            r'(?:at|join)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\s+,|\s+\.|$)',
            r'([A-Z][a-zA-Z\s&]+?)\s+is\s+(?:a|an|the)',
            r'Company:\s*([A-Z][a-zA-Z\s&]+?)(?:\n|\s+|$)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                company_info["company_name"] = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r'Location:\s*([A-Za-z\s,]+?)(?:\n|$)',
            r'Based in\s+([A-Za-z\s,]+?)(?:\s|,|\.|$)',
            r'([A-Za-z]+,\s*[A-Z]{2})',  # City, State format
            r'Remote|Work from home|Hybrid'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_info["location"] = match.group(1).strip() if match.group(1) else match.group(0)
                break
        
        return company_info
    
    def parse_job_description(self, input_data: str, input_type: str = "text") -> Dict[str, Any]:
        """Parse job description and return structured data."""
        try:
            if input_type.lower() == "url":
                text = self.parse_url(input_data)
                source = input_data
            else:
                text = self.parse_text(input_data)
                source = "text_input"
            
            # Extract basic information
            company_info = self.extract_company_info(text)
            
            return {
                "raw_text": text,
                "company_info": company_info,
                "word_count": len(text.split()),
                "character_count": len(text),
                "source": source,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def validate_jd_content(self, text: str) -> Dict[str, Any]:
        """Validate if the text looks like a job description."""
        validation_result = {
            "is_valid": False,
            "confidence": 0.0,
            "issues": []
        }
        
        if not text or len(text.strip()) < 50:
            validation_result["issues"].append("Text too short to be a job description")
            return validation_result
        
        # Check for JD indicators
        jd_indicators = [
            r'\b(responsibilities|duties|requirements)\b',
            r'\b(qualifications|skills|experience)\b',
            r'\b(position|role|job title)\b',
            r'\b(company|organization|team)\b',
            r'\b(apply|application|candidate)\b'
        ]
        
        matches = 0
        for pattern in jd_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        confidence = matches / len(jd_indicators)
        validation_result["confidence"] = confidence
        validation_result["is_valid"] = confidence >= 0.6
        
        if confidence < 0.6:
            validation_result["issues"].append("Content doesn't appear to be a job description")
        
        return validation_result