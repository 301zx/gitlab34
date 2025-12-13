from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role != 'admin':
                return jsonify({'error': '需要管理员权限'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return decorated_function

def own_resource_required(f):
    @wraps(f)
    def decorated_function(user_id, *args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user or (current_user.role != 'admin' and current_user_id != user_id):
                return jsonify({'error': '权限不足'}), 403
            
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    return decorated_function