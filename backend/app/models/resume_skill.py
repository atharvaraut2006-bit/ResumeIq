from app import db
from datetime import datetime

class ResumeSkill(db.Model):
    __tablename__ = 'resume_skills'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    evidence_type = db.Column(db.String(50), nullable=False) # 'explicit' or 'inferred'
    evidence_text = db.Column(db.Text, nullable=True)
    source_section = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resume = db.relationship('Resume', backref=db.backref('resume_skills', lazy=True, cascade="all, delete-orphan"))
    skill = db.relationship('Skill')

    # Ensure a resume doesn't have duplicate canonical skills
    __table_args__ = (
        db.UniqueConstraint('resume_id', 'skill_id', name='uq_resume_skill'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'skill': self.skill.to_dict() if self.skill else None,
            'confidence': self.confidence,
            'evidence_type': self.evidence_type,
            'evidence_text': self.evidence_text,
            'source_section': self.source_section
        }
