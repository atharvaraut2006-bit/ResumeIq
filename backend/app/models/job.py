from app import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    parsed_data = db.Column(db.Text, nullable=True) # Stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'company': self.company,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class JobSkill(db.Model):
    __tablename__ = 'job_skills'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    importance = db.Column(db.String(50), nullable=False) # 'required', 'preferred', 'optional'
    confidence = db.Column(db.Float, nullable=False)
    evidence_text = db.Column(db.Text, nullable=True)
    source_section = db.Column(db.String(50), nullable=True)

    job = db.relationship('Job', backref=db.backref('job_skills', lazy=True, cascade="all, delete-orphan"))
    skill = db.relationship('Skill')

    __table_args__ = (
        db.UniqueConstraint('job_id', 'skill_id', name='uq_job_skill'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'skill': self.skill.to_dict() if self.skill else None,
            'importance': self.importance,
            'confidence': self.confidence,
            'evidence_text': self.evidence_text,
            'source_section': self.source_section
        }
