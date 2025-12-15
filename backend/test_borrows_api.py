# test_borrows_api.py
"""
测试借阅记录API，查看为什么会返回422错误
"""
from app import create_app
from app.models import User, BorrowRecord
from flask_jwt_extended import create_access_token

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 测试借阅记录API ===")
    
    # 1. 检查数据库中的用户
    users = User.query.all()
    print(f"\n1. 数据库中用户数量: {len(users)}")
    for user in users:
        print(f"   - id: {user.id}, username: {user.username}, role: {user.role}")
    
    # 2. 检查借阅记录
    borrows = BorrowRecord.query.all()
    print(f"\n2. 数据库中借阅记录数量: {len(borrows)}")
    for borrow in borrows[:5]:
        print(f"   - id: {borrow.id}, user_id: {borrow.user_id}, book_id: {borrow.book_id}, status: {borrow.status}")
    
    # 3. 测试获取借阅记录API
    print(f"\n3. 测试获取借阅记录API")
    
    # 获取一个测试用户
    test_user = users[1] if len(users) > 1 else users[0]
    print(f"   测试用户: {test_user.username} (id: {test_user.id})")
    
    # 创建测试请求环境
    from flask.testing import FlaskClient
    client = app.test_client()
    
    # 获取JWT token，Flask-JWT-Extended 4.x要求identity必须是字符串类型
    access_token = create_access_token(identity=str(test_user.id))
    print(f"   JWT Token: {access_token[:20]}...")
    
    # 测试GET /api/borrows/my?status=borrowed
    print(f"\n4. 测试请求: GET /api/borrows/my?page=1&per_page=10&status=borrowed")
    response = client.get(
        '/api/borrows/my?page=1&per_page=10&status=borrowed',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.get_json()}")
    
    # 测试GET /api/borrows/my（不带status参数）
    print(f"\n5. 测试请求: GET /api/borrows/my?page=1&per_page=10")
    response = client.get(
        '/api/borrows/my?page=1&per_page=10',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    print(f"   响应状态码: {response.status_code}")
    print(f"   响应内容: {response.get_json()}")
    
    print("\n=== 测试完成 ===")
