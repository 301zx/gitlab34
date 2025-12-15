# cleanup_categories.py
"""
清理分类表中的重复记录
保留每个分类名称的第一个记录（ID最小的）
"""
from app import create_app
from app import db
from app.models import Category
from collections import defaultdict

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 开始清理重复分类记录 ===")
    
    # 获取所有分类记录
    all_categories = Category.query.all()
    print(f"当前分类总数: {len(all_categories)}")
    
    # 按分类名称分组
    categories_by_name = defaultdict(list)
    for category in all_categories:
        categories_by_name[category.name].append(category)
    
    # 统计重复情况
    duplicate_count = 0
    for name, categories in categories_by_name.items():
        if len(categories) > 1:
            print(f"分类 '{name}' 有 {len(categories)} 条重复记录")
            duplicate_count += len(categories) - 1
    
    print(f"\n需要删除的重复记录总数: {duplicate_count}")
    
    # 执行清理操作
    deleted_count = 0
    for name, categories in categories_by_name.items():
        if len(categories) > 1:
            # 按ID排序，保留第一个（ID最小的）
            categories.sort(key=lambda x: x.id)
            
            # 保留第一个，删除其他
            keep_category = categories[0]
            delete_categories = categories[1:]
            
            print(f"\n保留分类: id={keep_category.id}, name={keep_category.name}")
            for cat in delete_categories:
                print(f"删除分类: id={cat.id}, name={cat.name}")
                db.session.delete(cat)
                deleted_count += 1
    
    # 提交更改
    db.session.commit()
    
    # 验证清理结果
    remaining_categories = Category.query.all()
    print(f"\n=== 清理完成 ===")
    print(f"删除的重复记录数: {deleted_count}")
    print(f"剩余分类总数: {len(remaining_categories)}")
    
    # 打印剩余分类
    print("\n剩余分类列表:")
    for category in remaining_categories:
        print(f"- id: {category.id}, name: {category.name}, description: {category.description}")
    
    # 再次检查是否还有重复
    remaining_names = [cat.name for cat in remaining_categories]
    from collections import Counter
    name_counts = Counter(remaining_names)
    duplicates_remaining = sum(1 for count in name_counts.values() if count > 1)
    
    if duplicates_remaining == 0:
        print("\n✅ 清理成功！没有剩余的重复分类记录")
    else:
        print(f"\n❌ 清理失败！仍有 {duplicates_remaining} 个分类存在重复")
