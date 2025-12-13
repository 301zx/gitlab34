from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Notification
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """获取当前用户的通知列表"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_read = request.args.get('is_read', type=bool)
        
        # 构建查询
        query = Notification.query.filter_by(user_id=user_id)
        
        # 按阅读状态筛选
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        
        # 按创建时间倒序排序
        query = query.order_by(Notification.created_at.desc())
        
        # 分页
        notifications = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'total': notifications.total,
            'page': notifications.page,
            'per_page': notifications.per_page,
            'pages': notifications.pages,
            'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_as_read(notification_id):
    """标记通知为已读"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 查找通知
        notification = Notification.query.get_or_404(notification_id)
        
        # 检查权限
        if notification.user_id != user_id:
            return jsonify({'error': '您没有权限操作此通知'}), 403
        
        # 标记为已读
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'message': '通知已标记为已读',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """删除通知"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 查找通知
        notification = Notification.query.get_or_404(notification_id)
        
        # 检查权限
        if notification.user_id != user_id:
            return jsonify({'error': '您没有权限操作此通知'}), 403
        
        # 删除通知
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({
            'message': '通知已删除'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_as_read():
    """标记所有通知为已读"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 更新所有通知为已读
        notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功标记 {len(notifications)} 条通知为已读'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
