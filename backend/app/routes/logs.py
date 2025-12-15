from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..middleware.auth import admin_required
import os
from pathlib import Path
import logging

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required
def get_logs():
    """获取系统日志（管理员权限）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        log_level = request.args.get('level')
        
        # 日志文件路径
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_file = log_dir / 'app.log'
        
        if not log_file.exists():
            return jsonify({
                'message': '日志文件不存在',
                'logs': [],
                'total': 0
            }), 200
        
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 筛选日志级别
        filtered_lines = []
        for line in lines:
            if log_level:
                if log_level.upper() in line:
                    filtered_lines.append(line.strip())
            else:
                filtered_lines.append(line.strip())
        
        # 分页
        total = len(filtered_lines)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_logs = filtered_lines[::-1][start:end]  # 倒序显示，最新的日志在前
        
        return jsonify({
            'logs': paginated_logs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@logs_bp.route('/logs', methods=['DELETE'])
@jwt_required()
@admin_required
def clear_logs():
    """清空系统日志（管理员权限）"""
    try:
        # 日志文件路径
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_file = log_dir / 'app.log'
        
        if log_file.exists():
            # 清空日志文件
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('')
        
        return jsonify({'message': '日志已清空'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
