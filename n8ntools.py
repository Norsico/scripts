#!/usr/bin/env python3
"""
n8ntools - 统一的命令行工具集
支持多个子工具，便于扩展和维护
"""

import sys
import os
import importlib.util
from pathlib import Path

# 解决 Windows 控制台中文乱码问题
if sys.platform == 'win32':
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 >nul 2>&1')
    # 重新配置 stdout 和 stderr 的编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')


# 工具注册表
TOOLS = {
    'get-subtitle-bilibili': {
        'path': 'get-subtitle-bilibili/get_bilibili_subtitle.py',
        'description': '获取B站视频字幕',
        'main_function': 'main'
    },
    'save-base64': {
        'path': 'save-base64/save_base64_file.py',
        'description': '保存Base64数据到本地文件（自动识别类型）',
        'main_function': 'main'
    },
    # 在这里添加更多工具
    # 'tool-name': {
    #     'path': 'tool-folder/tool_script.py',
    #     'description': '工具描述',
    #     'main_function': 'main'
    # },
}


def print_help():
    """打印帮助信息"""
    print("n8ntools - 命令行工具集")
    print()
    print("使用方法:")
    print("  n8ntools <tool-name> [arguments...]")
    print()
    print("可用工具:")
    for tool_name, tool_info in TOOLS.items():
        print(f"  {tool_name:<25} {tool_info['description']}")
    print()
    print("示例:")
    print('  n8ntools get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"')
    print()
    print("获取特定工具的帮助:")
    print("  n8ntools <tool-name> --help")


def load_tool_module(tool_path):
    """动态加载工具模块"""
    script_dir = Path(__file__).parent
    full_path = script_dir / tool_path
    
    if not full_path.exists():
        print(f"错误: 工具脚本不存在: {full_path}", file=sys.stderr)
        return None
    
    # 动态加载模块
    spec = importlib.util.spec_from_file_location("tool_module", full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def main():
    # 如果没有参数或请求帮助
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        return 0
    
    tool_name = sys.argv[1]
    
    # 检查工具是否存在
    if tool_name not in TOOLS:
        print(f"错误: 未知的工具 '{tool_name}'", file=sys.stderr)
        print(f"运行 'n8ntools --help' 查看可用工具", file=sys.stderr)
        return 1
    
    tool_info = TOOLS[tool_name]
    
    # 加载工具模块
    module = load_tool_module(tool_info['path'])
    if module is None:
        return 1
    
    # 修改sys.argv，让子工具看起来像直接被调用
    # 从 ['n8ntools.py', 'get-subtitle-bilibili', 'arg1', 'arg2']
    # 变成 ['get_bilibili_subtitle.py', 'arg1', 'arg2']
    tool_script_name = Path(tool_info['path']).name
    sys.argv = [tool_script_name] + sys.argv[2:]
    
    # 调用工具的main函数
    main_function = getattr(module, tool_info['main_function'], None)
    if main_function is None:
        print(f"错误: 工具模块中没有找到 '{tool_info['main_function']}' 函数", file=sys.stderr)
        return 1
    
    try:
        # 如果是异步函数，需要特殊处理
        import asyncio
        import inspect
        
        if inspect.iscoroutinefunction(main_function):
            result = asyncio.run(main_function())
        else:
            result = main_function()
        
        return result if result is not None else 0
    except KeyboardInterrupt:
        print("\n操作已取消", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

