# reinitialize_db.py
"""
重新初始化数据库，应用所有模型更改
包括为Category.name添加唯一约束
"""
from app import create_app
from app import db
from app.models import User, Category, Book
from datetime import datetime

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 开始重新初始化数据库 ===")
    
    # 删除所有表
    print("1. 删除所有现有表...")
    db.drop_all()
    
    # 创建所有表
    print("2. 创建新表...")
    db.create_all()
    
    # 创建默认分类
    print("3. 创建默认分类...")
    categories = [
        Category(name="文学", description="小说、散文、诗歌等文学作品"),
        Category(name="科技", description="计算机、工程、数学等科技类图书"),
        Category(name="历史", description="历史研究、传记等"),
        Category(name="艺术", description="绘画、音乐、设计等艺术类图书"),
        Category(name="教育", description="教材、参考书等教育类图书")
    ]
    
    for category in categories:
        db.session.add(category)
    
    # 创建管理员账户
    print("4. 创建管理员账户...")
    admin = User(
        username='admin',
        email='admin@library.com',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # 创建测试图书
    print("5. 创建测试图书...")
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
            category_id=2,
            total_copies=3,
            available_copies=3
        )
    ]
    
    for book in books:
        db.session.add(book)
    
    # 提交更改
    print("6. 提交所有更改...")
    db.session.commit()
    
    print("\n=== 数据库重新初始化完成 ===")
    print("管理员账号: admin / admin123")
    print("已创建5个分类和2本测试图书")
    print("Category.name字段已添加唯一约束")
