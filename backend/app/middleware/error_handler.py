from flask import jsonify
import logging
from datetime import datetime
import traceback

def handle_error(error):
    """统一错误处理"""
    error_id = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    
    # 记录错误日志
    logging.error(f"Error {error_id}: {str(error)}")
    logging.error(traceback.format_exc())
    
    # 根据错误类型返回不同的响应
    if hasattr(error, 'code'):
        status_code = error.code
    else:
        status_code = 500
    
    error_messages = {
        400: '请求参数错误',
        401: '未授权访问',
        403: '权限不足',
        404: '资源不存在',
        405: '方法不允许',
        500: '服务器内部错误'
    }
    
    message = error_messages.get(status_code, '未知错误')
    
    response = {
        'error': {
            'code': status_code,
            'message': message,
            'error_id': error_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    }
    
    # 开发环境返回详细错误信息
    if hasattr(error, 'description') and hasattr(error, 'code'):
        response['error']['details'] = error.description
    
    return jsonify(response), status_code

def register_error_handlers(app):
    """注册错误处理器"""
    app.errorhandler(400)(handle_error)
    app.errorhandler(401)(handle_error)
    app.errorhandler(403)(handle_error)
    app.errorhandler(404)(handle_error)
    app.errorhandler(405)(handle_error)
    app.errorhandler(500)(handle_error)
    
    # 处理所有未捕获的异常
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return handle_error(error)