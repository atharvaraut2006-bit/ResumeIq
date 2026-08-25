from app.models.job_match import JobMatch, SkillMatch

def analyze_gaps(job_match: JobMatch):
    """
    Phase 8: Domain-Based Skill Gap Analysis.
    Classifies gaps into:
    1. Technical Skill Gaps
    2. Communication & Interpersonal Skill Gaps
    3. Leadership & Management Skill Gaps
    """
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    
    technical_gaps = []
    communication_gaps = []
    leadership_gaps = []
    
    soft_skill_gaps = []
    weak_evidence = []
    
    COMMUNICATION_KEYWORDS = {
        'communication', 'written communication', 'verbal communication', 
        'presentation', 'documentation', 'collaboration', 'interpersonal', 
        'stakeholder', 'negotiation', 'writing', 'speaking', 'articulate'
    }
    
    LEADERSHIP_KEYWORDS = {
        'leadership', 'team leadership', 'management', 'project management', 
        'agile', 'scrum', 'problem solving', 'time management', 'adaptability', 
        'critical thinking', 'decision making', 'mentorship', 'strategic', 
        'planning', 'coordination', 'ownership'
    }
    
    for sm in skill_matches:
        if sm.match_type == "missing":
            sname = sm.skill_name.lower()
            gap = {
                "skill": sm.skill_name,
                "required": sm.required,
                "confidence": 95,
                "reason": f"Skill missing from resume.",
                "action": f"If experienced with {sm.skill_name}, add it to your resume.",
                "category": sm.category
            }
            
            if any(k in sname for k in COMMUNICATION_KEYWORDS) or (sm.category == "soft" and "communicat" in sname):
                gap["domain"] = "communication"
                gap["priority"] = "moderate"
                communication_gaps.append(gap)
            elif any(k in sname for k in LEADERSHIP_KEYWORDS) or sm.category == "soft":
                gap["domain"] = "leadership"
                gap["priority"] = "low"
                leadership_gaps.append(gap)
            else:
                gap["domain"] = "technical"
                gap["priority"] = "high"
                technical_gaps.append(gap)
                
        elif sm.match_type == "semantic" and sm.category == "soft":
            if sm.confidence and sm.confidence < 0.80:
                weak_evidence.append({
                    "skill": sm.skill_name,
                    "evidence_found": sm.evidence,
                    "reason": f"Limited evidence for {sm.skill_name} detected.",
                    "action": f"Strengthen the phrasing to clearly demonstrate {sm.skill_name}.",
                    "priority": "low"
                })
                
    # Add non-skill gaps
    experience_gaps = []
    if job_match.experience_score is not None and job_match.experience_score < 100:
        experience_gaps.append("Experience falls short of requirements. Focus on demonstrating rapid impact in existing roles.")
        
    education_gaps = []
    if job_match.education_score is not None and job_match.education_score < 100:
        education_gaps.append("Missing preferred degree level. Emphasize relevant certifications or real-world project complexity.")
        
    project_gaps = []
    if job_match.project_score is not None and job_match.project_score < 50:
        project_gaps.append("Projects lack direct relevance to the JD requirements. Consider building a domain-specific project.")

    return {
        "skill_gaps": {
            "technical_gaps": technical_gaps,
            "communication_gaps": communication_gaps,
            "leadership_gaps": leadership_gaps,
            # Backwards compatibility aliases
            "high_priority": technical_gaps,
            "medium_priority": communication_gaps,
            "low_priority": leadership_gaps
        },
        "soft_skill_gaps": soft_skill_gaps,
        "weak_evidence": weak_evidence,
        "experience_gaps": experience_gaps,
        "education_gaps": education_gaps,
        "project_gaps": project_gaps,
        "learning_roadmap": []
    }
