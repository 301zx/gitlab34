import json

def test_user_register(client, database):
    """测试用户注册"""
    new_user = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "confirm_password": "testpassword123"
    }
    response = client.post("/api/auth/register", json=new_user)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "注册成功"
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_user_login(client, database):
    """测试用户登录"""
    login_data = {
        "username": "user",
        "password": "user123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "user"


def test_admin_login(client, database):
    """测试管理员登录"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"
