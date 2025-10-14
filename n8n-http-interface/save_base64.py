"""
Base64 文件保存模块
提供核心功能，可被 CLI 和 HTTP API 调用
"""

import base64
from pathlib import Path
from typing import Tuple, Optional


# 文件类型魔术字节签名
FILE_SIGNATURES = {
    # 图片格式
    b'\xFF\xD8\xFF': ('jpg', 'image/jpeg'),
    b'\x89PNG\r\n\x1a\n': ('png', 'image/png'),
    b'GIF87a': ('gif', 'image/gif'),
    b'GIF89a': ('gif', 'image/gif'),
    b'RIFF': ('webp', 'image/webp'),  # 需要进一步检查
    b'BM': ('bmp', 'image/bmp'),
    b'\x00\x00\x01\x00': ('ico', 'image/x-icon'),
    
    # 音频格式
    b'ID3': ('mp3', 'audio/mpeg'),
    b'\xFF\xFB': ('mp3', 'audio/mpeg'),
    b'\xFF\xF3': ('mp3', 'audio/mpeg'),
    b'\xFF\xF2': ('mp3', 'audio/mpeg'),
    b'ftyp': ('mp4', 'audio/mp4'),  # MP4音频容器
    b'RIFF': ('wav', 'audio/wav'),  # 需要进一步检查
    b'OggS': ('ogg', 'audio/ogg'),
    b'fLaC': ('flac', 'audio/flac'),
    
    # 视频格式
    b'\x00\x00\x00\x18ftypmp4': ('mp4', 'video/mp4'),
    b'\x00\x00\x00\x1Cftypmp4': ('mp4', 'video/mp4'),
    b'\x1AE\xDF\xA3': ('webm', 'video/webm'),
    b'FLV': ('flv', 'video/x-flv'),
    
    # 文档格式
    b'%PDF': ('pdf', 'application/pdf'),
    b'PK\x03\x04': ('zip', 'application/zip'),
    
    # 文本格式
    b'{': ('json', 'application/json'),
    b'<?xml': ('xml', 'application/xml'),
}


def detect_file_type(data: bytes) -> Tuple[str, str]:
    """
    通过魔术字节检测文件类型
    
    Args:
        data: 文件的二进制数据
    
    Returns:
        (扩展名, MIME类型)
    """
    # 检查文件签名
    for signature, (ext, mime) in FILE_SIGNATURES.items():
        if data.startswith(signature):
            # 特殊处理 RIFF 格式（WAV 和 WEBP）
            if signature == b'RIFF' and len(data) > 12:
                if data[8:12] == b'WAVE':
                    return ('wav', 'audio/wav')
                elif data[8:12] == b'WEBP':
                    return ('webp', 'image/webp')
            return (ext, mime)
    
    # 尝试检测文本格式
    try:
        text = data.decode('utf-8')
        if text.strip().startswith('{') or text.strip().startswith('['):
            return ('json', 'application/json')
        elif text.strip().startswith('<?xml'):
            return ('xml', 'application/xml')
        elif text.strip().startswith('<!DOCTYPE html') or '<html' in text.lower():
            return ('html', 'text/html')
        else:
            return ('txt', 'text/plain')
    except:
        pass
    
    # 默认为二进制文件
    return ('bin', 'application/octet-stream')


def save_base64_file_core(
    base64_data: str,
    output_path: str,
    auto_extension: bool = True,
    force_extension: Optional[str] = None
) -> dict:
    """
    保存 Base64 数据到文件（核心函数）
    
    Args:
        base64_data: Base64 编码的数据
        output_path: 输出文件路径
        auto_extension: 是否自动添加文件扩展名
        force_extension: 强制使用的扩展名
    
    Returns:
        包含操作结果的字典
    """
    try:
        # 移除可能的 data URL 前缀
        if ',' in base64_data and base64_data.startswith('data:'):
            base64_data = base64_data.split(',', 1)[1]
        
        # 解码 Base64
        file_data = base64.b64decode(base64_data)
        
        # 检测文件类型
        detected_ext, mime_type = detect_file_type(file_data)
        
        # 处理输出路径
        output_path = Path(output_path)
        
        # 确定最终的文件扩展名
        final_extension = None
        if force_extension:
            final_extension = force_extension.lstrip('.')
        elif auto_extension and not output_path.suffix:
            final_extension = detected_ext
        
        # 如果需要添加扩展名
        if final_extension:
            output_path = output_path.with_suffix(f'.{final_extension}')
        
        # 创建目标目录（如果不存在）
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        file_size = len(file_data)
        
        return {
            "success": True,
            "file_path": str(output_path.absolute()),
            "file_size": file_size,
            "file_type": detected_ext,
            "mime_type": mime_type,
            "message": f"文件保存成功: {output_path.absolute()}"
        }
        
    except base64.binascii.Error as e:
        return {
            "success": False,
            "error": f"Base64 解码失败: {e}"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

