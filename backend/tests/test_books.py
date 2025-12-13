import json
from datetime import datetime


def test_get_books(client, database, user_token):
    """测试获取图书列表"""
    response = client.get("/api/books", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "books" in data
    assert len(data["books"]) == 2


def test_get_book_detail(client, database, user_token):
    """测试获取图书详情"""
    response = client.get("/api/books/1", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["title"] == "百年孤独"
    assert data["author"] == "加西亚·马尔克斯"


def test_add_book(client, database, admin_token):
    """测试添加图书（管理员）"""
    new_book = {
        "isbn": "9787536692930",
        "title": "活着",
        "author": "余华",
        "publisher": "重庆出版社",
        "publish_date": "1993-05-01",
        "category_id": 1,
        "total_copies": 5,
        "available_copies": 5
    }
    response = client.post("/api/books", json=new_book, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "图书添加成功"
    assert data["book"]["title"] == "活着"


def test_update_book(client, database, admin_token):
    """测试更新图书（管理员）"""
    updated_book = {
        "title": "百年孤独（修订版）",
        "author": "加西亚·马尔克斯",
        "publisher": "南海出版公司",
        "publish_date": "1967-05-30",
        "category_id": 1,
        "total_copies": 5,
        "available_copies": 5
    }
    response = client.put("/api/books/1", json=updated_book, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "图书更新成功"
    assert data["book"]["title"] == "百年孤独（修订版）"


def test_delete_book(client, database, admin_token):
    """测试删除图书（管理员）"""
    response = client.delete("/api/books/1", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "图书删除成功"
    
    # 验证图书已删除
    response = client.get("/api/books/1", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 404
