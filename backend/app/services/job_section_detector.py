import re
from typing import Dict

def detect_job_sections(text: str) -> Dict[str, str]:
    """
    Splits a job description into logical sections.
    """
    sections = {}
    current_section = "description" # Default
    current_content = []
    
    # Common JD headings
    headings_map = {
        r"ABOUT THE ROLE|JOB DESCRIPTION|WHAT YOU'LL DO": "description",
        r"RESPONSIBILITIES|WHAT YOU WILL BE DOING|KEY RESPONSIBILITIES": "responsibilities",
        r"REQUIREMENTS|REQUIRED QUALIFICATIONS|MINIMUM QUALIFICATIONS|MUST HAVE": "required_requirements",
        r"PREFERRED QUALIFICATIONS|NICE TO HAVE|PREFERRED SKILLS|BONUS": "preferred_requirements",
        r"SKILLS|TECHNICAL SKILLS": "skills",
        r"EDUCATION": "education",
        r"EXPERIENCE": "experience"
    }
    
    lines = text.split('\n')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        is_heading = False
        
        # Check if line is a heading
        if len(line_clean) < 50: 
            line_upper = line_clean.upper()
            # Remove punctuation for matching
            clean_upper = re.sub(r'[^\w\s]', '', line_upper).strip()
            
            for pattern, normalized_name in headings_map.items():
                if re.fullmatch(r"^(" + pattern + r")$", clean_upper):
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
        
    # Fallback: if no explicit 'required' section is found, but 'skills' is, map skills to required
    if "skills" in sections and "required_requirements" not in sections:
        sections["required_requirements"] = sections["skills"]
        
    return sections
