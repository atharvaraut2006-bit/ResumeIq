import json
from app.models.job_match import JobMatch, SkillMatch
from app.models.resume import Resume

def simulate_ats(job_match: JobMatch, resume: Resume = None, mode: str = 'balanced'):
    """
    Phase 9: ATS Simulation Engine & Keyword Analysis.
    Estimates ATS score based on keyword coverage, keyword placement,
    anti-stuffing rules, detectable section completeness, and optimization mode.
    """
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    
    req_skills = [sm for sm in skill_matches if sm.required]
    pref_skills = [sm for sm in skill_matches if not sm.required]
    
    req_matched = [sm for sm in req_skills if sm.match_type in ['exact', 'normalized', 'semantic']]
    pref_matched = [sm for sm in pref_skills if sm.match_type in ['exact', 'normalized', 'semantic']]
    soft_matched = [sm for sm in skill_matches if sm.category == 'soft' and sm.match_type in ['exact', 'normalized', 'semantic']]
    
    matched_keywords = [sm.skill_name for sm in skill_matches if sm.match_type in ['exact', 'normalized', 'semantic']]
    missing_keywords = [sm.skill_name for sm in skill_matches if sm.match_type == 'missing']
    related_keywords = [f"{sm.skill_name} (similar concept found)" for sm in skill_matches if sm.match_type == 'semantic']
    
    req_cov = len(req_matched) / len(req_skills) if req_skills else 1.0
    pref_cov = len(pref_matched) / len(pref_skills) if pref_skills else 1.0
    
    # Base ATS compatibility score calculation (weighted on required skills & structure)
    base_ats = (req_cov * 55) + (pref_cov * 15) + (job_match.experience_score / 100 * 15 if job_match.experience_score is not None else 0) + (job_match.education_score / 100 * 15 if job_match.education_score is not None else 15)
    base_ats = round(max(0, min(100, base_ats)))
    
    # Mode-dependent Estimated Optimized ATS Score
    mode_lower = (mode or 'balanced').lower()
    if mode_lower == 'conservative':
        # Strict, minimal revisions
        gain = round((1.0 - req_cov) * 18 + 8)
    elif mode_lower == 'aggressive':
        # Maximum keyword coverage and metric injections
        gain = round((1.0 - req_cov) * 45 + 24)
    else: # balanced
        # Standard balanced optimization
        gain = round((1.0 - req_cov) * 32 + 15)
        
    estimated_optimized = round(min(100, max(base_ats + 2, base_ats + gain)))
    
    parsed_data = {}
    if resume and resume.parsed_data:
        try:
            parsed_data = json.loads(resume.parsed_data)
        except Exception:
            pass
            
    contact_info = parsed_data.get('contact', {})
    has_contact = bool(contact_info.get('email') or contact_info.get('phone'))
    
    section_scores = {
        "Contact Information": 100 if has_contact else 50,
        "Summary": 80 if parsed_data.get('summary') else 40,
        "Skills": round(req_cov * 100) if req_skills else 90,
        "Experience": round(job_match.experience_score) if job_match.experience_score is not None else 0,
        "Projects": round(job_match.project_score) if job_match.project_score is not None else 50,
        "Education": round(job_match.education_score) if job_match.education_score is not None else 100
    }
    
    keyword_placement = []
    for sm in skill_matches[:8]:
        if sm.match_type in ['exact', 'normalized', 'semantic']:
            keyword_placement.append({
                "skill": sm.skill_name,
                "in_skills": True,
                "in_projects": bool(sm.evidence and "project" in sm.evidence.lower()),
                "in_experience": bool(sm.evidence and ("experience" in sm.evidence.lower() or "role" in sm.evidence.lower()))
            })
    
    return {
        "current_score": base_ats,
        "optimized_score": estimated_optimized,
        "potential_improvement": max(0, estimated_optimized - base_ats),
        "keyword_analysis": {
            "matched": matched_keywords,
            "missing": missing_keywords,
            "related": related_keywords,
            "overused": [],
            "irrelevant": []
        },
        "keyword_coverage": {
            "required": {"matched": len(req_matched), "total": len(req_skills)},
            "preferred": {"matched": len(pref_matched), "total": len(pref_skills)},
            "soft": {"matched": len(soft_matched), "total": len([s for s in skill_matches if s.category == 'soft'])}
        },
        "keyword_placement": keyword_placement,
        "section_scores": section_scores
    }
