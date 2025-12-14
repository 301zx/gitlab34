# check_user_borrows.py
"""
检查用户的借阅记录，查看是否有逾期未还的图书
"""
from app import create_app
from app.models import db, User, BorrowRecord
from datetime import datetime

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 检查用户借阅记录 ===")
    
    # 获取所有用户
    users = User.query.all()
    
    for user in users:
        print(f"\n用户: {user.username} (id: {user.id}, role: {user.role})")
        
        # 获取用户的所有借阅记录
        borrows = BorrowRecord.query.filter_by(user_id=user.id).all()
        print(f"借阅记录数量: {len(borrows)}")
        
        if borrows:
            for borrow in borrows:
                status = borrow.status
                due_date = borrow.due_date
                return_date = borrow.return_date
                is_overdue = due_date < datetime.utcnow()
                
                print(f"- 记录ID: {borrow.id}, 图书ID: {borrow.book_id}, 状态: {status}, 应还日期: {due_date}, 实际归还日期: {return_date}, 已逾期: {is_overdue}")
        
        # 检查是否有逾期记录
        overdue_count = BorrowRecord.query.filter(
            BorrowRecord.user_id == user.id,
            BorrowRecord.status == 'overdue'
        ).count()
        
        borrowed_count = BorrowRecord.query.filter(
            BorrowRecord.user_id == user.id,
            BorrowRecord.status == 'borrowed'
        ).count()
        
        print(f"逾期记录数量: {overdue_count}")
        print(f"当前借阅数量: {borrowed_count}")
        
        if overdue_count > 0:
            print(f"⚠️  用户 {user.username} 有 {overdue_count} 条逾期记录")
            # 查看具体的逾期记录
            overdue_records = BorrowRecord.query.filter(
                BorrowRecord.user_id == user.id,
                BorrowRecord.status == 'overdue'
            ).all()
            for record in overdue_records:
                print(f"  - 逾期记录ID: {record.id}, 图书ID: {record.book_id}, 应还日期: {record.due_date}")
        else:
            print(f"✅ 用户 {user.username} 没有逾期记录")
    
    print("\n=== 检查完成 ===")
