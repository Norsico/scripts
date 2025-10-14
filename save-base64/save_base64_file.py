"""
Base64文件保存工具（命令行版本）
自动识别文件类型并保存到本地
"""

import argparse
import sys
import os
import json
from pathlib import Path

# 解决 Windows 控制台中文乱码问题
if sys.platform == 'win32':
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 >nul 2>&1')
    # 重新配置 stdout 和 stderr 的编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

# 导入核心功能模块
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
from save_base64 import save_base64_file_core




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
    
    # 打印进度信息
    if ',' in base64_data and base64_data.startswith('data:'):
        print("检测到 Data URL 格式，正在提取...", file=sys.stderr)
    
    print("正在解码 Base64 数据...", file=sys.stderr)
    
    # 保存文件
    result = save_base64_file_core(
        base64_data=base64_data,
        output_path=args.output_path,
        auto_extension=not args.no_auto_ext,
        force_extension=args.force_ext
    )
    
    # 打印结果信息
    if result.get("success"):
        print(f"检测到文件类型: {result['file_type']} ({result['mime_type']})", file=sys.stderr)
        print(f"正在保存文件到: {result['file_path']}", file=sys.stderr)
        print(f"✓ 文件保存成功", file=sys.stderr)
        print(f"  路径: {result['file_path']}", file=sys.stderr)
        print(f"  大小: {result['file_size']:,} 字节 ({result['file_size'] / 1024:.2f} KB)", file=sys.stderr)
        print(f"  类型: {result['mime_type']}", file=sys.stderr)
    else:
        print(f"✗ {result.get('error', '未知错误')}", file=sys.stderr)
    
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

