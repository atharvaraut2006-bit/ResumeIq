import json
from app.models.job import Job, JobSkill
from app.services.job_section_detector import detect_job_sections
from app.services.job_requirement_extractor import extract_experience_requirements, extract_education_requirements, extract_soft_skills, extract_responsibilities
from app.services.skill_normalizer import extract_skills_from_text
from app.services.confidence_service import calculate_job_skill_confidence
from app.services.skill_extractor import _extract_snippet, _add_or_update_skill
from app import db
import logging

logger = logging.getLogger(__name__)

from app.services.skill_knowledge_base import initialize_knowledge_base

def analyze_and_store_job(job_id: int):
    """
    Analyzes JD text, extracts requirements and skills, normalizes them against the
    Skill KB, and stores them in JobSkill table.
    """
    job = Job.query.get(job_id)
    if not job or not job.description:
        raise ValueError("Job description not found")
        
    initialize_knowledge_base()
    text = job.description
    sections = detect_job_sections(text)
    
    extracted_skills_dict = {} # canonical_id -> data
    
    # Also extract skills from full text
    full_text_skills = extract_skills_from_text(text)
    for skill_id, matched_text in full_text_skills:
        extracted_skills_dict[skill_id] = {
            "importance": "required",
            "confidence": 0.85,
            "evidence_text": _extract_snippet(text, matched_text),
            "source_section": "general"
        }
    
    # Analyze sections for technical & soft skills
    for section_name, section_text in sections.items():
        importance = "optional"
        if section_name == "required_requirements":
            importance = "required"
        elif section_name == "preferred_requirements":
            importance = "preferred"
        elif section_name == "responsibilities":
            importance = "required" # Usually required if it's a responsibility
            
        found_skills = extract_skills_from_text(section_text)
        for skill_id, matched_text in found_skills:
            confidence = calculate_job_skill_confidence(section_name)
            snippet = _extract_snippet(section_text, matched_text)
            
            # If a skill was already found as optional/preferred, but now found as required, upgrade it.
            # _add_or_update_skill uses confidence, but we need custom logic for importance upgrading
            if skill_id in extracted_skills_dict:
                existing_imp = extracted_skills_dict[skill_id]["importance"]
                # Upgrade if necessary
                if importance == "required" and existing_imp != "required":
                    extracted_skills_dict[skill_id]["importance"] = "required"
                    extracted_skills_dict[skill_id]["confidence"] = confidence
                    extracted_skills_dict[skill_id]["evidence_text"] = snippet
                    extracted_skills_dict[skill_id]["source_section"] = section_name
            else:
                extracted_skills_dict[skill_id] = {
                    "importance": importance,
                    "confidence": confidence,
                    "evidence_text": snippet,
                    "source_section": section_name
                }
                
    # Also extract non-technical requirements
    experience = extract_experience_requirements(text)
    education = extract_education_requirements(text)
    soft_skills = extract_soft_skills(text)
    responsibilities = extract_responsibilities(sections.get("responsibilities", ""))
    
    parsed_data = {
        "experience_requirements": experience,
        "education_requirements": education,
        "soft_skills": soft_skills,
        "responsibilities": responsibilities
    }
    
    # Store parsed non-technical data
    job.parsed_data = json.dumps(parsed_data)
    
    # Store technical skills to database (JobSkill)
    JobSkill.query.filter_by(job_id=job.id).delete()
    
    final_skills = []
    for skill_id, data in extracted_skills_dict.items():
        js = JobSkill(
            job_id=job.id,
            skill_id=skill_id,
            importance=data["importance"],
            confidence=data["confidence"],
            evidence_text=data["evidence_text"],
            source_section=data["source_section"]
        )
        db.session.add(js)
        final_skills.append(js)
        
    db.session.commit()
    logger.info(f"Analyzed {len(final_skills)} skills for job {job_id}")
    
    # Combine everything for response
    result = {
        "title": job.title,
        "company": job.company,
        "required_skills": [js.to_dict() for js in final_skills if js.importance == "required"],
        "preferred_skills": [js.to_dict() for js in final_skills if js.importance == "preferred"],
        "optional_skills": [js.to_dict() for js in final_skills if js.importance == "optional"],
        **parsed_data
    }
    
    return result
