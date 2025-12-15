from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, User
from ..middleware.auth import admin_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # 验证输入
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': '用户名、邮箱和密码是必填项'}), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # 生成访问令牌，Flask-JWT-Extended 4.x要求identity必须是字符串类型
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': '用户注册成功',
            'user': user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # 验证输入
        if not data.get('login') or not data.get('password'):
            return jsonify({'error': '登录名和密码是必填项'}), 400
        
        # 通过用户名或邮箱查找用户
        user = User.query.filter(
            (User.username == data['login']) | (User.email == data['login'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': '无效的登录名或密码'}), 401
        
        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 401
        
        # 生成访问令牌，Flask-JWT-Extended 4.x要求identity必须是字符串类型
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': '登录成功',
            'user': user.to_dict(),
            'token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500