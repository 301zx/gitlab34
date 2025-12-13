import os
import schedule
import time
from datetime import datetime
from app import create_app
from app.models import db, BorrowRecord

def check_overdue_books():
    """检查逾期图书"""
    app = create_app()
    
    with app.app_context():
        try:
            # 查找借阅中且已过期的记录
            overdue_records = BorrowRecord.query.filter(
                BorrowRecord.status == 'borrowed',
                BorrowRecord.due_date < datetime.utcnow()
            ).all()
            
            for record in overdue_records:
                record.status = 'overdue'
                # 计算罚金
                days_overdue = (datetime.utcnow() - record.due_date).days
                record.fine_amount = days_overdue * 0.5  # 每天0.5元
            
            db.session.commit()
            print(f"{datetime.datetime.now(datetime.timezone.utc)}: 检查完成，发现 {len(overdue_records)} 条逾期记录")
            
        except Exception as e:
            print(f"检查逾期图书时出错: {e}")
            db.session.rollback()

def run_scheduler():
    """运行定时任务"""
    # 每天凌晨1点执行
    schedule.every().day.at("01:00").do(check_overdue_books)
    
    # 开发环境：每分钟执行一次（用于测试）
    if os.environ.get('FLASK_ENV') == 'development':
        schedule.every(1).minutes.do(check_overdue_books)
    
    print("定时任务启动...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    run_scheduler()