# check_categories.py
from app import create_app
from app import db
from app.models import Category

# 创建Flask应用实例
app = create_app()

# 在应用上下文中操作
with app.app_context():
    print("=== 分类表详细数据 ===")
    categories = Category.query.all()
    
    for cat in categories:
        print(f"id: {cat.id}, name: {cat.name}, parent_id: {cat.parent_id}, description: {cat.description}")
    
    print("\n=== 分类名称统计 ===")
    from collections import Counter
    category_names = [cat.name for cat in categories]
    name_counts = Counter(category_names)
    
    for name, count in name_counts.items():
        if count > 1:
            print(f"分类 '{name}' 重复了 {count} 次")
    
    print("\n=== 建议删除的重复分类 ===")
    # 找出需要保留的分类（每个名称保留一个）
    categories_to_keep = []
    categories_to_delete = []
    
    seen_names = set()
    for cat in categories:
        if cat.name not in seen_names:
            categories_to_keep.append(cat)
            seen_names.add(cat.name)
        else:
            categories_to_delete.append(cat)
    
    print(f"需要保留: {len(categories_to_keep)} 个分类")
    print(f"需要删除: {len(categories_to_delete)} 个重复分类")
    
    for cat in categories_to_delete:
        print(f"- id: {cat.id}, name: {cat.name} (重复)")
