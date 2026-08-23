from app import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.Text, nullable=True) # Stored as JSON string
    
    # Phase Add-on: 2-Level Resume Validation Fields
    validation_status = db.Column(db.String(50), nullable=False, default='VALIDATING') # VALID, NOT_A_RESUME, UNSUPPORTED_FORMAT, CORRUPTED_FILE, EMPTY_FILE, LOW_CONFIDENCE
    is_resume = db.Column(db.Boolean, nullable=False, default=False)
    resume_confidence = db.Column(db.Float, nullable=False, default=0.0)
    validation_reason = db.Column(db.Text, nullable=True)
    validated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'validation_status': self.validation_status,
            'is_resume': self.is_resume,
            'resume_confidence': round(self.resume_confidence, 2),
            'validation_reason': self.validation_reason,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else self.created_at.isoformat(),
            'character_count': len(self.raw_text) if self.raw_text else 0
        }
