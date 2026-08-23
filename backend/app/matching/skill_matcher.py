from typing import List, Dict, Tuple
from app.models.resume_skill import ResumeSkill
from app.models.job import JobSkill
from app.matching.semantic_engine import semantic_engine
from app.matching.config import MATCHING_CONFIG

def match_technical_skills(resume_skills: List[ResumeSkill], job_skills: List[JobSkill]) -> List[Dict]:
    """
    Compares technical skills to determine exact, normalized, semantic, partial, or missing matches.
    """
    results = []
    
    # Pre-process resume skills
    res_skill_dict = {rs.skill_id: rs for rs in resume_skills if rs.skill}
    res_skill_names = [rs.skill.canonical_name for rs in resume_skills if rs.skill]
    
    strong_thresh = MATCHING_CONFIG["semantic_thresholds"]["strong_match"]
    related_thresh = MATCHING_CONFIG["semantic_thresholds"]["related_match"]

    for js in job_skills:
        # We only match technical skills here (or general skills if category is mixed)
        # Soft skills will be handled by soft_skill_matcher
        if js.skill and js.skill.category == "soft":
            continue
            
        req_type = js.importance # 'required', 'preferred'
        js_name = js.skill.canonical_name if js.skill else "Unknown"
        
        # 1. Exact / Normalized Match (because skill_id is already normalized during extraction)
        if js.skill_id in res_skill_dict:
            rs = res_skill_dict[js.skill_id]
            results.append({
                "skill_name": js_name,
                "category": "technical",
                "match_type": "exact", # Treat canonical ID match as exact/normalized
                "required": req_type == 'required',
                "confidence": round(js.confidence * rs.confidence, 4),
                "evidence": rs.evidence_text,
                "related_skill": None
            })
            continue
            
        # 2. Semantic / Related Match
        if res_skill_names:
            sims = semantic_engine.compute_similarity_batch(js_name, res_skill_names)
            max_sim = max(sims)
            best_idx = sims.index(max_sim)
            best_res_name = res_skill_names[best_idx]
            
            if max_sim >= strong_thresh:
                results.append({
                    "skill_name": js_name,
                    "category": "technical",
                    "match_type": "semantic",
                    "required": req_type == 'required',
                    "confidence": round(max_sim, 4),
                    "evidence": f"Semantically matches your skill: {best_res_name}",
                    "related_skill": best_res_name
                })
                continue
            elif max_sim >= related_thresh:
                results.append({
                    "skill_name": js_name,
                    "category": "technical",
                    "match_type": "partial",
                    "required": req_type == 'required',
                    "confidence": round(max_sim, 4),
                    "evidence": f"Related experience detected: {best_res_name}",
                    "related_skill": best_res_name
                })
                continue
                
        # 3. Missing Match
        results.append({
            "skill_name": js_name,
            "category": "technical",
            "match_type": "missing",
            "required": req_type == 'required',
            "confidence": 0.0,
            "evidence": None,
            "related_skill": None
        })
        
    return results
