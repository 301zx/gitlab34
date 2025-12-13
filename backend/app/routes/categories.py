from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Category
from ..middleware.auth import admin_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        categories = Category.query.all()
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    """创建分类（管理员权限）"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': '分类名称不能为空'}), 400

        # 检查分类名称是否已存在
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'error': '分类名称已存在'}), 400

        category = Category(
            name=data['name'],
            description=data.get('description', ''),
            parent_id=data.get('parent_id')
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'message': '分类创建成功',
            'category': category.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """更新分类（管理员权限）"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()

        if 'name' in data and data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category and existing_category.id != category_id:
                return jsonify({'error': '分类名称已存在'}), 400
            category.name = data['name']

        if 'description' in data:
            category.description = data['description']

        if 'parent_id' in data:
            category.parent_id = data['parent_id']

        db.session.commit()

        return jsonify({
            'message': '分类更新成功',
            'category': category.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """删除分类（管理员权限）"""
    try:
        category = Category.query.get_or_404(category_id)

        # 检查是否有子分类
        subcategories = Category.query.filter_by(parent_id=category_id).count()
        if subcategories > 0:
            return jsonify({'error': '该分类下有子分类，无法删除'}), 400

        # 检查是否有图书使用该分类
        books_count = category.books.count()
        if books_count > 0:
            return jsonify({'error': '该分类下有图书，无法删除'}), 400

        db.session.delete(category)
        db.session.commit()

        return jsonify({'message': '分类删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500