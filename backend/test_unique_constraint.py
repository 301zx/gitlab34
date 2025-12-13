# test_unique_constraint.py
"""
测试Category模型的name字段唯一约束是否生效
"""
from app import create_app
from app import db
from app.models import Category

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 测试Category模型唯一约束 ===")
    
    # 尝试创建一个重复的分类
    print("\n1. 尝试创建一个与现有分类同名的分类...")
    try:
        # 创建一个与现有分类同名的分类
        new_category = Category(
            name="文学",
            description="测试重复分类"
        )
        db.session.add(new_category)
        db.session.commit()
        print("❌ 错误：可以创建重复分类！")
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        print(f"✅ 成功：无法创建重复分类")
        print(f"   错误信息：{type(e).__name__}: {e}")
    
    # 尝试创建一个新的、不重复的分类
    print("\n2. 尝试创建一个新的、不重复的分类...")
    try:
        new_category = Category(
            name="经济",
            description="经济学相关图书"
        )
        db.session.add(new_category)
        db.session.commit()
        print(f"✅ 成功：可以创建新的分类")
        print(f"   创建的分类：id={new_category.id}, name={new_category.name}")
        
        # 清理测试数据
        db.session.delete(new_category)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ 错误：无法创建新分类")
        print(f"   错误信息：{type(e).__name__}: {e}")
    
    print("\n=== 测试完成 ===")
