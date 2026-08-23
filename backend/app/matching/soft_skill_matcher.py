from typing import List, Dict
from app.models.resume import Resume
from app.models.job import JobSkill
from app.matching.semantic_engine import semantic_engine
from app.matching.config import MATCHING_CONFIG
import json

def match_soft_skills(resume: Resume, job_skills: List[JobSkill]) -> List[Dict]:
    """
    Cross-references required soft skills against resume text/projects to find evidence.
    """
    results = []
    
    # Extract resume evidence blocks (experience, summary, projects, raw_text)
    evidence_blocks = []
    if resume.parsed_data:
        try:
            parsed = json.loads(resume.parsed_data)
            if parsed.get("summary"):
                evidence_blocks.append(parsed["summary"])
            if parsed.get("skills_raw"):
                evidence_blocks.append(parsed["skills_raw"])
            
            for exp in parsed.get("experience", []):
                desc = exp.get("description") or exp.get("raw") or ""
                if desc.strip():
                    evidence_blocks.append(desc.strip())
                    
            for proj in parsed.get("projects", []):
                desc = proj.get("description") or proj.get("raw") or ""
                if desc.strip():
                    evidence_blocks.append(desc.strip())
        except Exception:
            pass

    if not evidence_blocks and resume.raw_text:
        evidence_blocks = [resume.raw_text]

    strong_thresh = MATCHING_CONFIG["semantic_thresholds"]["strong_match"]
    
    for js in job_skills:
        if not js.skill or js.skill.category != "soft":
            continue
            
        req_type = js.importance
        js_name = js.skill.canonical_name
        
        best_sim = 0.0
        best_evidence = None
        
        if evidence_blocks:
            sims = semantic_engine.compute_similarity_batch(js_name, evidence_blocks)
            best_sim = max(sims)
            best_idx = sims.index(best_sim)
            best_evidence = evidence_blocks[best_idx]
            
        if best_sim >= strong_thresh:
            results.append({
                "skill_name": js_name,
                "category": "soft",
                "match_type": "semantic", # Evidence-backed
                "required": req_type == 'required',
                "confidence": round(best_sim, 4),
                "evidence": f"Found evidence in resume: \"{best_evidence[:100]}...\"",
                "related_skill": None
            })
        else:
            results.append({
                "skill_name": js_name,
                "category": "soft",
                "match_type": "missing",
                "required": req_type == 'required',
                "confidence": 0.0,
                "evidence": "No strong evidence found in resume experience or projects.",
                "related_skill": None
            })
            
    return results
