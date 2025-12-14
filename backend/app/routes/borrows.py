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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
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
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 处理 status 参数，支持单值和数组值
        # 同时处理 status 和 status[] 格式的参数
        status_values = request.args.getlist('status') + request.args.getlist('status[]')

        query = BorrowRecord.query.filter_by(user_id=current_user_id)

        if status_values:
            query = query.filter(BorrowRecord.status.in_(status_values))

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
            'per_page': borrows.per_page,
            'pages': borrows.pages
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
        # 同时处理 status 和 status[] 格式的参数
        status_values = request.args.getlist('status') + request.args.getlist('status[]')
        search = request.args.get('search', '')

        query = BorrowRecord.query

        if status_values:
            query = query.filter(BorrowRecord.status.in_(status_values))

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
        current_user_id = int(get_jwt_identity())
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

@borrows_bp.route('/borrows/batch/return', methods=['POST'])
@jwt_required()
@admin_required
def batch_return_books():
    """批量归还图书（管理员权限）"""
    try:
        data = request.get_json()
        record_ids = data.get('record_ids', [])

        if not record_ids or not isinstance(record_ids, list):
            return jsonify({'error': '请选择要归还的借阅记录'}), 400

        # 开始事务
        returned_count = 0
        errors = []

        for record_id in record_ids:
            try:
                borrow_record = BorrowRecord.query.get(record_id)
                if not borrow_record:
                    errors.append(f'借阅记录 {record_id} 不存在')
                    continue

                if borrow_record.status == 'returned':
                    errors.append(f'借阅记录 {record_id} 已归还')
                    continue

                # 更新借阅记录
                borrow_record.return_date = datetime.utcnow()
                borrow_record.status = 'returned'

                # 计算罚金（如果有逾期）
                if borrow_record.due_date < datetime.utcnow():
                    days_overdue = (datetime.utcnow() - borrow_record.due_date).days
                    fine_rate = 0.5  # 每天0.5元
                    borrow_record.fine_amount = days_overdue * fine_rate

                # 更新图书库存
                book = Book.query.get(borrow_record.book_id)
                book.available_copies += 1

                returned_count += 1
            except Exception as e:
                errors.append(f'处理借阅记录 {record_id} 时出错: {str(e)}')
                continue

        # 提交事务
        db.session.commit()

        return jsonify({
            'message': f'批量归还完成，成功归还 {returned_count} 本图书',
            'returned_count': returned_count,
            'errors': errors
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
        # 获取查询参数
        date_range = request.args.get('range', '7d')  # 7d, 30d, 90d
        
        # 计算日期范围
        now = datetime.utcnow()
        if date_range == '7d':
            start_date = now - timedelta(days=7)
        elif date_range == '30d':
            start_date = now - timedelta(days=30)
        elif date_range == '90d':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=7)  # 默认7天
        
        # 1. 概览数据
        total_books = Book.query.count()
        total_users = User.query.count()
        current_borrows = BorrowRecord.query.filter_by(status='borrowed').count()
        overdue_count = BorrowRecord.query.filter_by(status='overdue').count()
        
        # 2. 借阅趋势数据
        borrow_trend = []
        
        # 根据日期范围生成日期序列
        if date_range == '7d':
            # 最近7天，按天统计
            for i in range(7):
                date = now - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                # 统计当天借阅数量
                count = BorrowRecord.query.filter(
                    BorrowRecord.borrow_date >= date.replace(hour=0, minute=0, second=0, microsecond=0),
                    BorrowRecord.borrow_date < (date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
                
                borrow_trend.append({'date': date_str, 'count': count})
            
            # 反转列表，按日期升序
            borrow_trend = borrow_trend[::-1]
        else:
            # 最近30天或90天，按周统计
            weeks = []
            if date_range == '30d':
                weeks = 4
            else:
                weeks = 12
            
            for i in range(weeks):
                start_of_week = now - timedelta(weeks=i, days=now.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                
                week_str = f"{start_of_week.strftime('%m-%d')}~{end_of_week.strftime('%m-%d')}"
                
                # 统计本周借阅数量
                count = BorrowRecord.query.filter(
                    BorrowRecord.borrow_date >= start_of_week,
                    BorrowRecord.borrow_date < end_of_week + timedelta(days=1)
                ).count()
                
                borrow_trend.append({'date': week_str, 'count': count})
            
            # 反转列表，按日期升序
            borrow_trend = borrow_trend[::-1]
        
        # 3. 借阅状态分布
        status_distribution = []
        statuses = [
            ('borrowed', '已借阅'),
            ('returned', '已归还'),
            ('overdue', '已逾期')
        ]
        
        for status, name in statuses:
            count = BorrowRecord.query.filter_by(status=status).count()
            status_distribution.append({
                'name': name,
                'value': count
            })
        
        # 4. 热门图书（借阅次数最多的前10本）
        top_books = []
        
        # 使用SQLAlchemy查询借阅次数最多的图书
        book_borrow_counts = db.session.query(
            BorrowRecord.book_id,
            db.func.count(BorrowRecord.id).label('borrow_count')
        ).group_by(BorrowRecord.book_id).order_by(db.text('borrow_count DESC')).limit(10).all()
        
        for book_id, borrow_count in book_borrow_counts:
            book = Book.query.get(book_id)
            if book:
                top_books.append({
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'borrow_count': borrow_count
                })
        
        # 5. 用户借阅排名（借阅次数最多的前10个用户）
        top_users = []
        
        # 使用SQLAlchemy查询借阅次数最多的用户
        user_borrow_counts = db.session.query(
            BorrowRecord.user_id,
            db.func.count(BorrowRecord.id).label('borrow_count')
        ).group_by(BorrowRecord.user_id).order_by(db.text('borrow_count DESC')).limit(10).all()
        
        for user_id, borrow_count in user_borrow_counts:
            user = User.query.get(user_id)
            if user:
                top_users.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'borrow_count': borrow_count
                })
        
        # 返回所有统计数据
        return jsonify({
            'overview': {
                'totalBooks': total_books,
                'totalUsers': total_users,
                'currentBorrows': current_borrows,
                'overdueCount': overdue_count
            },
            'borrowTrend': borrow_trend,
            'statusDistribution': status_distribution,
            'topBooks': top_books,
            'topUsers': top_users
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500