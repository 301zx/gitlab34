import os

class ProductionConfig:
    """生产环境配置"""
    
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/app/uploads'
    
    # 安全配置
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')