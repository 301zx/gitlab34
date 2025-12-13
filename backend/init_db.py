# init_db.py
from app import create_app
from app.models import User, Category, Book
from app import db
from datetime import datetime

import os
from pathlib import Path

def init_database():
    # 创建Flask应用实例
    app = create_app()
    
    # 确保在应用上下文中操作
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认分类
        categories = [
            Category(name="文学", description="小说、散文、诗歌等文学作品"),
            Category(name="科技", description="计算机、工程、数学等科技类图书"),
            Category(name="历史", description="历史研究、传记等"),
            Category(name="艺术", description="绘画、音乐、设计等艺术类图书"),
            Category(name="教育", description="教材、参考书等教育类图书")
        ]
        
        for category in categories:
            if not Category.query.filter_by(name=category.name).first():
                db.session.add(category)
        
        # 创建管理员账户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@library.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # 创建测试图书
        books = [
            Book(
                isbn='9787115544301',
                title='Python编程从入门到实践',
                author='Eric Matthes',
                publisher='人民邮电出版社',
                publish_date=datetime.strptime('2020-01-01', '%Y-%m-%d').date(),
                category_id=1,
                total_copies=5,
                available_copies=5
            ),
            Book(
                isbn='9787115544302',
                title='Vue.js设计与实现',
                author='霍春阳',
                publisher='人民邮电出版社',
                publish_date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(),
                category_id=1,
                total_copies=3,
                available_copies=3
            )
        ]
        
        for book in books:
            if not Book.query.filter_by(isbn=book.isbn).first():
                db.session.add(book)
        
        db.session.commit()
        print("数据库初始化完成！")
        print("管理员账号: admin / admin123")

if __name__ == '__main__':
    init_database()