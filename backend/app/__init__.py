import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
import logging

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # In production, restrict this
    db.init_app(app)

    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Register blueprints
    from app.routes.resume_routes import resume_bp
    from app.routes.job_routes import job_bp
    from app.routes.skill_routes import skill_bp
    from app.routes.match_routes import match_bp
    from app.routes.optimization_routes import optimization_bp
    from app.routes.export_routes import export_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.improvement_routes import improvement_bp

    app.register_blueprint(resume_bp, url_prefix='/api')
    app.register_blueprint(job_bp, url_prefix='/api')
    app.register_blueprint(skill_bp, url_prefix='/api')
    app.register_blueprint(match_bp, url_prefix='/api')
    app.register_blueprint(optimization_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(improvement_bp, url_prefix='/api')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "ResumeIQ Backend"
        })

    with app.app_context():
        # Import models here to avoid circular dependencies
        from app.models import user, resume, skill, resume_skill, job, optimization, export, recommendation
        db.create_all()
        
        # Ensure SQLite table column migrations
        try:
            import sqlite3
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                # Migrate resumes table
                existing_res_cols = [row[1] for row in c.execute('PRAGMA table_info(resumes)').fetchall()]
                new_res_cols = [
                    ('user_id', "INTEGER"),
                    ('validation_status', "TEXT DEFAULT 'VALID'"),
                    ('is_resume', "INTEGER DEFAULT 1"),
                    ('resume_confidence', "REAL DEFAULT 1.0"),
                    ('validation_reason', "TEXT"),
                    ('validated_at', "TEXT")
                ]
                for col_name, col_type in new_res_cols:
                    if col_name not in existing_res_cols:
                        c.execute(f"ALTER TABLE resumes ADD COLUMN {col_name} {col_type}")
                
                # Migrate jobs table
                existing_job_cols = [row[1] for row in c.execute('PRAGMA table_info(jobs)').fetchall()]
                if 'user_id' not in existing_job_cols:
                    c.execute("ALTER TABLE jobs ADD COLUMN user_id INTEGER")

                # Migrate resume_versions table
                existing_ver_cols = [row[1] for row in c.execute('PRAGMA table_info(resume_versions)').fetchall()]
                new_ver_cols = [
                    ('job_match_id', "INTEGER"),
                    ('version_number', "INTEGER DEFAULT 1"),
                    ('version_name', "TEXT DEFAULT 'Original Resume'"),
                    ('optimization_mode', "TEXT DEFAULT 'balanced'"),
                    ('parent_version_id', "INTEGER"),
                    ('status', "TEXT DEFAULT 'draft'"),
                    ('parsed_data', "TEXT DEFAULT '{}'"),
                    ('original_match_score', "REAL"),
                    ('optimized_match_score', "REAL"),
                    ('original_ats_score', "REAL"),
                    ('optimized_ats_score', "REAL"),
                    ('created_at', "TEXT"),
                    ('updated_at', "TEXT")
                ]
                for col_name, col_type in new_ver_cols:
                    if col_name not in existing_ver_cols:
                        c.execute(f"ALTER TABLE resume_versions ADD COLUMN {col_name} {col_type}")

                conn.commit()
                conn.close()
        except Exception as mig_err:
            logging.warning(f"Migration check skipped: {mig_err}")
        
        from app.services.skill_knowledge_base import initialize_knowledge_base
        initialize_knowledge_base()

    return app
