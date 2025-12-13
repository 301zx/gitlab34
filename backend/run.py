import os
from app import create_app
from config.init import config

# 获取环境变量，默认为开发环境
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    # 获取端口配置，默认为5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"启动图书管理系统 - 环境: {env}")
    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/api/docs")
    
    # 开发环境配置
    if env == 'development':
        app.run(debug=True, host=host, port=port)
    else:
        app.run(host=host, port=port)