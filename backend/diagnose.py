import os
import sys
import importlib.util

# 1. 检测init_db.py文件是否存在
def check_init_db_exists():
    file_path = os.path.join(os.getcwd(), "init_db.py")
    if os.path.exists(file_path):
        print("✅ init_db.py 文件存在")
        return True
    else:
        print("❌ init_db.py 文件不存在，当前路径：", os.getcwd())
        return False

# 2. 检测app模块是否存在
def check_app_module():
    app_path = os.path.join(os.getcwd(), "app")
    init_file = os.path.join(app_path, "__init__.py")
    if os.path.exists(app_path) and os.path.isdir(app_path):
        print("✅ app 模块文件夹存在")
        if os.path.exists(init_file):
            print("✅ app/__init__.py 文件存在")
            return True
        else:
            print("❌ app/__init__.py 文件缺失（需创建空文件）")
            return False
    else:
        print("❌ app 模块文件夹不存在")
        return False

# 3. 检测create_app和db是否可导入
def check_import_objects():
    try:
        # 将当前目录加入Python搜索路径
        sys.path.insert(0, os.getcwd())
        from app import create_app, db
        print("✅ 成功导入 create_app 和 db")
        return True
    except ImportError as e:
        if "cannot import name 'create_app'" in str(e):
            print("❌ app模块中未定义 create_app 函数")
        elif "cannot import name 'db'" in str(e):
            print("❌ app模块中未定义 db 对象")
        else:
            print("❌ 导入失败：", str(e))
        return False
    except Exception as e:
        print("❌ 导入时发生未知错误：", str(e))
        return False

# 主诊断流程
if __name__ == "__main__":
    print("=== 开始诊断 library-management-system 项目问题 ===")
    # 检查文件存在性
    if not check_init_db_exists():
        sys.exit(1)
    # 检查app模块结构
    if not check_app_module():
        sys.exit(1)
    # 检查导入是否正常
    check_import_objects()
    print("=== 诊断结束 ===")