from app import db
from datetime import datetime

class JobMatch(db.Model):
    __tablename__ = 'job_matches'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    # Scores
    overall_score = db.Column(db.Float, nullable=True)
    technical_score = db.Column(db.Float, nullable=True)
    soft_skill_score = db.Column(db.Float, nullable=True)
    experience_score = db.Column(db.Float, nullable=True)
    responsibility_score = db.Column(db.Float, nullable=True)
    project_score = db.Column(db.Float, nullable=True)
    education_score = db.Column(db.Float, nullable=True)
    preferred_skill_score = db.Column(db.Float, nullable=True)
    certification_score = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resume = db.relationship('Resume', backref=db.backref('job_matches', lazy=True, cascade="all, delete-orphan"))
    job = db.relationship('Job', backref=db.backref('matches', lazy=True, cascade="all, delete-orphan"))
    skill_matches = db.relationship('SkillMatch', backref='job_match', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'resume_id': self.resume_id,
            'job_id': self.job_id,
            'overall_score': self.overall_score,
            'technical_score': self.technical_score,
            'soft_skill_score': self.soft_skill_score,
            'experience_score': self.experience_score,
            'responsibility_score': self.responsibility_score,
            'project_score': self.project_score,
            'education_score': self.education_score,
            'preferred_skill_score': self.preferred_skill_score,
            'certification_score': self.certification_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class SkillMatch(db.Model):
    __tablename__ = 'skill_matches'

    id = db.Column(db.Integer, primary_key=True)
    job_match_id = db.Column(db.Integer, db.ForeignKey('job_matches.id'), nullable=False)
    
    # Store the actual names directly if they aren't strictly linked to canonical skills
    skill_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=True) # technical, soft
    match_type = db.Column(db.String(50), nullable=False) # exact, normalized, semantic, partial, missing
    required = db.Column(db.Boolean, default=True)
    
    confidence = db.Column(db.Float, nullable=True)
    evidence = db.Column(db.Text, nullable=True)
    
    # Related/partial match info
    related_skill = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'job_match_id': self.job_match_id,
            'skill_name': self.skill_name,
            'category': self.category,
            'match_type': self.match_type,
            'required': self.required,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'related_skill': self.related_skill
        }
