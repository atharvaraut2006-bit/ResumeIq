from app import db
from datetime import datetime

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    canonical_name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    aliases = db.relationship('SkillAlias', backref='skill', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'canonical_name': self.canonical_name,
            'category': self.category
        }

class SkillAlias(db.Model):
    __tablename__ = 'skill_aliases'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    alias = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'skill_id': self.skill_id,
            'alias': self.alias
        }
