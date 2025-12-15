import os

# 服务器配置
bind = "0.0.0.0:5000"
workers = int(os.environ.get('GUNICORN_WORKERS', 4))
worker_class = "sync"
worker_connections = 1000
timeout = 30
max_requests = 1000
max_requests_jitter = 100

# 日志配置
accesslog = "-"  # 标准输出
errorlog = "-"   # 标准错误输出
loglevel = "info"

# 进程名称
proc_name = "library_management_system"

# 开发环境配置
if os.environ.get('FLASK_ENV') == 'development':
    reload = True
    max_requests = 0  # 开发环境不限制请求数