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
    current_section = "contact"
    current_content = []
    
    headings_map = {
        r"SUMMARY|PROFESSIONAL SUMMARY|PROFILE|PROFILE SUMMARY|ABOUT ME|ABOUT|CAREER OBJECTIVE|OBJECTIVE|PROFESSIONAL RESUME|PROFESSIONAL OVERVIEW|CAREER OVERVIEW|OVERVIEW|BACKGROUND|SUMMARY OF QUALIFICATIONS|PROFILE STATEMENT": "summary",
        r"EDUCATION|ACADEMIC BACKGROUND|ACADEMICS|QUALIFICATIONS": "education",
        r"EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT HISTORY|WORK HISTORY|INTERNSHIP|INTERNSHIPS|EMPLOYMENT": "experience",
        r"SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|TECHNICAL PROFICIENCIES|SKILLS & TECHNOLOGIES": "skills",
        r"PROJECTS|ACADEMIC PROJECTS|PERSONAL PROJECTS|KEY PROJECTS": "projects",
        r"CERTIFICATIONS|CERTIFICATES|LICENSES": "certifications",
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
        
        if len(line_clean) < 60:
            line_upper = line_clean.upper()
            
            for pattern, normalized_name in headings_map.items():
                if re.search(r"^\s*([•\-\d\.]*\s*)?(" + pattern + r")\s*[:-]?$", line_upper):
                    if current_content:
                        sections[current_section] = "\n".join(current_content).strip()
                    
                    current_section = normalized_name
                    current_content = []
                    is_heading = True
                    break
        
        if not is_heading:
            current_content.append(line_clean)
            
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
        
    # Fallback Summary extraction
    if not sections.get("summary") and sections.get("contact"):
        contact_lines = [l for l in sections["contact"].split('\n') if l.strip()]
        non_meta_lines = [
            l for l in contact_lines 
            if '@' not in l and not re.search(r'\d{10}', re.sub(r'[-.\s]', '', l)) 
            and not re.search(r'linkedin|github|http', l.lower())
        ]
        if len(non_meta_lines) >= 2:
            potential_summary = " ".join(non_meta_lines[1:]).strip()
            if len(potential_summary) > 25:
                sections["summary"] = potential_summary
        
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
