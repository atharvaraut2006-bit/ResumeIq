import logging
from app import db
from app.models.resume import Resume
from app.models.job import Job
from app.models.resume_skill import ResumeSkill
from app.models.job import JobSkill
from app.models.job_match import JobMatch, SkillMatch

from app.matching.config import MATCHING_CONFIG
from app.matching.skill_matcher import match_technical_skills
from app.matching.soft_skill_matcher import match_soft_skills
from app.matching.experience_matcher import match_experience
from app.matching.education_matcher import match_education
from app.matching.responsibility_matcher import match_responsibilities
from app.matching.project_matcher import match_projects

logger = logging.getLogger(__name__)

def generate_analysis(resume_id: int, job_id: int) -> JobMatch:
    resume = Resume.query.get(resume_id)
    job = Job.query.get(job_id)
    
    if not resume or not job:
        raise ValueError("Resume or Job not found")
        
    # Check for existing analysis to preserve Phase 6 requirements (Don't overwrite needlessly, or if we do, update it)
    job_match = JobMatch.query.filter_by(resume_id=resume_id, job_id=job_id).first()
    if job_match:
        # Clear existing skill matches to force fresh recalculation
        SkillMatch.query.filter_by(job_match_id=job_match.id).delete()
        db.session.commit()
    else:
        job_match = JobMatch(resume_id=resume_id, job_id=job_id)
        db.session.add(job_match)
        db.session.flush()
    
    # 1. & 2. Skills
    resume_skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
    job_skills = JobSkill.query.filter_by(job_id=job_id).all()
    
    tech_results = match_technical_skills(resume_skills, job_skills)
    soft_results = match_soft_skills(resume, job_skills)
    
    all_results = tech_results + soft_results
    
    skill_matches = []
    for r in all_results:
        sm = SkillMatch(
            job_match_id=job_match.id,
            skill_name=r["skill_name"],
            category=r["category"],
            match_type=r["match_type"],
            required=r["required"],
            confidence=r["confidence"],
            evidence=r["evidence"],
            related_skill=r["related_skill"]
        )
        skill_matches.append(sm)
        
    db.session.add_all(skill_matches)
    
    # Calculate tech and soft scores
    def calc_skill_score(results, is_required):
        filtered = [r for r in results if r["required"] == is_required]
        if not filtered: return None
        matched = sum(1 for r in filtered if r["match_type"] in ["exact", "normalized", "semantic"])
        partial = sum(0.5 for r in filtered if r["match_type"] == "partial")
        return ((matched + partial) / len(filtered)) * 100.0

    tech_req_score = calc_skill_score([r for r in tech_results], True)
    tech_pref_score = calc_skill_score([r for r in tech_results], False)
    
    # Leave as None if there are no requirements, so it gets excluded from weight
    job_match.technical_score = tech_req_score
    job_match.preferred_skill_score = tech_pref_score
    
    soft_score = calc_skill_score(soft_results, True)
    job_match.soft_skill_score = soft_score
    
    # 3. Experience
    job_match.experience_score = match_experience(resume, job)
    
    # 4. Education
    job_match.education_score = match_education(resume, job)
    
    # 5. Responsibilities
    job_match.responsibility_score = match_responsibilities(resume, job)
    
    # 6. Projects
    job_match.project_score = match_projects(resume, job)
    
    # 7. Certifications (Mock for now, leave as None unless we explicitly check)
    job_match.certification_score = None
    
    # CALCULATE OVERALL SCORE
    weights = MATCHING_CONFIG["weights"]
    total_weight = 0
    final_score = 0
    
    scores_map = {
        "technical_skills": job_match.technical_score,
        "soft_skills": job_match.soft_skill_score,
        "experience": job_match.experience_score,
        "responsibilities": job_match.responsibility_score,
        "projects": job_match.project_score,
        "education": job_match.education_score,
        "preferred_skills": job_match.preferred_skill_score,
        "certifications": job_match.certification_score
    }
    
    for category, score in scores_map.items():
        if score is not None:
            w = weights[category]
            total_weight += w
            final_score += score * w
            
    if total_weight > 0:
        job_match.overall_score = round(final_score / total_weight, 2)
    else:
        job_match.overall_score = 0.0
        
    db.session.commit()
    return job_match

def explain_score(job_match: JobMatch) -> list[str]:
    exps = []
    
    if job_match.technical_score is not None:
        if job_match.technical_score >= 80: exps.append("✓ Strong technical foundation")
        elif job_match.technical_score < 50: exps.append("⚠ Missing critical technical skills")
        
    if job_match.experience_score is not None:
        if job_match.experience_score >= 80: exps.append("✓ Experience meets requirements")
        else: exps.append("⚠ Experience falls short of requirements")
        
    if job_match.education_score is not None:
        if job_match.education_score == 100: exps.append("✓ Education requirement satisfied")
        
    if job_match.project_score is not None:
        if job_match.project_score >= 70: exps.append("✓ Relevant projects found")
    
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    missing = [sm.skill_name for sm in skill_matches if sm.match_type == "missing" and sm.required]
    if missing:
        exps.append(f"⚠ Missing required skills: {', '.join(missing[:3])}")
        
    return exps
