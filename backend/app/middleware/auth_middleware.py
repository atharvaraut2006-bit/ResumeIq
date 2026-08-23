from functools import wraps
from flask import request, jsonify, g, session
from app.models.user import User
import jwt
from datetime import datetime, timedelta
from app.config import Config

JWT_SECRET = Config.SECRET_KEY or "jwt-super-secret-key-12345"

def generate_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def get_current_user():
    if hasattr(g, 'current_user') and g.current_user is not None:
        return g.current_user

    user = None
    auth_header = request.headers.get('Authorization')
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        decoded = decode_token(token)
        if decoded and 'user_id' in decoded:
            user = User.query.get(decoded['user_id'])
            
    if not user and 'user_id' in session:
        user = User.query.get(session['user_id'])

    g.current_user = user
    return user

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authentication required. Please sign in to access this resource."
                }
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def verify_user_ownership(resource) -> bool:
    """
    IDOR Protection Helper.
    Verifies that the resource belongs to the currently authenticated user.
    Allows guest resources (user_id is None) if request is unauthenticated or matching guest context.
    """
    if not resource:
        return True
        
    res_user_id = getattr(resource, 'user_id', None)
    if res_user_id is None:
        return True # Guest resource
        
    current_user = get_current_user()
    if not current_user:
        return False # Protected resource attempted by unauthenticated guest
        
    return res_user_id == current_user.id
