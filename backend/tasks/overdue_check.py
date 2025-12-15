import os
import schedule
import time
from datetime import datetime, timedelta
from app import create_app
from app.models import db, BorrowRecord, Notification

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
                
                # 创建逾期通知
                notification = Notification(
                    user_id=record.user_id,
                    title='图书逾期提醒',
                    content=f'您借阅的图书《{record.book.title}》已逾期 {days_overdue} 天，逾期费用为 {record.fine_amount} 元，请尽快归还。',
                    notification_type='overdue_reminder'
                )
                db.session.add(notification)
            
            db.session.commit()
            print(f"{datetime.now()}: 检查完成，发现 {len(overdue_records)} 条逾期记录")
            
        except Exception as e:
            print(f"检查逾期图书时出错: {e}")
            db.session.rollback()

def send_return_reminders():
    """发送到期提醒（提前3天）"""
    app = create_app()
    
    with app.app_context():
        try:
            # 查找3天后到期的借阅记录
            three_days_later = datetime.utcnow() + timedelta(days=3)
            due_records = BorrowRecord.query.filter(
                BorrowRecord.status == 'borrowed',
                BorrowRecord.due_date <= three_days_later,
                BorrowRecord.due_date > datetime.utcnow()
            ).all()
            
            for record in due_records:
                # 检查是否已经发送过提醒
                existing_notification = Notification.query.filter(
                    Notification.user_id == record.user_id,
                    Notification.notification_type == 'return_reminder',
                    Notification.content.contains(record.book.title)
                ).order_by(Notification.created_at.desc()).first()
                
                # 如果没有发送过或者超过24小时，则发送新提醒
                if not existing_notification or (
                    datetime.utcnow() - existing_notification.created_at > timedelta(hours=24)
                ):
                    # 计算剩余天数
                    days_remaining = (record.due_date - datetime.utcnow()).days + 1
                    
                    # 创建到期提醒
                    notification = Notification(
                        user_id=record.user_id,
                        title='图书到期提醒',
                        content=f'您借阅的图书《{record.book.title}》将在 {days_remaining} 天后到期，请提前安排归还。',
                        notification_type='return_reminder'
                    )
                    db.session.add(notification)
            
            db.session.commit()
            print(f"{datetime.now()}: 发送到期提醒完成，处理 {len(due_records)} 条记录")
            
        except Exception as e:
            print(f"发送到期提醒时出错: {e}")
            db.session.rollback()

def run_scheduler():
    """运行定时任务"""
    # 每天凌晨1点执行逾期检查
    schedule.every().day.at("01:00").do(check_overdue_books)
    # 每天上午9点发送到期提醒
    schedule.every().day.at("09:00").do(send_return_reminders)
    
    # 开发环境：每分钟执行一次（用于测试）
    if os.environ.get('FLASK_ENV') == 'development':
        schedule.every(1).minutes.do(check_overdue_books)
        schedule.every(1).minutes.do(send_return_reminders)
    
    print("定时任务启动...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    run_scheduler()