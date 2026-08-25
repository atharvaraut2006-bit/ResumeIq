from app.models.job_match import JobMatch, SkillMatch

def analyze_gaps(job_match: JobMatch):
    """
    Phase 8: Skill Gap Analysis & Priority Ranking.
    Consumes Phase 7 output.
    Pure JD-Based Priority Classification:
    - High Priority: Mandatory Technical Skills required by the JD.
    - Moderate Priority: Mandatory Soft Skills & Secondary Technical Requirements.
    - Low Priority: Optional / Preferred Skills listed in the JD.
    """
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    soft_skill_gaps = []
    weak_evidence = []
    
    for sm in skill_matches:
        if sm.match_type == "missing":
            gap = {
                "skill": sm.skill_name,
                "required": sm.required,
                "confidence": 95,
                "reason": f"Skill missing from resume.",
                "action": f"If experienced with {sm.skill_name}, add it to your resume.",
                "category": sm.category
            }
            
            if sm.required and sm.category == "technical":
                gap["priority"] = "high"
                high_priority.append(gap)
            elif sm.required or sm.category == "soft":
                gap["priority"] = "moderate"
                medium_priority.append(gap)
            else:
                gap["priority"] = "low"
                low_priority.append(gap)
                
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
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        },
        "soft_skill_gaps": soft_skill_gaps,
        "weak_evidence": weak_evidence,
        "experience_gaps": experience_gaps,
        "education_gaps": education_gaps,
        "project_gaps": project_gaps,
        "learning_roadmap": []
    }
