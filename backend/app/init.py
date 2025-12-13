from flask import Flask
from flask_jwt_extended import JWTExtended
from flask_cors import CORS
from .models import db, bcrypt
from .middleware.error_handler import register_error_handlers
import os

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///../database/library.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key'),
        JWT_ACCESS_TOKEN_EXPIRES=86400  # 24小时过期
    )
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    jwt = JWTExtended(app)
    CORS(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.books import books_bp
    from .routes.users import users_bp
    from .routes.borrows import borrows_bp
    from .routes.categories import categories_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(borrows_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员账户
        from .models import User, Category
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@library.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # 创建默认分类
            categories = [
                Category(name="文学", description="小说、散文、诗歌等文学作品"),
                Category(name="科技", description="计算机、工程、数学等科技类图书"),
                Category(name="历史", description="历史研究、传记等"),
                Category(name="艺术", description="绘画、音乐、设计等艺术类图书"),
                Category(name="教育", description="教材、参考书等教育类图书")
            ]
            
            for category in categories:
                if not Category.query.filter_by(name=category.name).first():
                    db.session.add(category)
            
            db.session.commit()
            print("默认数据初始化完成！")
            print("管理员账号: admin / admin123")
    
    return app