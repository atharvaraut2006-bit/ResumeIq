import json
import re
from app.models.resume import Resume
from app.models.job import Job

def _get_edu_level(text: str) -> int:
    if not text: return 0
    t = text.lower()
    if any(k in t for k in ['phd', 'doctorate']): return 4
    if any(k in t for k in ['master', 'm.tech', 'm.s', 'm.a', 'post graduate', 'mca', 'mba']): return 3
    if any(k in t for k in ['bachelor', 'b.tech', 'b.e', 'b.s', 'b.a', 'bca', 'bba', 'undergraduate', 'degree']): return 2
    if any(k in t for k in ['associate', 'diploma', '12th', '10th', 'high school', 'secondary', 'university', 'institute', 'college', 'school', 'vit', 'nptel', 'cgpa', 'gpa']): return 1
    return 0

def match_education(resume: Resume, job: Job) -> float:
    """
    Evaluates candidate education against JD education requirements with fallback scanning.
    Returns score between 0.0 and 100.0.
    """
    job_level = 0
    if job.parsed_data:
        try:
            parsed_job = json.loads(job.parsed_data)
            edu_reqs = parsed_job.get("education_requirements", [])
            for req in edu_reqs:
                lvl = _get_edu_level(req)
                if lvl > job_level:
                    job_level = lvl
        except Exception:
            pass

    # Check candidate education level from parsed_data
    res_level = 0
    if resume.parsed_data:
        try:
            parsed_res = json.loads(resume.parsed_data)
            for edu in parsed_res.get("education", []):
                degree_text = (edu.get("degree") or "") + " " + (edu.get("institution") or "") + " " + (edu.get("raw") or "")
                lvl = _get_edu_level(degree_text)
                if lvl > res_level:
                    res_level = lvl
        except Exception:
            pass

    # Direct raw text fallback check for degree/college terms
    if res_level == 0 and resume.raw_text:
        res_level = _get_edu_level(resume.raw_text)

    # Scenarios:
    if res_level > 0:
        if job_level == 0 or res_level >= job_level:
            return 100.0
        else:
            return 75.0
    else:
        if job_level == 0:
            return 100.0 # Standard requirement satisfied
        return 0.0
