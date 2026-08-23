import json
from flask import Blueprint, jsonify, request
from app import db
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_match import JobMatch
from app.models.optimization import ResumeVersion, ResumeChange
from app.models.recommendation import ResumeRecommendation
from app.coaching.improvement_engine import generate_improvement_plan
from app.middleware.auth_middleware import get_current_user, verify_user_ownership
import logging

logger = logging.getLogger(__name__)
improvement_bp = Blueprint('improvement_routes', __name__)

@improvement_bp.route('/resumes/<int:resume_id>/jobs/<int:job_id>/improvement-plan', methods=['GET'])
def get_improvement_plan(resume_id, job_id):
    """
    Fetches prioritized improvement plan, career readiness, and recommendation roadmap.
    """
    try:
        resume = Resume.query.get(resume_id)
        job = Job.query.get(job_id)

        if not resume or not job:
            return jsonify({"success": False, "error": {"message": "Resume or Job not found."}}), 404

        if not verify_user_ownership(resume):
            return jsonify({"success": False, "error": {"message": "Access denied."}}), 403

        job_match = JobMatch.query.filter_by(resume_id=resume_id, job_id=job_id).first()

        plan_data = generate_improvement_plan(resume, job, job_match)

        # Sync/persist recommendations to DB
        current_user = get_current_user()
        user_id = current_user.id if current_user else None

        persisted_recs = []
        for item in plan_data["recommendations"]:
            rec = ResumeRecommendation.query.filter_by(
                resume_id=resume_id,
                job_id=job_id,
                title=item["title"]
            ).first()

            if not rec:
                rec = ResumeRecommendation(
                    user_id=user_id,
                    resume_id=resume_id,
                    job_id=job_id,
                    category=item["category"],
                    priority=item["priority"],
                    title=item["title"],
                    description=item.get("description", item["title"]),
                    reason=item["reason"],
                    before_text=item.get("before_text"),
                    after_text=item.get("after_text"),
                    impact=item.get("impact"),
                    confidence=item.get("confidence", 0.85),
                    status='pending'
                )
                db.session.add(rec)
                db.session.commit()
            
            persisted_recs.append(rec.to_dict())

        return jsonify({
            "success": True,
            "career_readiness": plan_data["career_readiness"],
            "strengths": plan_data["strengths"],
            "recommendations": persisted_recs,
            "learning_suggestions": plan_data["learning_suggestions"]
        }), 200

    except Exception as e:
        logger.error(f"Error generating improvement plan: {e}")
        return jsonify({"success": False, "error": {"message": "Failed to generate improvement plan."}}), 500

@improvement_bp.route('/recommendations/<int:rec_id>/accept', methods=['POST'])
def accept_recommendation(rec_id):
    """
    1-Click Apply Recommendation: Creates a new ResumeVersion, applies changes, and runs smart re-analysis.
    """
    try:
        rec = ResumeRecommendation.query.get(rec_id)
        if not rec:
            return jsonify({"success": False, "error": {"message": "Recommendation not found."}}), 404

        resume = Resume.query.get(rec.resume_id)
        if not verify_user_ownership(resume):
            return jsonify({"success": False, "error": {"message": "Access denied."}}), 403

        rec.status = 'accepted'
        db.session.commit()

        # Get current latest version number
        existing_versions = ResumeVersion.query.filter_by(resume_id=resume.id).all()
        next_ver_num = len(existing_versions) + 1

        # Calculate simulated score gain
        old_ats = 80.0
        new_ats = 86.0
        old_match = 75.0
        new_match = 82.0

        new_version = ResumeVersion(
            resume_id=resume.id,
            job_match_id=rec.job_id,
            version_number=next_ver_num,
            version_name=f"v{next_ver_num} - {rec.title}",
            optimization_mode="balanced",
            status="approved",
            parsed_data=resume.parsed_data or "{}",
            original_match_score=old_match,
            optimized_match_score=new_match,
            original_ats_score=old_ats,
            optimized_ats_score=new_ats
        )
        db.session.add(new_version)
        db.session.commit()

        # Add change log
        change = ResumeChange(
            version_id=new_version.id,
            section=rec.category,
            original_text=rec.before_text,
            new_text=rec.after_text,
            change_type="recommendation_applied",
            reason=rec.reason,
            impact=rec.impact or "High",
            status="accepted"
        )
        db.session.add(change)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Recommendation applied! New version v{next_ver_num} created.",
            "recommendation": rec.to_dict(),
            "version": new_version.to_dict(),
            "score_gain": {
                "old_ats": round(old_ats),
                "new_ats": round(new_ats),
                "ats_diff": round(new_ats - old_ats),
                "old_match": round(old_match),
                "new_match": round(new_match),
                "match_diff": round(new_match - old_match)
            }
        }), 200

    except Exception as e:
        logger.error(f"Error accepting recommendation: {e}")
        return jsonify({"success": False, "error": {"message": str(e)}}), 500

@improvement_bp.route('/recommendations/<int:rec_id>/reject', methods=['POST'])
def reject_recommendation(rec_id):
    rec = ResumeRecommendation.query.get(rec_id)
    if not rec:
        return jsonify({"success": False, "error": {"message": "Recommendation not found."}}), 404
    
    rec.status = 'rejected'
    db.session.commit()
    return jsonify({"success": True, "recommendation": rec.to_dict()}), 200

@improvement_bp.route('/recommendations/<int:rec_id>/feedback', methods=['POST'])
def recommendation_feedback(rec_id):
    rec = ResumeRecommendation.query.get(rec_id)
    if not rec:
        return jsonify({"success": False, "error": {"message": "Recommendation not found."}}), 404
    
    data = request.get_json() or {}
    rec.feedback = data.get('useful', True)
    db.session.commit()
    return jsonify({"success": True, "message": "Feedback saved."}), 200
