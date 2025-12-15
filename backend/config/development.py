import os

class DevelopmentConfig:
    """开发环境配置"""
    
    # 基础配置
    DEBUG = True
    TESTING = False
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///../database/library.db')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # 日志配置
    LOG_LEVEL = 'DEBUG'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../uploads')
    
    # 邮件配置（可选）
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')