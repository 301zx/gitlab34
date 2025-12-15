from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Book, Category, User
from ..middleware.auth import admin_required
import os
import uuid
from datetime import datetime, date
from werkzeug.utils import secure_filename
from pathlib import Path

# 临时注释掉pandas，等安装完成后再取消注释
# import pandas as pd

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)
        publisher = request.args.get('publisher', '')
        min_publish_year = request.args.get('min_publish_year', type=int)
        max_publish_year = request.args.get('max_publish_year', type=int)
        available_only = request.args.get('available_only', type=bool, default=False)
        
        # 构建查询
        query = Book.query
        
        if search:
            query = query.filter(
                (Book.title.contains(search)) | 
                (Book.author.contains(search)) |
                (Book.isbn.contains(search))
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if publisher:
            query = query.filter(Book.publisher.contains(publisher))
        
        if min_publish_year:
            query = query.filter(
                db.extract('year', Book.publish_date) >= min_publish_year
            )
        
        if max_publish_year:
            query = query.filter(
                db.extract('year', Book.publish_date) <= max_publish_year
            )
        
        if available_only:
            query = query.filter(Book.available_copies > 0)
        
        # 分页
        books = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'books': [book.to_dict() for book in books.items],
            'total': books.total,
            'page': books.page,
            'per_page': books.per_page,
            'pages': books.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books', methods=['POST'])
@jwt_required()
@admin_required
def create_book():
    try:
        data = request.get_json()
        
        # 验证输入
        required_fields = ['isbn', 'title', 'author', 'category_id', 'total_copies']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field}是必填项'}), 400
        
        # 检查ISBN是否已存在
        if Book.query.filter_by(isbn=data['isbn']).first():
            return jsonify({'error': 'ISBN已存在'}), 400
        
        # 创建新图书
        publish_date_value = None
        if data.get('publish_date'):
            publish_date_value = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
        
        book = Book(
            isbn=data['isbn'],
            title=data['title'],
            author=data['author'],
            publisher=data.get('publisher'),
            publish_date=publish_date_value,
            category_id=data['category_id'],
            total_copies=data['total_copies'],
            available_copies=data['total_copies']
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': '图书添加成功',
            'book': book.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        return jsonify({'book': book.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        data = request.get_json()
        
        # 更新字段
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'publisher' in data:
            book.publisher = data['publisher']
        if 'publish_date' in data:
            if data['publish_date']:
                book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
            else:
                book.publish_date = None
        if 'category_id' in data:
            book.category_id = data['category_id']
        if 'total_copies' in data:
            # 更新可用副本数
            diff = data['total_copies'] - book.total_copies
            book.total_copies = data['total_copies']
            book.available_copies += diff
        
        db.session.commit()
        
        return jsonify({
            'message': '图书更新成功',
            'book': book.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        
        # 检查是否有相关的借阅记录
        if book.borrow_records.count() > 0:
            return jsonify({'error': '图书存在借阅记录，无法删除'}), 400
        
        # 检查是否有相关的评论记录
        if book.reviews.count() > 0:
            return jsonify({'error': '图书存在评论记录，无法删除'}), 400
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({'message': '图书删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/books/batch/import', methods=['POST'])
@jwt_required()
@admin_required
def batch_import_books():
    """批量导入图书（管理员权限）"""
    try:
        # 暂时禁用批量导入功能，因为pandas库尚未安装
        return jsonify({
            'error': '批量导入功能暂时不可用，请稍后重试'
        }), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500