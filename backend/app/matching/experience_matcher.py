import re
import json
from app.models.resume import Resume
from app.models.job import Job

def _extract_years(text: str) -> float:
    if not text: return 0.0
    matches = re.findall(r'(\d+)\s*(?:\+|-)?\s*(?:\d+)?\s*year', text.lower())
    if matches:
        return float(matches[0])
    return 0.0

def match_experience(resume: Resume, job: Job) -> float:
    """
    Extracts experience in years from job requirements and compares with total resume experience.
    If candidate has NO work experience section on resume, returns 0.0 (0%).
    """
    has_exp_section = False
    exp_text = ""
    
    if resume.parsed_data:
        try:
            parsed = json.loads(resume.parsed_data)
            exp_list = parsed.get("experience", [])
            # Only count if non-empty real experience entries exist
            valid_entries = [e for e in exp_list if (e.get("raw") or e.get("description") or "").strip()]
            if valid_entries:
                has_exp_section = True
                exp_text = " ".join([e.get("raw", "") or e.get("description", "") for e in valid_entries])
        except Exception:
            pass

    # If candidate has NO work experience section at all (fresher student)
    if not has_exp_section:
        return 0.0

    resume_years = _extract_years(exp_text)
    if resume_years == 0.0 and has_exp_section:
        resume_years = 1.0 # Has experience section, default to 1 year

    job_years_req = 0.0
    if job.parsed_data:
        try:
            parsed_job = json.loads(job.parsed_data)
            exp_reqs = parsed_job.get("experience_requirements", [])
            for req in exp_reqs:
                yrs = _extract_years(req)
                if yrs > job_years_req:
                    job_years_req = yrs
        except Exception:
            pass

    if job_years_req == 0.0:
        return 100.0 if has_exp_section else 0.0

    score = min(100.0, (resume_years / job_years_req) * 100.0)
    return round(score, 2)
