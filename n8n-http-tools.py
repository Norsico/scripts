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

# 解决 Windows 控制台中文乱码问题
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# 添加模块目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'n8n-http-interface'))

# 导入工具模块
from save_base64 import save_base64_file_core
from get_bilibili_subtitle import get_bilibili_subtitle_core
from tts_synthesis import tts_synthesis_core
from generate_image_gemini import generate_image_gemini_core

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
                "description": "保存 Base64 数据到本地文件，自动识别文件类型"
            },
            {
                "path": "/get-bilibili-subtitle",
                "method": "POST",
                "description": "获取B站视频字幕"
            },
            {
                "path": "/tts-synthesis",
                "method": "POST",
                "description": "TTS 语音合成，批量生成音频文件"
            },
            {
                "path": "/generate-image-gemini",
                "method": "POST",
                "description": "使用 Google Gemini 生成图片（Nano Banana / gemini-2.5-flash-image）"
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
        "force_ext": "jpg",  // 可选：强制指定文件扩展名
        "auto_extension": true,  // 可选：是否自动添加扩展名，默认 true
        "mime_type": "image/jpeg"  // 可选：指定 MIME 类型来确定文件扩展名
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
        mime_type = body.get('mime_type')
        
        # 调用核心函数
        result = save_base64_file_core(
            base64_data=base64_data,
            output_path=output_path,
            auto_extension=auto_extension,
            force_extension=force_ext,
            mime_type=mime_type
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


@app.route('/get-bilibili-subtitle', methods=['POST'])
def api_get_bilibili_subtitle():
    """
    获取B站视频字幕
    
    POST Body:
    {
        "url": "https://www.bilibili.com/video/BV1DdDAYfEWQ",
        "text_only": true  // 可选，默认 true（去除时间戳）
    }
    """
    try:
        body = request.get_json()
        
        if not body:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        if 'url' not in body:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: url"
            }), 400
        
        video_url = body['url']
        text_only = body.get('text_only', True)
        
        # 调用异步函数
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            get_bilibili_subtitle_core(video_url, text_only)
        )
        loop.close()
        
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


@app.route('/tts-synthesis', methods=['POST'])
def api_tts_synthesis():
    """
    TTS 语音合成
    
    POST Body:
    {
        "text": {
            "自述文案": ["文案1", "文案2", ...]
        },
        "prompt_audio_url": "https://example.com/audio.wav",
        "save_path": "output/path",
        "api_key": "your_api_key"
    }
    """
    try:
        body = request.get_json()
        
        if not body:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        # 验证必需参数
        required_params = ['text', 'prompt_audio_url', 'save_path', 'api_key']
        for param in required_params:
            if param not in body:
                return jsonify({
                    "success": False,
                    "error": f"缺少必需参数: {param}"
                }), 400
        
        text_dict = body['text']
        prompt_audio_url = body['prompt_audio_url']
        save_path = body['save_path']
        api_key = body['api_key']
        
        # 调用核心函数
        result = tts_synthesis_core(
            text_dict=text_dict,
            prompt_audio_url=prompt_audio_url,
            save_path=save_path,
            api_key=api_key
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


@app.route('/generate-image-gemini', methods=['POST'])
def api_generate_image_gemini():
    """
    使用 Google Gemini 生成图片
    
    POST Body:
    {
        "prompt": "生成图像的提示词",
        "save_path": "output/path",
        "aspect_ratio": "16:9",  // 可选：宽高比
        "added_prompt": "additional refinement prompt"  // 可选：附加提示词（两步生成）
    }
    """
    try:
        body = request.get_json()
        
        if not body:
            return jsonify({
                "success": False,
                "error": "请求体不能为空"
            }), 400
        
        # 验证必需参数
        if 'prompt' not in body:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: prompt"
            }), 400
        
        if 'save_path' not in body:
            return jsonify({
                "success": False,
                "error": "缺少必需参数: save_path"
            }), 400
        
        prompt = body['prompt']
        save_path = body['save_path']
        aspect_ratio = body.get('aspect_ratio')
        added_prompt = body.get('added_prompt')
        
        # 调用核心函数
        result = generate_image_gemini_core(
            prompt=prompt,
            save_path=save_path,
            aspect_ratio=aspect_ratio,
            added_prompt=added_prompt
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
    print(f"  POST http://{HOST}:{PORT}/get-bilibili-subtitle")
    print("    - 获取B站视频字幕")
    print(f"  POST http://{HOST}:{PORT}/tts-synthesis")
    print("    - TTS 语音合成，批量生成音频文件")
    print(f"  POST http://{HOST}:{PORT}/generate-image-gemini")
    print("    - 使用 Google Gemini 生成图片（Nano Banana）")
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

