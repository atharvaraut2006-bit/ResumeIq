from app import db
from datetime import datetime

class ResumeRecommendation(db.Model):
    __tablename__ = 'resume_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('resume_versions.id'), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    
    category = db.Column(db.String(50), nullable=False) # 'ats', 'missing_keywords', 'skills', 'experience', 'projects', 'summary', 'quantification', 'clarity'
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM') # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    
    before_text = db.Column(db.Text, nullable=True)
    after_text = db.Column(db.Text, nullable=True)
    
    impact = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=False, default=0.85) # 0.0 to 1.0
    
    status = db.Column(db.String(20), nullable=False, default='pending') # 'pending', 'accepted', 'rejected'
    feedback = db.Column(db.Boolean, nullable=True) # True for positive, False for negative
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'version_id': self.version_id,
            'job_id': self.job_id,
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'reason': self.reason,
            'before_text': self.before_text,
            'after_text': self.after_text,
            'impact': self.impact,
            'confidence': round(self.confidence * 100),
            'status': self.status,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat()
        }
