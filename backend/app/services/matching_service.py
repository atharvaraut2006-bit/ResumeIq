import logging
from app import db
from app.models.resume import Resume
from app.models.job import Job
from app.models.resume_skill import ResumeSkill
from app.models.job import JobSkill
from app.models.job_match import JobMatch, SkillMatch

logger = logging.getLogger(__name__)

def match_resume_to_job(resume_id: int, job_id: int) -> JobMatch:
    """
    Compares structured resume skills against parsed job requirements.
    Returns a JobMatch containing SkillMatch records.
    """
    resume = Resume.query.get(resume_id)
    job = Job.query.get(job_id)

    if not resume:
        raise ValueError(f"Resume with ID {resume_id} not found.")
    if not job:
        raise ValueError(f"Job with ID {job_id} not found.")

    # 1. Fetch skills
    resume_skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
    job_skills = JobSkill.query.filter_by(job_id=job_id).all()

    # Create lookup dictionary for resume skills by skill_id
    resume_skills_dict = {rs.skill_id: rs for rs in resume_skills}

    # Check if a match already exists for this resume and job.
    # If so, delete it so we can recalculate it fresh (deterministic)
    existing_match = JobMatch.query.filter_by(resume_id=resume_id, job_id=job_id).first()
    if existing_match:
        db.session.delete(existing_match)
        db.session.commit()

    # Create new JobMatch
    job_match = JobMatch(resume_id=resume_id, job_id=job_id)
    db.session.add(job_match)
    db.session.flush() # Flush to get the ID

    skill_matches = []
    
    # 2. Iterate through Job requirements
    for js in job_skills:
        skill_id = js.skill_id
        req_type = js.importance  # 'required' or 'preferred'
        job_evidence = js.evidence_text
        job_conf = js.confidence

        if skill_id in resume_skills_dict:
            # Match found
            rs = resume_skills_dict[skill_id]
            match_status = 'matched'
            resume_evidence = rs.evidence_text
            resume_conf = rs.confidence
            
            # Simple joint confidence: average of both (or min, or multiply)
            # Let's use multiplication of probabilities for joint confidence
            match_conf = round(resume_conf * job_conf, 4)
        else:
            # Missing
            match_status = 'missing'
            resume_evidence = None
            resume_conf = 0.0
            match_conf = 0.0

        sm = SkillMatch(
            job_match_id=job_match.id,
            skill_id=skill_id,
            requirement_type=req_type,
            match_status=match_status,
            match_confidence=match_conf,
            resume_confidence=resume_conf,
            job_confidence=job_conf,
            resume_evidence=resume_evidence,
            job_evidence=job_evidence
        )
        skill_matches.append(sm)

    db.session.add_all(skill_matches)
    db.session.commit()
    
    logger.info(f"Generated match for Resume {resume_id} and Job {job_id}")
    return job_match
