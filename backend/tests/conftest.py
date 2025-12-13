import pytest
from app import create_app
from app.models import db, User, Book, Category, BorrowRecord, Review
from datetime import datetime, timedelta
import json

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # 使用内存数据库
        "JWT_SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def database(app):
    """创建并初始化数据库"""
    with app.app_context():
        db.create_all()
        
        # 添加测试数据
        # 1. 添加分类
        category1 = Category(name="文学", description="文学作品")
        category2 = Category(name="科技", description="科技类图书")
        db.session.add_all([category1, category2])
        db.session.commit()
        
        # 2. 添加用户
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        user = User(username="user", email="user@example.com", role="user")
        user.set_password("user123")
        db.session.add_all([admin, user])
        db.session.commit()
        
        # 3. 添加图书
        book1 = Book(
            isbn="9787544270878",
            title="百年孤独",
            author="加西亚·马尔克斯",
            publisher="南海出版公司",
            publish_date=datetime(1967, 5, 30).date(),
            category_id=category1.id,
            total_copies=5,
            available_copies=5
        )
        book2 = Book(
            isbn="9787111676617",
            title="Python编程：从入门到实践",
            author="埃里克·马瑟斯",
            publisher="机械工业出版社",
            publish_date=datetime(2020, 7, 1).date(),
            category_id=category2.id,
            total_copies=3,
            available_copies=3
        )
        db.session.add_all([book1, book2])
        db.session.commit()
        
        yield db
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_token(client, database):
    """获取管理员JWT令牌"""
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    data = json.loads(response.data)
    return data["access_token"]

@pytest.fixture
def user_token(client, database):
    """获取普通用户JWT令牌"""
    response = client.post("/api/auth/login", json={
        "username": "user",
        "password": "user123"
    })
    data = json.loads(response.data)
    return data["access_token"]
