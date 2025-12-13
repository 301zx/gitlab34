from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Reservation, Book, User
from datetime import datetime, timedelta
from ..middleware.auth import admin_required

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    """创建图书预约"""
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        
        if not book_id:
            return jsonify({'error': 'book_id是必填项'}), 400
        
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 检查图书是否存在
        book = Book.query.get_or_404(book_id)
        
        # 检查图书是否已可借阅（如果可借阅，不允许预约）
        if book.available_copies > 0:
            return jsonify({'error': '该图书当前可借阅，无需预约'}), 400
        
        # 检查用户是否已预约该图书
        existing_reservation = Reservation.query.filter_by(
            user_id=user_id, 
            book_id=book_id, 
            status='pending'
        ).first()
        
        if existing_reservation:
            return jsonify({'error': '您已预约该图书'}), 400
        
        # 创建预约记录，有效期为7天
        reservation = Reservation(
            user_id=user_id,
            book_id=book_id,
            status='pending',
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': '预约成功！',
            'reservation': reservation.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@jwt_required()
def cancel_reservation(reservation_id):
    """取消图书预约"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 查找预约记录
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # 检查权限（只有预约者或管理员可以取消）
        if reservation.user_id != user_id:
            # 检查是否是管理员
            current_user = User.query.get(user_id)
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': '您没有权限取消此预约'}), 403
        
        # 检查预约状态
        if reservation.status != 'pending':
            return jsonify({'error': '只能取消待处理的预约'}), 400
        
        # 取消预约
        reservation.status = 'canceled'
        db.session.commit()
        
        return jsonify({'message': '预约已取消'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservations_bp.route('/reservations/my', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """获取当前用户的预约列表"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查找当前用户的预约记录，分页查询
        reservations = Reservation.query.filter_by(user_id=user_id).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'reservations': [reservation.to_dict() for reservation in reservations.items],
            'total': reservations.total,
            'page': reservations.page,
            'per_page': reservations.per_page,
            'pages': reservations.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservations_bp.route('/reservations', methods=['GET'])
@jwt_required()
@admin_required
def get_all_reservations():
    """获取所有预约列表（管理员）"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查找所有预约记录，分页查询
        reservations = Reservation.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'reservations': [reservation.to_dict() for reservation in reservations.items],
            'total': reservations.total,
            'page': reservations.page,
            'per_page': reservations.per_page,
            'pages': reservations.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservations_bp.route('/reservations/<int:reservation_id>/fulfill', methods=['POST'])
@jwt_required()
@admin_required
def fulfill_reservation(reservation_id):
    """完成预约（管理员）"""
    try:
        # 查找预约记录
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # 检查预约状态
        if reservation.status != 'pending':
            return jsonify({'error': '只能完成待处理的预约'}), 400
        
        # 检查预约是否已过期
        if reservation.expires_at < datetime.utcnow():
            return jsonify({'error': '该预约已过期'}), 400
        
        # 更新预约状态
        reservation.status = 'fulfilled'
        db.session.commit()
        
        return jsonify({'message': '预约已完成'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
