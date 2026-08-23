import re
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from app import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.middleware.auth_middleware import generate_token, get_current_user, auth_required
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth_routes', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    """
    Creates a new user account with secure password hashing.
    """
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not name or len(name) < 2:
            return jsonify({"success": False, "error": {"message": "Please enter your full name."}}), 400

        if not email or not re.match(EMAIL_REGEX, email):
            return jsonify({"success": False, "error": {"message": "Please enter a valid email address."}}), 400

        if not password or len(password) < 6:
            return jsonify({"success": False, "error": {"message": "Password must be at least 6 characters long."}}), 400

        # Check email uniqueness
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "error": {"message": "An account with this email already exists."}}), 409

        user = User(name=name, email=email)
        user.set_password(password)
        user.last_login = datetime.utcnow()

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id)
        session['user_id'] = user.id

        return jsonify({
            "success": True,
            "token": token,
            "user": user.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"success": False, "error": {"message": "Internal error during account creation."}}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authenticates user credentials and issues JWT token.
    """
    try:
        data = request.get_json() or {}
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({"success": False, "error": {"message": "Email and password are required."}}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"success": False, "error": {"message": "Invalid email or password."}}), 401

        user.last_login = datetime.utcnow()
        db.session.commit()

        token = generate_token(user.id)
        session['user_id'] = user.id

        return jsonify({
            "success": True,
            "token": token,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"success": False, "error": {"message": "Internal error during sign in."}}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True, "message": "Signed out successfully."}), 200

@auth_bp.route('/auth/me', methods=['GET'])
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "user": None}), 200
    return jsonify({"success": True, "user": user.to_dict()}), 200

@auth_bp.route('/auth/convert-guest', methods=['POST'])
@auth_required
def convert_guest():
    """
    Transfers temporary guest resume and job resources to the authenticated user.
    """
    try:
        data = request.get_json() or {}
        resume_id = data.get('resume_id')
        current_user = get_current_user()

        if resume_id:
            resume = Resume.query.get(resume_id)
            if resume and (resume.user_id is None or resume.user_id == current_user.id):
                resume.user_id = current_user.id
                db.session.commit()
                return jsonify({"success": True, "resume": resume.to_dict()}), 200

        return jsonify({"success": True, "message": "Guest session converted."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": {"message": str(e)}}), 500
