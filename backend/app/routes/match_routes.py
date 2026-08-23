from flask import Blueprint, jsonify
from app.matching.scoring_engine import generate_analysis, explain_score
from app.matching.config import get_score_category
from app.models.job_match import SkillMatch
import logging

logger = logging.getLogger(__name__)
match_bp = Blueprint('match_routes', __name__)

@match_bp.route('/resumes/<int:resume_id>/jobs/<int:job_id>/match', methods=['POST'])
def match_job(resume_id, job_id):
    """
    Executes the Phase 7 Intelligent Matching and Scoring pipeline.
    Guarded by Level 1 & 2 Resume Validation.
    """
    try:
        from app.models.resume import Resume
        resume = Resume.query.get(resume_id)
        if not resume or resume.validation_status != 'VALID':
            return jsonify({
                "success": False, 
                "error": {
                    "code": "INVALID_RESUME_DOCUMENT", 
                    "message": getattr(resume, 'validation_reason', None) or "Matching blocked: Document was not identified as a valid resume."
                }
            }), 400
            
        job_match = generate_analysis(resume_id, job_id)
        
        # Format skill matches
        skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
        
        matched_skills = [sm.to_dict() for sm in skill_matches if sm.match_type in ["exact", "normalized", "semantic"] and sm.category == "technical"]
        matched_soft = [sm.to_dict() for sm in skill_matches if sm.match_type in ["exact", "normalized", "semantic"] and sm.category == "soft"]
        missing_req = [sm.to_dict() for sm in skill_matches if sm.match_type == "missing" and sm.required]
        missing_pref = [sm.to_dict() for sm in skill_matches if sm.match_type == "missing" and not sm.required]
        related = [sm.to_dict() for sm in skill_matches if sm.match_type == "partial"]

        explanations = explain_score(job_match)
        score_category = get_score_category(job_match.overall_score)

        result = {
            "success": True,
            "job_match_id": job_match.id,
            "overall_score": job_match.overall_score,
            "score_category": score_category,
            "technical_score": job_match.technical_score,
            "soft_skill_score": job_match.soft_skill_score,
            "experience_score": job_match.experience_score,
            "responsibility_score": job_match.responsibility_score,
            "project_score": job_match.project_score,
            "education_score": job_match.education_score,
            "preferred_skill_score": job_match.preferred_skill_score,
            "certification_score": job_match.certification_score,
            "matched_skills": matched_skills,
            "matched_soft_skills": matched_soft,
            "missing_required_skills": missing_req,
            "missing_preferred_skills": missing_pref,
            "related_skills": related,
            "explanations": explanations,
            "job": job_match.job.to_dict() if job_match.job else None
        }
        
        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"Validation error during matching: {e}")
        return jsonify({"success": False, "error": {"code": "INVALID_INPUT", "message": str(e)}}), 400
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Internal error during matching: {e}")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(e), "traceback": tb}}), 500
