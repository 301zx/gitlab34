# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 先创建扩展实例
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # 配置日志记录
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'app.log'
    
    # 设置日志级别
    app.logger.setLevel(logging.INFO)
    
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # 添加日志处理器
    app.logger.addHandler(file_handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # 记录应用启动日志
    app.logger.info('图书管理系统应用初始化')
    
    # 配置
    if config_class:
        app.config.from_object(config_class)
    else:
        # 默认配置
        # 配置数据库路径
        backend_dir = Path(__file__).parent
        project_root = backend_dir.parent
        database_dir = project_root / 'database'
        database_dir.mkdir(exist_ok=True)
        database_path = database_dir / 'library.db'
        
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)    
    
    # 注册错误处理器
    from app.middleware.error_handler import register_error_handlers
    register_error_handlers(app)
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.books import books_bp
    from app.routes.users import users_bp
    from app.routes.borrows import borrows_bp
    from app.routes.categories import categories_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(borrows_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')
    
    return app