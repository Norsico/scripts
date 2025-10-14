"""
Base64文件保存工具
自动识别文件类型并保存到本地
"""

import base64
import argparse
import sys
import os
import json
from pathlib import Path
from typing import Tuple, Optional

# 解决 Windows 控制台中文乱码问题
if sys.platform == 'win32':
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 >nul 2>&1')
    # 重新配置 stdout 和 stderr 的编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')


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
    b'PK\x03\x04': ('zip', 'application/zip'),  # 也可能是docx, xlsx等
    
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


def save_base64_file(
    base64_data: str,
    output_path: str,
    auto_extension: bool = True,
    force_extension: Optional[str] = None
) -> dict:
    """
    保存 Base64 数据到文件
    
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
            print("检测到 Data URL 格式，正在提取...", file=sys.stderr)
            base64_data = base64_data.split(',', 1)[1]
        
        # 解码 Base64
        print("正在解码 Base64 数据...", file=sys.stderr)
        file_data = base64.b64decode(base64_data)
        
        # 检测文件类型
        detected_ext, mime_type = detect_file_type(file_data)
        print(f"检测到文件类型: {detected_ext} ({mime_type})", file=sys.stderr)
        
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
        print(f"正在保存文件到: {output_path}", file=sys.stderr)
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        file_size = len(file_data)
        print(f"✓ 文件保存成功", file=sys.stderr)
        print(f"  路径: {output_path.absolute()}", file=sys.stderr)
        print(f"  大小: {file_size:,} 字节 ({file_size / 1024:.2f} KB)", file=sys.stderr)
        print(f"  类型: {mime_type}", file=sys.stderr)
        
        return {
            "success": True,
            "file_path": str(output_path.absolute()),
            "file_size": file_size,
            "file_type": detected_ext,
            "mime_type": mime_type
        }
        
    except base64.binascii.Error as e:
        error_msg = f"Base64 解码失败: {e}"
        print(f"✗ {error_msg}", file=sys.stderr)
        return {
            "success": False,
            "error": error_msg
        }
    except Exception as e:
        error_msg = f"保存文件失败: {e}"
        print(f"✗ {error_msg}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": error_msg
        }


def main():
    parser = argparse.ArgumentParser(
        description="保存 Base64 数据到本地文件（自动识别文件类型）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从命令行参数读取 Base64
  python save_base64_file.py "iVBORw0KGgo..." "output/image"
  
  # 从文件读取 Base64
  python save_base64_file.py --input base64.txt "output/image"
  
  # 从标准输入读取 Base64
  echo "iVBORw0KGgo..." | python save_base64_file.py --stdin "output/image"
  
  # 指定文件扩展名
  python save_base64_file.py "iVBORw0KGgo..." "output/image.png"
  
  # 强制使用特定扩展名
  python save_base64_file.py --force-ext jpg "base64data" "output/image"

输出说明:
  - 所有日志信息输出到 stderr
  - JSON 结果输出到 stdout（方便 n8n 等工具解析）
        """
    )
    
    parser.add_argument(
        "base64_data",
        nargs='?',
        help="Base64 编码的数据（或使用 --input 或 --stdin）"
    )
    parser.add_argument(
        "output_path",
        help="输出文件路径（可以不带扩展名，将自动识别）"
    )
    parser.add_argument(
        "--input", "-i",
        help="从文件读取 Base64 数据"
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="从标准输入读取 Base64 数据"
    )
    parser.add_argument(
        "--force-ext", "-e",
        help="强制使用指定的文件扩展名"
    )
    parser.add_argument(
        "--no-auto-ext",
        action="store_true",
        help="不自动添加文件扩展名"
    )
    
    args = parser.parse_args()
    
    # 获取 Base64 数据
    base64_data = None
    
    if args.stdin:
        print("从标准输入读取 Base64 数据...", file=sys.stderr)
        base64_data = sys.stdin.read().strip()
    elif args.input:
        print(f"从文件读取 Base64 数据: {args.input}", file=sys.stderr)
        with open(args.input, 'r', encoding='utf-8') as f:
            base64_data = f.read().strip()
    elif args.base64_data:
        base64_data = args.base64_data
    else:
        print("✗ 错误: 必须提供 Base64 数据（通过参数、--input 或 --stdin）", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    if not base64_data:
        print("✗ 错误: Base64 数据为空", file=sys.stderr)
        sys.exit(1)
    
    print("Base64 文件保存工具", file=sys.stderr)
    print(f"数据长度: {len(base64_data):,} 字符", file=sys.stderr)
    print(f"输出路径: {args.output_path}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # 保存文件
    result = save_base64_file(
        base64_data=base64_data,
        output_path=args.output_path,
        auto_extension=not args.no_auto_ext,
        force_extension=args.force_ext
    )
    
    # 输出 JSON 结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get("success"):
        print("", file=sys.stderr)
        print("✓ 任务完成！", file=sys.stderr)
        sys.exit(0)
    else:
        print("", file=sys.stderr)
        print("✗ 任务失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

