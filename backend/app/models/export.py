from app import db
from datetime import datetime

class ResumeExport(db.Model):
    __tablename__ = 'resume_exports'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    resume_version_id = db.Column(db.Integer, db.ForeignKey('resume_versions.id'), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    template_id = db.Column(db.String(50), nullable=False, default='ats_focused')
    file_format = db.Column(db.String(10), nullable=False, default='pdf') # 'pdf' or 'docx'
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    ats_score = db.Column(db.Float, nullable=True)
    page_count = db.Column(db.Integer, nullable=True, default=1)
    status = db.Column(db.String(50), nullable=False, default='completed') # 'completed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "resume_version_id": self.resume_version_id,
            "job_id": self.job_id,
            "template_id": self.template_id,
            "file_format": self.file_format,
            "file_name": self.file_name,
            "ats_score": self.ats_score,
            "page_count": self.page_count,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
