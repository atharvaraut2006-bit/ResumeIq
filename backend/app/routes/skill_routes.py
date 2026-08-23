from flask import Blueprint, jsonify
from app.services.skill_extractor import extract_and_store_resume_skills
from app.models.resume import Resume
import logging

skill_bp = Blueprint('skill', __name__)
logger = logging.getLogger(__name__)

@skill_bp.route('/resumes/<int:resume_id>/extract-skills', methods=['POST'])
def extract_skills(resume_id):
    logger.info(f"Skill extraction requested for resume {resume_id}")
    
    resume = Resume.query.get(resume_id)
    if not resume:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resume not found."}}), 404
        
    try:
        skills = extract_and_store_resume_skills(resume_id)
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "skills": skills
        }), 200
        
    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "INVALID_STATE", "message": str(e)}}), 400
    except Exception as e:
        logger.error(f"Error during skill extraction: {e}")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Failed to extract skills."}}), 500
