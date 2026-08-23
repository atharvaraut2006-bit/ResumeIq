import json
from app.models.resume import Resume
from app.models.job import Job
from app.matching.semantic_engine import semantic_engine

def match_projects(resume: Resume, job: Job) -> float:
    """
    Evaluates project relevance against the overall job description text.
    Returns 0-100 score.
    """
    res_projs = []
    if resume.parsed_data:
        try:
            parsed = json.loads(resume.parsed_data)
            for proj in parsed.get("projects", []):
                desc = proj.get("description") or proj.get("raw") or ""
                if desc.strip(): res_projs.append(desc.strip())
        except Exception:
            pass
            
    if not res_projs and resume.raw_text:
        # Fallback: scan raw_text for project section or mentions
        res_projs = [resume.raw_text[:1500]]
        
    if not res_projs:
        return 50.0
        
    job_desc = job.description
    if not job_desc:
        return 50.0
        
    # See how relevant the projects are to the entire JD
    sims = semantic_engine.compute_similarity_batch(job_desc[:1000], res_projs) # JD might be huge, cap to 1000 chars for semantic comparison
    best_proj = max(sims)
    
    scaled = min(1.0, best_proj / 0.5) * 100
    return round(scaled, 2)
