import re
from typing import Dict, List, Any

def extract_experience_requirements(text: str) -> List[Dict[str, Any]]:
    """
    Extracts experience constraints from text like '2+ years'
    """
    results = []
    if not text:
        return results
        
    # Match patterns like "X+ years", "X-Y years"
    matches = re.finditer(r'(\d+)(?:\+|-(\d+))?\s*(?:to\s*\d+)?\s*years?(?:\s+of)?\s+experience', text, re.IGNORECASE)
    
    for match in matches:
        min_years = int(match.group(1))
        max_years = int(match.group(2)) if match.group(2) else None
        
        results.append({
            "minimum_years": min_years,
            "maximum_years": max_years,
            "raw_text": match.group(0)
        })
        
    return results

def extract_education_requirements(text: str) -> List[Dict[str, Any]]:
    """
    Extracts education constraints.
    """
    results = []
    if not text:
        return results
        
    # Simple rule-based extraction
    degrees = {
        r"bachelor'?s|b\.tech|b\.e\.|bs|bsc|ba": "Bachelor's",
        r"master'?s|m\.tech|m\.e\.|ms|msc|ma|mba": "Master's",
        r"phd|ph\.d|doctorate": "PhD"
    }
    
    for pattern, normalized in degrees.items():
        if re.search(r'\b(?:' + pattern + r')\b', text, re.IGNORECASE):
            results.append({
                "degree": normalized,
                "fields": [] # Would extract "Computer Science" etc. with NLP
            })
            
    return results

def extract_soft_skills(text: str) -> List[str]:
    """
    Extracts common soft skills.
    """
    if not text:
        return []
        
    soft_skills_list = [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Time Management", "Adaptability", "Collaboration", "Critical Thinking",
        "Agile", "Scrum", "Mentoring"
    ]
    
    found = []
    for skill in soft_skills_list:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found.append(skill)
            
    return found

def extract_responsibilities(text: str) -> List[str]:
    """
    Extracts bullet points from a responsibilities section.
    """
    if not text:
        return []
        
    lines = text.split('\n')
    responsibilities = []
    
    for line in lines:
        clean = line.strip()
        # Look for bullet points
        if clean.startswith('-') or clean.startswith('•') or clean.startswith('*'):
            responsibilities.append(clean[1:].strip())
            
    return responsibilities
