import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    
    # Use absolute path for DB to prevent SQLite path resolution errors
    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    default_db_url = 'sqlite:///' + os.path.join(basedir, 'database', 'resumeiq.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default_db_url)
    
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite:///../'):
        SQLALCHEMY_DATABASE_URI = default_db_url
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE_MB', 5)) * 1024 * 1024
    RESUME_VALIDATION_THRESHOLD = 0.70
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
