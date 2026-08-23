def calculate_resume_skill_confidence(source_section: str, evidence_type: str) -> float:
    """
    Calculates deterministic confidence for a resume skill based on where and how it was found.
    """
    if not source_section:
        source_section = "unknown"
        
    source = source_section.lower()
    
    if evidence_type == "explicit":
        if source == "skills":
            return 0.99
        elif source == "experience":
            return 0.95
        elif source == "projects":
            return 0.90
        elif source == "certifications":
            return 0.90
        elif source == "education":
            return 0.85
        else:
            return 0.80
            
    elif evidence_type == "inferred":
        if source == "experience":
            return 0.88
        elif source == "projects":
            return 0.85
        elif source == "summary":
            return 0.80
        else:
            return 0.75
            
    return 0.70

def calculate_job_skill_confidence(source_section: str) -> float:
    """
    Calculates deterministic confidence for a job requirement.
    """
    if not source_section:
        source_section = "unknown"
        
    source = source_section.lower()
    
    if source == "requirements":
        return 0.98
    elif source == "qualifications":
        return 0.96
    elif source == "responsibilities":
        return 0.85
    elif source == "nice_to_have":
        return 0.90
    else:
        return 0.80
