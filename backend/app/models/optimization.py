from app import db
from datetime import datetime

class OptimizationSuggestion(db.Model):
    __tablename__ = 'optimization_suggestions'

    id = db.Column(db.Integer, primary_key=True)
    job_match_id = db.Column(db.Integer, db.ForeignKey('job_matches.id'), nullable=False)
    
    section = db.Column(db.String(50), nullable=False) # 'summary', 'experience', 'projects', 'skills'
    original_text = db.Column(db.Text, nullable=True)
    suggested_text = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    impact = db.Column(db.String(50), nullable=False) # 'High', 'Medium', 'Low'
    
    status = db.Column(db.String(50), default='pending') # 'pending', 'accepted', 'rejected', 'edited'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'job_match_id': self.job_match_id,
            'section': self.section,
            'original_text': self.original_text,
            'suggested_text': self.suggested_text,
            'reason': self.reason,
            'impact': self.impact,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class ResumeVersion(db.Model):
    __tablename__ = 'resume_versions'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_match_id = db.Column(db.Integer, db.ForeignKey('job_matches.id'), nullable=True)
    
    version_number = db.Column(db.Integer, nullable=False, default=1)
    version_name = db.Column(db.String(255), nullable=False, default='Original Resume')
    optimization_mode = db.Column(db.String(50), nullable=False, default='balanced')
    parent_version_id = db.Column(db.Integer, db.ForeignKey('resume_versions.id'), nullable=True)
    
    status = db.Column(db.String(50), nullable=False, default='draft') # draft, generated, reviewed, approved, archived
    parsed_data = db.Column(db.Text, nullable=False) # The modified or original JSON resume
    
    original_match_score = db.Column(db.Float, nullable=True)
    optimized_match_score = db.Column(db.Float, nullable=True)
    original_ats_score = db.Column(db.Float, nullable=True)
    optimized_ats_score = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    changes = db.relationship('ResumeChange', backref='version', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_match_id': self.job_match_id,
            'version_number': self.version_number,
            'version_name': self.version_name,
            'optimization_mode': self.optimization_mode,
            'parent_version_id': self.parent_version_id,
            'status': self.status,
            'original_match_score': self.original_match_score,
            'optimized_match_score': self.optimized_match_score,
            'original_ats_score': self.original_ats_score,
            'optimized_ats_score': self.optimized_ats_score,
            'changes_count': len(self.changes) if self.changes else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else self.created_at.isoformat()
        }

class ResumeChange(db.Model):
    __tablename__ = 'resume_changes'

    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('resume_versions.id'), nullable=False)
    
    section = db.Column(db.String(50), nullable=False) # 'summary', 'skills', 'experience', 'projects', 'education', 'certifications'
    original_text = db.Column(db.Text, nullable=True)
    new_text = db.Column(db.Text, nullable=False)
    change_type = db.Column(db.String(50), nullable=False, default='rewrite') # rewrite, reorder, format, keyword_alignment, summary_update
    reason = db.Column(db.Text, nullable=False)
    impact = db.Column(db.String(50), nullable=False, default='Medium') # High, Medium, Low
    status = db.Column(db.String(50), nullable=False, default='pending') # pending, accepted, rejected, edited
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'version_id': self.version_id,
            'section': self.section,
            'original_text': self.original_text,
            'new_text': self.new_text,
            'change_type': self.change_type,
            'reason': self.reason,
            'impact': self.impact,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
