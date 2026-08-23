import json
from app.models.resume import Resume
from app.models.resume_skill import ResumeSkill
from app.services.skill_normalizer import normalize_skill_name, extract_skills_from_text
from app.services.confidence_service import calculate_resume_skill_confidence
from app import db
import logging

logger = logging.getLogger(__name__)

def extract_and_store_resume_skills(resume_id: int):
    """
    Extracts skills from parsed resume JSON, normalizes them, assigns confidence, 
    and stores them in ResumeSkill table.
    """
    resume = Resume.query.get(resume_id)
    if not resume or not resume.parsed_data:
        raise ValueError("Resume or parsed data not found")
        
    parsed_data = json.loads(resume.parsed_data)
    extracted_skills_dict = {} # Map canonical_skill_id -> {skill_obj, best_confidence, evidence_type, evidence_text, source_section}
    
    # 1. Process explicit skills from the "Skills" section
    skills_raw = parsed_data.get("skills_raw", "")
    if skills_raw:
        # Split by commas or newlines for explicit lists
        raw_list = [s.strip() for s in skills_raw.replace('\n', ',').split(',')]
        for raw_item in raw_list:
            if not raw_item: continue
            
            canonical_skill = normalize_skill_name(raw_item)
            if canonical_skill:
                # Add or update dictionary with highest confidence
                confidence = calculate_resume_skill_confidence("skills", "explicit")
                _add_or_update_skill(
                    extracted_skills_dict, canonical_skill, confidence, 
                    "explicit", raw_item, "skills"
                )
                
    # 2. Extract inferred skills from other sections (Experience, Projects, Summary)
    sections_to_scan = {
        "experience": _flatten_list(parsed_data.get("experience", [])),
        "projects": _flatten_list(parsed_data.get("projects", [])),
        "summary": parsed_data.get("summary", ""),
        "certifications": _flatten_list(parsed_data.get("certifications", []))
    }
    
    for section_name, section_text in sections_to_scan.items():
        if not section_text.strip():
            continue
            
        found_skills = extract_skills_from_text(section_text)
        for canonical_skill_id, matched_text in found_skills:
            # If found in experience/projects, it's inferred (unless they explicitly say "Skills: ...")
            # We'll treat all text block extractions as inferred for simplicity, 
            # though advanced NLP could differentiate.
            confidence = calculate_resume_skill_confidence(section_name, "inferred")
            
            # Find a short surrounding context snippet for evidence (max 100 chars)
            snippet = _extract_snippet(section_text, matched_text)
            
            _add_or_update_skill(
                extracted_skills_dict, canonical_skill_id, confidence, 
                "inferred", snippet, section_name
            )
            
    # 3. Store to Database (Idempotent: delete old ones first or use upsert)
    # We will delete existing skills for this resume and recreate them
    ResumeSkill.query.filter_by(resume_id=resume.id).delete()
    
    final_skills = []
    for skill_id, data in extracted_skills_dict.items():
        rs = ResumeSkill(
            resume_id=resume.id,
            skill_id=skill_id,
            confidence=data["confidence"],
            evidence_type=data["evidence_type"],
            evidence_text=data["evidence_text"],
            source_section=data["source_section"]
        )
        db.session.add(rs)
        final_skills.append(rs)
        
    db.session.commit()
    logger.info(f"Extracted {len(final_skills)} skills for resume {resume_id}")
    
    # Return formatted list
    return [rs.to_dict() for rs in final_skills]

def _add_or_update_skill(skills_dict, skill_id, confidence, evidence_type, evidence_text, source_section):
    """Helper to keep only the highest confidence evidence for a skill"""
    if skill_id not in skills_dict or confidence > skills_dict[skill_id]["confidence"]:
        skills_dict[skill_id] = {
            "confidence": confidence,
            "evidence_type": evidence_type,
            "evidence_text": evidence_text,
            "source_section": source_section
        }

def _flatten_list(data_list) -> str:
    """Helper to turn complex section arrays into flat text for searching"""
    if not isinstance(data_list, list):
        return ""
    texts = []
    for item in data_list:
        if isinstance(item, dict):
            # E.g., project has name, description
            texts.append(" ".join(str(v) for v in item.values() if v))
        else:
            texts.append(str(item))
    return " ".join(texts)

def _extract_snippet(full_text: str, match: str, padding=40) -> str:
    """Extracts a snippet of text surrounding the match."""
    try:
        idx = full_text.lower().find(match.lower())
        if idx == -1: return match
        
        start = max(0, idx - padding)
        end = min(len(full_text), idx + len(match) + padding)
        
        snippet = full_text[start:end].replace('\n', ' ').strip()
        if start > 0: snippet = "..." + snippet
        if end < len(full_text): snippet = snippet + "..."
        return snippet
    except:
        return match
