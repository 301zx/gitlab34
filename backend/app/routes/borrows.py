from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from ..models import db, User, Book, BorrowRecord
from ..middleware.auth import admin_required

borrows_bp = Blueprint('borrows', __name__)

@borrows_bp.route('/borrow', methods=['POST'])
@jwt_required()
def borrow_book():
    """借阅图书"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('book_id'):
            return jsonify({'error': '请选择要借阅的图书'}), 400

        book_id = data['book_id']
        book = Book.query.get_or_404(book_id)

        # 检查图书是否可借
        if book.available_copies <= 0:
            return jsonify({'error': '该图书暂无库存'}), 400

        # 检查用户是否已达到最大借阅数量
        user = User.query.get(current_user_id)
        current_borrows = BorrowRecord.query.filter_by(
            user_id=current_user_id, 
            status='borrowed'
        ).count()

        max_borrows = 5  # 最大借阅数量
        if current_borrows >= max_borrows:
            return jsonify({'error': f'已达到最大借阅数量({max_borrows}本)'}), 400

        # 检查用户是否有逾期未还的图书
        overdue_borrows = BorrowRecord.query.filter_by(
            user_id=current_user_id, 
            status='overdue'
        ).count()
        if overdue_borrows > 0:
            return jsonify({'error': '您有逾期未还的图书，请先归还'}), 400

        # 创建借阅记录
        borrow_record = BorrowRecord(
            user_id=current_user_id,
            book_id=book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),  # 借阅期限30天
            status='borrowed'
        )

        # 更新图书库存
        book.available_copies -= 1

        db.session.add(borrow_record)
        db.session.commit()

        return jsonify({
            'message': '借阅成功',
            'borrow_record': borrow_record.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrows_bp.route('/return/<int:record_id>', methods=['POST'])
@jwt_required()
def return_book(record_id):
    """归还图书"""
    try:
        current_user_id = get_jwt_identity()
        borrow_record = BorrowRecord.query.get_or_404(record_id)

        # 检查权限：只能归还自己的图书或管理员操作
        if borrow_record.user_id != current_user_id:
            current_user = User.query.get(current_user_id)
            if current_user.role != 'admin':
                return jsonify({'error': '权限不足'}), 403

        # 检查图书是否已归还
        if borrow_record.status == 'returned':
            return jsonify({'error': '该图书已归还'}), 400

        book = Book.query.get(borrow_record.book_id)

        # 更新借阅记录
        borrow_record.return_date = datetime.utcnow()
        borrow_record.status = 'returned'

        # 计算罚金（如果有逾期）
        if borrow_record.due_date < datetime.utcnow():
            days_overdue = (datetime.utcnow() - borrow_record.due_date).days
            fine_rate = 0.5  # 每天0.5元
            borrow_record.fine_amount = days_overdue * fine_rate

        # 更新图书库存
        book.available_copies += 1

        db.session.commit()

        return jsonify({
            'message': '归还成功',
            'borrow_record': borrow_record.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrows_bp.route('/borrows/my', methods=['GET'])
@jwt_required()
def get_my_borrows():
    """获取我的借阅记录"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.getlist('status')

        query = BorrowRecord.query.filter_by(user_id=current_user_id)

        if status:
            query = query.filter(BorrowRecord.status.in_(status))

        # 按借阅时间倒序排列
        borrows = query.order_by(BorrowRecord.borrow_date.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        # 包含图书信息
        borrows_data = []
        for borrow in borrows.items:
            borrow_data = borrow.to_dict()
            borrow_data['book'] = borrow.book.to_dict()
            borrows_data.append(borrow_data)

        return jsonify({
            'borrows': borrows_data,
            'total': borrows.total,
            'page': borrows.page,
            'per_page': borrows.per_page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@borrows_bp.route('/borrows', methods=['GET'])
@jwt_required()
@admin_required
def get_all_borrows():
    """获取所有借阅记录（管理员权限）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        search = request.args.get('search', '')

        query = BorrowRecord.query

        if status:
            query = query.filter_by(status=status)

        if search:
            query = query.join(User).join(Book).filter(
                (User.username.contains(search)) |
                (Book.title.contains(search)) |
                (Book.author.contains(search))
            )

        borrows = query.order_by(BorrowRecord.borrow_date.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )

        # 包含用户和图书信息
        borrows_data = []
        for borrow in borrows.items:
            borrow_data = borrow.to_dict()
            borrow_data['user'] = borrow.user.to_dict()
            borrow_data['book'] = borrow.book.to_dict()
            borrows_data.append(borrow_data)

        return jsonify({
            'borrows': borrows_data,
            'total': borrows.total,
            'page': borrows.page,
            'per_page': borrows.per_page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@borrows_bp.route('/borrows/<int:record_id>/renew', methods=['POST'])
@jwt_required()
def renew_book(record_id):
    """续借图书"""
    try:
        current_user_id = get_jwt_identity()
        borrow_record = BorrowRecord.query.get_or_404(record_id)

        # 检查权限
        if borrow_record.user_id != current_user_id:
            return jsonify({'error': '只能续借自己的图书'}), 403

        # 检查是否已归还
        if borrow_record.status != 'borrowed':
            return jsonify({'error': '只能续借未归还的图书'}), 400

        # 检查是否已续借过（防止无限续借）
        if borrow_record.renewed:
            return jsonify({'error': '该图书已续借过一次，无法再次续借'}), 400

        # 续借30天
        borrow_record.due_date += timedelta(days=30)
        borrow_record.renewed = True

        db.session.commit()

        return jsonify({
            'message': '续借成功',
            'borrow_record': borrow_record.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@borrows_bp.route('/borrows/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_borrow_stats():
    """获取借阅统计（管理员权限）"""
    try:
        # 当前借阅数量
        current_borrows = BorrowRecord.query.filter_by(status='borrowed').count()
        
        # 逾期借阅数量
        overdue_borrows = BorrowRecord.query.filter_by(status='overdue').count()
        
        # 本月归还数量
        this_month = datetime.utcnow().replace(day=1)
        total_returns = BorrowRecord.query.filter(
            BorrowRecord.status == 'returned',
            BorrowRecord.return_date >= this_month
        ).count()
        
        # 累计罚金
        total_fines = db.session.query(db.func.sum(BorrowRecord.fine_amount)).scalar() or 0

        return jsonify({
            'current_borrows': current_borrows,
            'overdue_borrows': overdue_borrows,
            'total_returns': total_returns,
            'total_fines': float(total_fines)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500