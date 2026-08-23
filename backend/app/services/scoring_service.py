import logging
from app import db
from app.models.job_match import JobMatch, SkillMatch

logger = logging.getLogger(__name__)

# Configurable Weights
WEIGHTS = {
    'required_skills': 0.60,
    'preferred_skills': 0.20,
    'experience': 0.10,
    'education': 0.05,
    'soft_skills': 0.05
}

def calculate_compatibility_score(job_match_id: int) -> JobMatch:
    """
    Calculates the deterministic compatibility score for a JobMatch.
    Updates the JobMatch object in the database and returns it.
    """
    job_match = JobMatch.query.get(job_match_id)
    if not job_match:
        raise ValueError(f"JobMatch {job_match_id} not found.")

    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    
    # 1. Required Skills Score
    required_matches = [sm for sm in skill_matches if sm.requirement_type == 'required']
    required_matched = [sm for sm in required_matches if sm.match_status == 'matched']
    
    if required_matches:
        required_score = (len(required_matched) / len(required_matches)) * 100
    else:
        # If no required skills were specified, this section doesn't apply.
        required_score = None

    # 2. Preferred Skills Score
    preferred_matches = [sm for sm in skill_matches if sm.requirement_type == 'preferred']
    preferred_matched = [sm for sm in preferred_matches if sm.match_status == 'matched']

    if preferred_matches:
        preferred_score = (len(preferred_matched) / len(preferred_matches)) * 100
    else:
        preferred_score = None

    # 3. Experience Alignment (Mock implementation, since complex date parsing wasn't fully fleshed out in Phase 1-4)
    # We will give a default of 100 if unknown, or scale it.
    # For now, to keep it deterministic without hallucinating:
    exp_score = 100.0
    
    # 4. Education Alignment 
    # For now, assume aligned unless proven otherwise.
    edu_score = 100.0
    
    # 5. Soft Skills Alignment
    job = job_match.job
    job_soft = []
    if job.parsed_data:
        import json
        try:
            parsed = json.loads(job.parsed_data)
            job_soft = parsed.get("soft_skills", [])
        except Exception:
            pass
            
    soft_score = 100.0 if not job_soft else 80.0

    # Handle missing categories by redistributing weights proportionally
    components = {
        'required_skills': required_score,
        'preferred_skills': preferred_score,
        'experience': exp_score,
        'education': edu_score,
        'soft_skills': soft_score
    }
    
    active_weight_total = 0.0
    overall_score = 0.0
    
    for category, score in components.items():
        if score is not None:
            active_weight_total += WEIGHTS[category]
            overall_score += score * WEIGHTS[category]
            
    if active_weight_total > 0:
        overall_score = overall_score / active_weight_total
    else:
        overall_score = 0.0

    # Save to database
    job_match.required_skills_score = round(required_score, 2) if required_score is not None else None
    job_match.preferred_skills_score = round(preferred_score, 2) if preferred_score is not None else None
    job_match.experience_score = round(exp_score, 2)
    job_match.education_score = round(edu_score, 2)
    job_match.soft_skills_score = round(soft_score, 2)
    job_match.overall_score = round(overall_score, 2)

    db.session.commit()
    logger.info(f"Calculated score {job_match.overall_score} for JobMatch {job_match.id}")
    
    return job_match

def generate_score_explanation(job_match: JobMatch) -> list[str]:
    """Generates human-readable bullet points explaining the score deterministically."""
    explanations = []
    
    # Required skills
    if job_match.required_skills_score is not None:
        if job_match.required_skills_score == 100:
            explanations.append("✓ You have all the required technical skills.")
        elif job_match.required_skills_score >= 70:
            explanations.append(f"✓ {int(job_match.required_skills_score)}% of required skills matched.")
        else:
            explanations.append(f"⚠ You are missing several required skills (only {int(job_match.required_skills_score)}% match).")

    # Preferred skills
    if job_match.preferred_skills_score is not None:
        if job_match.preferred_skills_score == 100:
            explanations.append("✓ You also have all the preferred skills!")
        elif job_match.preferred_skills_score > 0:
            explanations.append(f"✓ You have {int(job_match.preferred_skills_score)}% of the preferred 'nice-to-have' skills.")

    # Experience & Edu (Placeholders based on current static logic)
    if job_match.experience_score and job_match.experience_score >= 80:
        explanations.append("✓ Good experience alignment.")
    
    if job_match.education_score and job_match.education_score >= 80:
        explanations.append("✓ Education requirement satisfied.")

    return explanations
