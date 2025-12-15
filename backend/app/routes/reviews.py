from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Review, Book, User
from app import db
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)

# 获取图书的评论列表
@reviews_bp.route('/books/<int:book_id>/reviews', methods=['GET'])
def get_book_reviews(book_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取图书
        book = Book.query.get_or_404(book_id)
        
        # 获取评论列表，包含用户信息
        reviews_query = Review.query.filter_by(book_id=book_id)
        reviews_pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
        
        reviews = []
        for review in reviews_pagination.items:
            user = User.query.get(review.user_id)
            reviews.append({
                'id': review.id,
                'book_id': review.book_id,
                'user_id': review.user_id,
                'username': user.username if user else '未知用户',
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            })
        
        return jsonify({
            'reviews': reviews,
            'total': reviews_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': reviews_pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 添加评论
@reviews_bp.route('/books/<int:book_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(book_id):
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        # 验证图书存在
        book = Book.query.get_or_404(book_id)
        
        # 验证用户存在
        user = User.query.get_or_404(current_user_id)
        
        # 验证评分范围
        rating = data.get('rating')
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': '评分必须是1-5之间的整数'}), 400
        
        # 创建评论
        review = Review(
            book_id=book_id,
            user_id=current_user_id,
            rating=rating,
            comment=data.get('comment', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': '评论添加成功',
            'review': {
                'id': review.id,
                'book_id': review.book_id,
                'user_id': review.user_id,
                'username': user.username,
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 更新评论
@reviews_bp.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    try:
        data = request.get_json()
        current_user_id = int(get_jwt_identity())
        
        # 获取评论
        review = Review.query.get_or_404(review_id)
        
        # 验证用户权限
        if review.user_id != current_user_id:
            return jsonify({'error': '无权修改此评论'}), 403
        
        # 更新评论
        if 'rating' in data:
            rating = data['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return jsonify({'error': '评分必须是1-5之间的整数'}), 400
            review.rating = rating
        
        if 'comment' in data:
            review.comment = data['comment']
        
        db.session.commit()
        
        user = User.query.get(review.user_id)
        return jsonify({
            'message': '评论更新成功',
            'review': {
                'id': review.id,
                'book_id': review.book_id,
                'user_id': review.user_id,
                'username': user.username if user else '未知用户',
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 删除评论
@reviews_bp.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    try:
        current_user_id = int(get_jwt_identity())
        
        # 获取评论
        review = Review.query.get_or_404(review_id)
        
        # 验证用户权限（评论所有者或管理员）
        user = User.query.get(current_user_id)
        if review.user_id != current_user_id and user.role != 'admin':
            return jsonify({'error': '无权删除此评论'}), 403
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({'message': '评论删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 获取用户的评论列表
@reviews_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 验证用户存在
        user = User.query.get_or_404(user_id)
        
        # 获取用户的评论列表，包含图书信息
        reviews_query = Review.query.filter_by(user_id=user_id)
        reviews_pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
        
        reviews = []
        for review in reviews_pagination.items:
            book = Book.query.get(review.book_id)
            reviews.append({
                'id': review.id,
                'book_id': review.book_id,
                'book_title': book.title if book else '未知图书',
                'book_author': book.author if book else '未知作者',
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            })
        
        return jsonify({
            'reviews': reviews,
            'total': reviews_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': reviews_pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取当前用户的评论列表
@reviews_bp.route('/reviews/my', methods=['GET'])
@jwt_required()
def get_my_reviews():
    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取当前用户的评论列表，包含图书信息
        reviews_query = Review.query.filter_by(user_id=current_user_id)
        reviews_pagination = reviews_query.paginate(page=page, per_page=per_page, error_out=False)
        
        reviews = []
        for review in reviews_pagination.items:
            book = Book.query.get(review.book_id)
            reviews.append({
                'id': review.id,
                'book_id': review.book_id,
                'book_title': book.title if book else '未知图书',
                'book_author': book.author if book else '未知作者',
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.isoformat()
            })
        
        return jsonify({
            'reviews': reviews,
            'total': reviews_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': reviews_pagination.pages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
