# check_db.py
from app import create_app
from app import db
from sqlalchemy import inspect

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 数据库连接信息 ===")
    print(f"数据库URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print()
    
    print("=== 数据库表结构 ===")
    # 获取数据库中的所有表
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    for table in tables:
        print(f"\n表名: {table}")
        print("列信息:")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
    
    print("\n=== 数据统计 ===")
    # 导入模型类
    from app.models import User, Category, Book, BorrowRecord, Review, Reservation, Notification
    
    print(f"用户数量: {User.query.count()}")
    print(f"分类数量: {Category.query.count()}")
    print(f"图书数量: {Book.query.count()}")
    print(f"借阅记录: {BorrowRecord.query.count()}")
    print(f"评论数量: {Review.query.count()}")
    print(f"预约记录: {Reservation.query.count()}")
    print(f"通知数量: {Notification.query.count()}")
    
    print("\n=== 管理员账户 ===")
    admin = User.query.filter_by(role='admin').first()
    if admin:
        print(f"用户名: {admin.username}")
        print(f"邮箱: {admin.email}")
        print(f"角色: {admin.role}")
    
    print("\n=== 分类列表 ===")
    categories = Category.query.all()
    for category in categories:
        print(f"- {category.name}: {category.description}")
    
    print("\n=== 前5本图书 ===")
    books = Book.query.limit(5).all()
    for book in books:
        print(f"- {book.title} (作者: {book.author}, ISBN: {book.isbn})")
