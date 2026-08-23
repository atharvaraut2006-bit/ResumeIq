from flask import Blueprint, request, jsonify
from app.models.job import Job
from app.services.job_parser import analyze_and_store_job
from app import db
import logging

job_bp = Blueprint('job', __name__)
logger = logging.getLogger(__name__)

@job_bp.route('/jobs', methods=['POST'])
def create_job():
    data = request.json
    if not data or 'description' not in data:
        return jsonify({"success": False, "error": {"code": "MISSING_DESCRIPTION", "message": "Job description is required."}}), 400
        
    description = data['description'].strip()
    if len(description) < 100:
        return jsonify({"success": False, "error": {"code": "DESCRIPTION_TOO_SHORT", "message": "Please enter a valid, longer job description."}}), 400
        
    try:
        from app.middleware.auth_middleware import get_current_user
        current_user = get_current_user()

        new_job = Job(
            user_id=current_user.id if current_user else None,
            title=data.get('title'),
            company=data.get('company'),
            description=description
        )
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "job": new_job.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Failed to create job."}}), 500

@job_bp.route('/jobs/<int:job_id>/analyze', methods=['POST'])
def analyze_job(job_id):
    logger.info(f"Job analysis requested for job {job_id}")
    
    try:
        result = analyze_and_store_job(job_id)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "analysis": result
        }), 200
        
    except ValueError as e:
        return jsonify({"success": False, "error": {"code": "INVALID_STATE", "message": str(e)}}), 400
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Error during job analysis: {e}")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": str(e), "traceback": tb}}), 500
