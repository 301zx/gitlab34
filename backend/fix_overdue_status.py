# fix_overdue_status.py
"""
修复所有已归还但状态仍为overdue的借阅记录
将这些记录的状态从overdue更新为returned
"""
from app import create_app
from app.models import db, BorrowRecord
from datetime import datetime

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 修复已归还但状态为overdue的记录 ===")
    
    # 查找所有已归还但状态为overdue的记录
    fixed_count = 0
    
    # 方法1：查找有return_date且状态为overdue的记录
    overdue_but_returned = BorrowRecord.query.filter(
        BorrowRecord.status == 'overdue',
        BorrowRecord.return_date.isnot(None)
    ).all()
    
    print(f"找到 {len(overdue_but_returned)} 条已归还但状态为overdue的记录")
    
    if overdue_but_returned:
        for record in overdue_but_returned:
            print(f"修复记录: ID={record.id}, 图书ID={record.book_id}, 用户ID={record.user_id}, 应还日期={record.due_date}, 归还日期={record.return_date}")
            record.status = 'returned'
            fixed_count += 1
    
    # 提交更改
    if fixed_count > 0:
        db.session.commit()
        print(f"\n✅ 成功修复 {fixed_count} 条记录")
    else:
        print("\n✅ 没有需要修复的记录")
    
    # 验证修复结果
    print("\n=== 验证修复结果 ===")
    remaining_overdue = BorrowRecord.query.filter(
        BorrowRecord.status == 'overdue',
        BorrowRecord.return_date.isnot(None)
    ).count()
    
    print(f"仍有 {remaining_overdue} 条已归还但状态为overdue的记录")
    
    if remaining_overdue == 0:
        print("✅ 所有记录已修复完成")
    else:
        print(f"⚠️  还有 {remaining_overdue} 条记录需要修复")
    
    print("\n=== 修复完成 ===")
