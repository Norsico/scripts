"""
n8n HTTP Tools - 统一的 HTTP API 服务
为 n8n 工作流提供便捷的 HTTP 接口
"""

import json
import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入工具模块
from save_base64 import save_base64_file_core

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 服务配置
PORT = 6666
HOST = '127.0.0.1'


@app.route('/', methods=['GET'])
def index():
    """API 文档"""
    return jsonify({
        "name": "n8n HTTP Tools",
        "version": "1.0.0",
        "description": "为 n8n 工作流提供的 HTTP API 工具集",
        "endpoints": [
            {
                "path": "/save-base64",
                "method": "POST",
                "description": "保存 Base64 数据到本地文件，自动识别文件类型",
                "body": {
                    "data": "Base64 编码的数据（必需）",
                    "path": "输出文件路径（必需）",
                    "force_ext": "强制使用的扩展名（可选）",
                    "auto_extension": "是否自动添加扩展名，默认 true（可选）"
                },
                "example": {
                    "data": "iVBORw0KGgo...",
                    "path": "output/image",
                    "auto_extension": True
                }
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "健康检查"
            }
        ],
        "server": {
            "host": HOST,
            "port": PORT
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "message": "Service is running"
    })


@app.route('/save-base64', methods=['POST'])
def api_save_base64():
    """
    保存 Base64 数据到本地文件
    
    POST Body:
    {
        "data": "base64_encoded_data",
        "path": "output/file/path",
        "force_ext": "jpg",  // 可选
        "auto_extension": true  // 可选，默认 true
    }
    """
    try:
        # 获取请求数据
        body = request.get_json()
        
        if not body:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        # 验证必需参数
        if 'data' not in body:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: data"
            }), 400
        
        if 'path' not in body:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: path"
            }), 400
        
        base64_data = body['data']
        output_path = body['path']
        force_ext = body.get('force_ext')
        auto_extension = body.get('auto_extension', True)
        
        # 调用核心函数
        result = save_base64_file_core(
            base64_data=base64_data,
            output_path=output_path,
            auto_extension=auto_extension,
            force_extension=force_ext
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "success": False,
        "error": "API 端点不存在",
        "message": "请访问 / 查看可用的 API 端点"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        "success": False,
        "error": "服务器内部错误",
        "message": str(error)
    }), 500


def main():
    """启动服务器"""
    print("=" * 60)
    print("n8n HTTP Tools - HTTP API 服务")
    print("=" * 60)
    print(f"服务地址: http://{HOST}:{PORT}")
    print(f"API 文档: http://{HOST}:{PORT}/")
    print(f"健康检查: http://{HOST}:{PORT}/health")
    print("=" * 60)
    print("\n可用 API:")
    print(f"  POST http://{HOST}:{PORT}/save-base64")
    print("    - 保存 Base64 数据到本地文件")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    # 启动服务器
    try:
        app.run(
            host=HOST,
            port=PORT,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

