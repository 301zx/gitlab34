from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, User
from ..middleware.auth import admin_required, own_resource_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """获取用户列表（管理员权限）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        role = request.args.get('role', '')
        # 处理 status 参数，支持单值和数组值
        # 同时处理 status 和 status[] 格式的参数
        status_values = request.args.getlist('status') + request.args.getlist('status[]')

        # 构建查询
        query = User.query

        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search))
            )

        if role:
            query = query.filter_by(role=role)

        if status_values:
            # 处理状态过滤逻辑
            active_filter = False
            inactive_filter = False
            for status in status_values:
                if status == 'active':
                    active_filter = True
                elif status == 'inactive':
                    inactive_filter = True
            
            if active_filter and inactive_filter:
                # 如果同时包含active和inactive，不过滤
                pass
            elif active_filter:
                query = query.filter_by(is_active=True)
            elif inactive_filter:
                query = query.filter_by(is_active=False)

        # 分页查询
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'page': users.page,
            'per_page': users.per_page,
            'pages': users.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取用户详情"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只能查看自己的信息或管理员查看所有信息
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': '权限不足'}), 403

        user = User.query.get_or_404(user_id)
        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        # 只能修改自己的信息或管理员修改所有信息
        if current_user.role != 'admin' and current_user_id != user_id:
            return jsonify({'error': '权限不足'}), 403

        user = User.query.get_or_404(user_id)
        data = request.get_json()

        # 更新字段
        if 'username' in data and data['username'] != user.username:
            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': '用户名已存在'}), 400
            user.username = data['username']

        if 'email' in data and data['email'] != user.email:
            # 检查邮箱是否已存在
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': '邮箱已存在'}), 400
            user.email = data['email']

        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']

        if 'is_active' in data and current_user.role == 'admin':
            user.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """删除用户（管理员权限）"""
    try:
        current_user_id = get_jwt_identity()
        
        # 不能删除自己
        if current_user_id == user_id:
            return jsonify({'error': '不能删除自己的账户'}), 400

        user = User.query.get_or_404(user_id)
        
        # 检查用户是否有未归还的图书
        if user.borrow_records.filter_by(status='borrowed').count() > 0:
            return jsonify({'error': '用户有未归还的图书，无法删除'}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': '用户删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新个人资料"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        data = request.get_json()

        if 'username' in data and data['username'] != user.username:
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({'error': '用户名已存在'}), 400
            user.username = data['username']

        if 'email' in data and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': '邮箱已存在'}), 400
            user.email = data['email']

        db.session.commit()

        return jsonify({
            'message': '个人资料更新成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        data = request.get_json()

        if not data.get('current_password'):
            return jsonify({'error': '请输入当前密码'}), 400

        if not data.get('new_password'):
            return jsonify({'error': '请输入新密码'}), 400

        # 验证当前密码
        if not user.check_password(data['current_password']):
            return jsonify({'error': '当前密码不正确'}), 400

        # 设置新密码
        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': '密码修改成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500