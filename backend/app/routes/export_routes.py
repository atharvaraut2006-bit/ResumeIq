import os
import json
from flask import Blueprint, jsonify, request, send_file
from app import db
from app.models.resume import Resume
from app.models.optimization import ResumeVersion
from app.models.export import ResumeExport
from app.models.job_match import JobMatch
from app.models.template import TEMPLATES_CONFIG
from app.export.pdf_generator import generate_pdf
from app.export.docx_generator import generate_docx
import logging

logger = logging.getLogger(__name__)
export_bp = Blueprint('export_routes', __name__)

EXPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'exports'))
os.makedirs(EXPORTS_DIR, exist_ok=True)

@export_bp.route('/resume/templates', methods=['GET'])
def get_templates():
    return jsonify({"success": True, "templates": TEMPLATES_CONFIG}), 200

@export_bp.route('/resume/versions/<int:version_id>/export', methods=['POST'])
def export_version(version_id):
    """
    Phase 11 Document Export API.
    Converts finalized resume version into downloadable PDF or DOCX file.
    """
    try:
        data = request.get_json() or {}
        template_id = data.get('template_id', 'ats_focused')
        file_format = data.get('file_format', 'pdf').lower() # 'pdf' or 'docx'
        sections_order = data.get('sections_order')
        included_sections = data.get('included_sections')
        
        version = ResumeVersion.query.get(version_id)
        if not version:
            # Fallback: check if version_id is a direct Resume ID
            resume = Resume.query.get(version_id)
            if not resume:
                return jsonify({"success": False, "error": {"message": "Resume record not found for export."}}), 404
            
            # Create default version for this resume
            existing_vers = ResumeVersion.query.filter_by(resume_id=resume.id).all()
            ver_num = len(existing_vers) + 1
            job_match = JobMatch.query.filter_by(resume_id=resume.id).first()
            
            try:
                version = ResumeVersion(
                    resume_id=resume.id,
                    job_match_id=job_match.id if job_match else None,
                    version_number=ver_num,
                    version_name=f"Original Resume v{ver_num}",
                    status="approved",
                    parsed_data=resume.parsed_data or "{}"
                )
                db.session.add(version)
                db.session.commit()
            except Exception as ver_err:
                db.session.rollback()
                version = None
        else:
            resume = Resume.query.get(version.resume_id)
            if not resume:
                return jsonify({"success": False, "error": {"message": "Original resume record not found."}}), 404
            
        parsed_resume = json.loads(version.parsed_data if (version and version.parsed_data) else (resume.parsed_data or '{}'))
        if not parsed_resume.get('contact'):
            parsed_resume['contact'] = json.loads(resume.parsed_data or '{}').get('contact', {})
            
        contact_name = parsed_resume.get('contact', {}).get('name') or "Atharva_Raut"
        safe_name = "".join(c for c in contact_name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_')
        filename = f"{safe_name}_Resume_Final.{file_format}"
        file_path = os.path.join(EXPORTS_DIR, f"{version_id}_{file_format}_{filename}")

        if file_format == 'docx':
            res = generate_docx(
                resume_data=parsed_resume,
                output_path=file_path,
                template_id=template_id,
                sections_order=sections_order,
                included_sections=included_sections
            )
            page_count = 1
        else:
            res = generate_pdf(
                resume_data=parsed_resume,
                output_path=file_path,
                template_id=template_id,
                sections_order=sections_order,
                included_sections=included_sections
            )
            page_count = res.get('page_count', 1)

        export_rec = ResumeExport(
            resume_id=resume.id,
            resume_version_id=version.id if version else None,
            job_id=getattr(version, 'job_match_id', None) if version else None,
            template_id=template_id,
            file_format=file_format,
            file_name=filename,
            file_path=file_path,
            ats_score=(version.optimized_ats_score if version else 85.0) or 85.0,
            page_count=page_count,
            status='completed'
        )
        db.session.add(export_rec)
        db.session.commit()

        return jsonify({
            "success": True,
            "export": export_rec.to_dict(),
            "download_url": f"/api/resume/exports/{export_rec.id}/download"
        }), 201

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Failed to generate document export: {e}")
        return jsonify({"success": False, "error": {"message": str(e), "traceback": tb}}), 500

@export_bp.route('/resume/versions/<int:version_id>/exports', methods=['GET'])
def get_export_history(version_id):
    try:
        exports = ResumeExport.query.filter_by(resume_version_id=version_id).order_by(ResumeExport.created_at.desc()).all()
        return jsonify({"success": True, "exports": [e.to_dict() for e in exports]}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500

@export_bp.route('/resume/exports/<int:export_id>/download', methods=['GET'])
def download_export(export_id):
    try:
        export_rec = ResumeExport.query.get(export_id)
        if not export_rec or not os.path.exists(export_rec.file_path):
            return jsonify({"success": False, "error": {"message": "Export file not found."}}), 404
            
        mimetype = 'application/pdf' if export_rec.file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return send_file(
            export_rec.file_path,
            as_attachment=True,
            download_name=export_rec.file_name,
            mimetype=mimetype
        )
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500
