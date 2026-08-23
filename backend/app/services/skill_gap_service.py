from app.models.job_match import JobMatch, SkillMatch

def analyze_skill_gaps(job_match_id: int):
    """
    Sorts SkillMatch records into Strengths, Missing Required, and Missing Preferred.
    Returns a dictionary of categorized skills for the frontend.
    """
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match_id).all()
    
    strengths = []
    missing_required = []
    missing_preferred = []
    partially_matched = []  # Reserved for future knowledge base expansion
    
    for sm in skill_matches:
        if not sm.skill:
            continue
            
        skill_data = {
            "name": sm.skill.canonical_name,
            "category": sm.skill.category,
            "match_confidence": sm.match_confidence,
            "evidence": sm.resume_evidence if sm.match_status == 'matched' else sm.job_evidence
        }
        
        if sm.match_status == 'matched':
            strengths.append(skill_data)
        elif sm.match_status == 'missing':
            if sm.requirement_type == 'required':
                missing_required.append(skill_data)
            elif sm.requirement_type == 'preferred':
                missing_preferred.append(skill_data)
        elif sm.match_status == 'partially_matched':
            partially_matched.append(skill_data)
            
    # Sort strengths by confidence
    strengths = sorted(strengths, key=lambda x: x['match_confidence'] or 0.0, reverse=True)
    
    return {
        "strengths": strengths,
        "missing_required": missing_required,
        "missing_preferred": missing_preferred,
        "partially_matched": partially_matched
    }
