import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models import db, User, Book, Category, BorrowRecord

def generate_test_data():
    """生成测试数据"""
    app = create_app()
    
    with app.app_context():
        print("开始生成测试数据...")
        
        # 创建测试用户
        test_users = []
        for i in range(1, 21):
            user = User(
                username=f'user{i}',
                email=f'user{i}@test.com',
                role='user'
            )
            user.set_password('password123')
            test_users.append(user)
        
        db.session.add_all(test_users)
        
        # 获取分类
        categories = Category.query.all()
        
        # 创建测试图书
        test_books = []
        books_data = [
            {"title": "Python编程从入门到实践", "author": "Eric Matthes", "isbn": "9787115544311"},
            {"title": "Vue.js设计与实现", "author": "霍春阳", "isbn": "9787115544312"},
            {"title": "JavaScript高级程序设计", "author": "Matt Frisbie", "isbn": "9787115544313"},
            {"title": "深入理解计算机系统", "author": "Randal E. Bryant", "isbn": "9787115544314"},
            {"title": "算法导论", "author": "Thomas H. Cormen", "isbn": "9787115544315"},
            {"title": "设计模式", "author": "Erich Gamma", "isbn": "9787115544316"},
            {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9787115544317"},
            {"title": "重构", "author": "Martin Fowler", "isbn": "9787115544318"},
            {"title": "人月神话", "author": "Frederick P. Brooks", "isbn": "9787115544319"},
            {"title": "代码大全", "author": "Steve McConnell", "isbn": "9787115544320"}
        ]
        
        for book_data in books_data:
            # 检查ISBN是否已存在
            existing_book = Book.query.filter_by(isbn=book_data['isbn']).first()
            if not existing_book:
                book = Book(
                    isbn=book_data['isbn'],
                    title=book_data['title'],
                    author=book_data['author'],
                    publisher="人民邮电出版社",
                    publish_date=datetime(2020 + random.randint(0, 3), random.randint(1, 12), random.randint(1, 28)),
                    category_id=random.choice(categories).id,
                    total_copies=random.randint(3, 10),
                    available_copies=random.randint(1, 10)
                )
                test_books.append(book)
        
        # 先保存图书到数据库，获取有效的ID
        db.session.add_all(test_books)
        db.session.commit()
        
        # 创建借阅记录
        borrow_records = []
        for i in range(50):
            user = random.choice(test_users)
            book = random.choice(test_books)
            
            # 确保图书有库存
            if book.available_copies > 0:
                borrow_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
                due_date = borrow_date + timedelta(days=30)
                
                # 随机设置一些已归还的记录
                if random.random() > 0.3:  # 70%的概率已归还
                    return_date = borrow_date + timedelta(days=random.randint(1, 35))
                    status = 'returned' if return_date <= due_date else 'overdue'
                else:
                    return_date = None
                    status = 'borrowed' if datetime.utcnow() <= due_date else 'overdue'
                
                record = BorrowRecord(
                    user_id=user.id,
                    book_id=book.id,
                    borrow_date=borrow_date,
                    due_date=due_date,
                    return_date=return_date,
                    status=status
                )
                
                borrow_records.append(record)
                
                # 更新图书库存
                if status == 'borrowed':
                    book.available_copies -= 1
        
        db.session.add_all(borrow_records)
        
        # 提交到数据库
        db.session.commit()
        
        print("测试数据生成完成！")
        print(f"创建了 {len(test_users)} 个测试用户")
        print(f"创建了 {len(test_books)} 本测试图书")
        print(f"创建了 {len(borrow_records)} 条借阅记录")
        print("管理员账号: admin / admin123")

if __name__ == '__main__':
    generate_test_data()