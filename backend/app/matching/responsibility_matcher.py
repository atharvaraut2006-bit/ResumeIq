import json
from app.models.resume import Resume
from app.models.job import Job
from app.matching.semantic_engine import semantic_engine

def match_responsibilities(resume: Resume, job: Job) -> float:
    """
    Semantically compares Job responsibilities against Resume experience descriptions.
    If candidate has no work experience section, returns 0.0 (0%).
    """
    res_exps = []
    if resume.parsed_data:
        try:
            parsed = json.loads(resume.parsed_data)
            for exp in parsed.get("experience", []):
                desc = exp.get("description") or exp.get("raw") or ""
                if desc.strip():
                    res_exps.append(desc.strip())
        except Exception:
            pass
            
    # Candidate has NO work experience / responsibility bullet points
    if not res_exps:
        return 0.0

    job_resps = []
    if job.parsed_data:
        try:
            parsed = json.loads(job.parsed_data)
            job_resps = parsed.get("responsibilities", [])
        except Exception:
            pass
            
    if not job_resps:
        return None # No explicit responsibilities specified in JD

    total_score = 0
    for req in job_resps:
        sims = semantic_engine.compute_similarity_batch(req, res_exps)
        total_score += max(sims)
        
    avg = total_score / len(job_resps)
    scaled = min(1.0, avg / 0.6) * 100
    return round(scaled, 2)
