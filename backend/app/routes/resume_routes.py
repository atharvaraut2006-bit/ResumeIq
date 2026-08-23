import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.utils.validators import validate_file_level1
from app.services.pdf_service import extract_text_from_pdf
from app.services.resume_validator import validate_resume_content_level2
from app.models.resume import Resume
from app import db
from flask import current_app
import logging

resume_bp = Blueprint('resume', __name__)
logger = logging.getLogger(__name__)

@resume_bp.route('/resumes/upload', methods=['POST'])
def upload_resume():
    logger.info("Resume upload & 2-Level Validation started")
    
    if 'resume' not in request.files:
        return jsonify({"success": False, "error": {"code": "NO_FILE", "message": "No file part in the request."}}), 400
        
    file = request.files['resume']
    
    # 1. Level 1 File Validation
    is_valid_l1, err_code_l1, err_msg_l1 = validate_file_level1(file, current_app.config['MAX_CONTENT_LENGTH'])
    
    if not is_valid_l1:
        logger.warning(f"Level 1 File Validation failed: {err_code_l1}")
        return jsonify({
            "success": False, 
            "error": {
                "code": err_code_l1, 
                "message": err_msg_l1,
                "validation_status": err_code_l1
            }
        }), 400
        
    logger.info("Level 1 File Validation successful")
    
    original_filename = secure_filename(file.filename)
    stored_filename = f"{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
    
    try:
        file.save(file_path)
        
        # Extract raw text
        success_ext, result_text = extract_text_from_pdf(file_path)
        
        if not success_ext:
            if os.path.exists(file_path): os.remove(file_path)
            return jsonify({
                "success": False, 
                "error": {
                    "code": result_text, 
                    "message": "We couldn't read text from this file. Please ensure it is a valid text-based PDF or DOCX.",
                    "validation_status": "CORRUPTED_FILE"
                }
            }), 400
            
        # 2. Level 2 Resume Content Classification
        l2_result = validate_resume_content_level2(result_text)
        
        from app.middleware.auth_middleware import get_current_user, verify_user_ownership
        current_user = get_current_user()

        # Save resume record to DB with validation fields & user ownership
        new_resume = Resume(
            user_id=current_user.id if current_user else None,
            original_filename=original_filename,
            stored_filename=stored_filename,
            raw_text=result_text,
            validation_status=l2_result['status'],
            is_resume=l2_result['is_resume'],
            resume_confidence=l2_result['confidence'],
            validation_reason=l2_result['reason']
        )
        db.session.add(new_resume)
        db.session.commit()
        
        if not l2_result['is_resume']:
            logger.warning(f"Level 2 Resume Validation rejected document ID {new_resume.id}: {l2_result['reason']}")
            return jsonify({
                "success": False,
                "resume_id": new_resume.id,
                "validation": l2_result,
                "error": {
                    "code": l2_result['status'],
                    "message": l2_result['reason']
                }
            }), 400
            
        logger.info(f"Resume passed 2-Level Validation with confidence {l2_result['confidence']} (ID: {new_resume.id})")
        
        return jsonify({
            "success": True,
            "message": "Resume verified successfully.",
            "resume": new_resume.to_dict(),
            "validation": l2_result
        }), 201
        
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}")
        if os.path.exists(file_path): os.remove(file_path)
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred during upload."}}), 500

@resume_bp.route('/resumes/<int:resume_id>/parse', methods=['POST'])
def parse_resume_route(resume_id):
    logger.info(f"Resume parsing started for ID: {resume_id}")
    
    resume = Resume.query.get(resume_id)
    if not resume:
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resume not found."}}), 404
        
    from app.middleware.auth_middleware import verify_user_ownership
    if not verify_user_ownership(resume):
        return jsonify({"success": False, "error": {"code": "FORBIDDEN", "message": "Access denied. You do not own this resume."}}), 403
        
    # Backend Guard: Check validation status
    if resume.validation_status != 'VALID':
        return jsonify({
            "success": False, 
            "error": {
                "code": "INVALID_RESUME_DOCUMENT", 
                "message": resume.validation_reason or "Analysis blocked: This document was not identified as a valid resume."
            }
        }), 400
        
    if not resume.raw_text:
        return jsonify({"success": False, "error": {"code": "NO_TEXT", "message": "No extracted text available for this resume."}}), 400
        
    try:
        from app.services.resume_parser import parse_resume
        import json
        
        parsed_data = parse_resume(resume.raw_text)
        
        resume.parsed_data = json.dumps(parsed_data)
        db.session.commit()
        
        logger.info(f"Resume parsing completed for ID: {resume_id}")
        
        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "parsed_resume": parsed_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error during parsing for ID {resume_id}: {str(e)}")
        return jsonify({"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An error occurred while parsing."}}), 500
