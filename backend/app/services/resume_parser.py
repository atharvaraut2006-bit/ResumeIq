import re
import spacy
from typing import Dict, Any, List

# Load a small spacy model if available, otherwise fallback to basic processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If not installed, we rely purely on regex (or you can prompt user to run `python -m spacy download en_core_web_sm`)
    nlp = None

def parse_resume(text: str) -> Dict[str, Any]:
    """
    Parses raw resume text into structured data.
    """
    sections = extract_sections(text)
    
    # Extract specific entities from sections
    contact_info = extract_contact_info(text, sections.get("summary", "") + "\n" + sections.get("contact", ""))
    
    return {
        "contact": contact_info,
        "summary": sections.get("summary", ""),
        "education": extract_education(sections.get("education", "")),
        "experience": extract_experience(sections.get("experience", "")),
        "skills_raw": sections.get("skills", ""),
        "projects": extract_projects(sections.get("projects", "")),
        "certifications": extract_certifications(sections.get("certifications", "")),
        "achievements": extract_achievements(sections.get("achievements", "")),
        "other_sections": [{"section_name": k, "content": v} for k, v in sections.items() 
                           if k not in ["contact", "summary", "education", "experience", "skills", "projects", "certifications", "achievements"]]
    }

def extract_sections(text: str) -> Dict[str, str]:
    """
    Splits text into logical sections based on common headings.
    """
    sections = {}
    current_section = "contact" # Assume first part is contact/header
    current_content = []
    
    # Common section headings and their normalized names
    headings_map = {
        r"SUMMARY|PROFESSIONAL SUMMARY|OBJECTIVE|CAREER OBJECTIVE": "summary",
        r"EDUCATION|ACADEMIC BACKGROUND|ACADEMICS": "education",
        r"EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY|WORK HISTORY|INTERNSHIP|INTERNSHIPS": "experience",
        r"SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES": "skills",
        r"PROJECTS|ACADEMIC PROJECTS|PERSONAL PROJECTS": "projects",
        r"CERTIFICATIONS|CERTIFICATES": "certifications",
        r"ACHIEVEMENTS|AWARDS|HONORS": "achievements",
        r"PUBLICATIONS": "publications",
        r"POSITIONS OF RESPONSIBILITY|LEADERSHIP": "positions_of_responsibility",
        r"EXTRACURRICULAR ACTIVITIES|EXTRA-CURRICULAR": "extracurricular_activities"
    }
    
    lines = text.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        is_heading = False
        
        # Check if line is a heading (usually all caps or matches known heading)
        if len(line_clean) < 40: # Headings are usually short
            line_upper = line_clean.upper()
            
            for pattern, normalized_name in headings_map.items():
                if re.fullmatch(r"^(" + pattern + r")$", line_upper) or \
                   re.fullmatch(r"^(" + pattern + r")\s*[:-]?$", line_upper):
                    
                    if current_content:
                        sections[current_section] = "\n".join(current_content).strip()
                    
                    current_section = normalized_name
                    current_content = []
                    is_heading = True
                    break
        
        if not is_heading:
            current_content.append(line_clean)
            
    # Save the last section
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
        
    return sections

def extract_contact_info(full_text: str, top_text: str) -> Dict[str, Any]:
    # Look for email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text)
    email = email_match.group(0) if email_match else None
    
    # Look for phone (supports Indian numbers and basic international formats)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', full_text)
    phone = phone_match.group(0) if phone_match else None
    
    # Look for LinkedIn
    linkedin_match = re.search(r'(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+', full_text)
    linkedin = linkedin_match.group(0) if linkedin_match else None
    
    # Look for GitHub
    github_match = re.search(r'(https?:\/\/)?(www\.)?github\.com\/[a-zA-Z0-9_-]+', full_text)
    github = github_match.group(0) if github_match else None
    
    # Attempt to extract Name (heuristic: first non-empty line that isn't contact info)
    name = None
    lines = top_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # If it contains an email or phone, skip
        if '@' in line or re.search(r'\d{10}', re.sub(r'[-.\s]', '', line)):
            continue
        # If it's a known keyword, skip
        if line.upper() in ['RESUME', 'CV', 'CURRICULUM VITAE']:
            continue
        # Seems like a good candidate for a name
        name = line
        break
        
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "portfolio": None # Needs more complex regex to distinguish from other links
    }

def extract_education(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    
    lines = text.split('\n')
    entries = []
    
    current_entry = {"degree": None, "institution": None, "year": None, "raw": ""}
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        current_entry["raw"] += line_str + "\n"
        
        # Check degree pattern
        if not current_entry["degree"]:
            deg_match = re.search(r'\b(b\.tech|b\.e|b\.s|b\.a|bachelor|m\.tech|m\.s|m\.a|master|phd|doctorate|diploma|higher secondary|senior secondary|10th|12th)\b', line_str, re.I)
            if deg_match:
                current_entry["degree"] = line_str
                
        # Check institution pattern
        if not current_entry["institution"]:
            inst_match = re.search(r'\b(university|institute|college|school|academy|campus|vit|iit|nit|bits)\b', line_str, re.I)
            if inst_match:
                current_entry["institution"] = line_str
                
        # Check year pattern
        year_match = re.search(r'\b(19|20)\d{2}\b', line_str)
        if year_match:
            current_entry["year"] = year_match.group(0)
            entries.append(current_entry)
            current_entry = {"degree": None, "institution": None, "year": None, "raw": ""}
            
    if current_entry["raw"].strip():
        if not current_entry["degree"]:
            current_entry["degree"] = current_entry["raw"].strip()
        entries.append(current_entry)
        
    return entries

def extract_experience(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
        
    # Just chunk the text for now
    return [{"raw": text.strip()}]

def extract_projects(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    return [{"raw": text.strip()}]

def extract_certifications(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    return [{"raw": text.strip()}]

def extract_achievements(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    return [{"raw": text.strip()}]
