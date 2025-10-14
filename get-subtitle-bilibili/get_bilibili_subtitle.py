"""
B站字幕下载脚本
使用飞鱼视频下载助手的API通过无头浏览器获取字幕
"""

import asyncio
import json
import argparse
import sys
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 解决 Windows 控制台中文乱码问题
if sys.platform == 'win32':
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 >nul 2>&1')
    # 重新配置 stdout 和 stderr 的编码
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')


def parse_srt_to_text(srt_content: str) -> str:
    """
    将 SRT 格式字幕转换为纯文本（去除序号和时间戳）
    
    Args:
        srt_content: SRT 格式的字幕内容
    
    Returns:
        纯文本字幕，每行一句
    """
    if not srt_content:
        return ""
    
    lines = srt_content.strip().split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        # 跳过序号（纯数字）
        if line.isdigit():
            continue
        # 跳过时间戳行（包含 -->）
        if '-->' in line:
            continue
        # 这是字幕文本内容
        text_lines.append(line)
    
    return '\n'.join(text_lines)


async def get_bilibili_subtitle(video_url: str, headless: bool = True, text_only: bool = True):
    """
    通过无头浏览器获取B站视频字幕
    
    Args:
        video_url: B站视频链接
        headless: 是否使用无头模式
        text_only: 是否只返回纯文本（去除时间戳），默认为 True
    
    Returns:
        API响应数据（字典格式）
    """
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 用于存储API响应
        api_response = None
        
        # 监听API请求
        async def handle_response(response):
            nonlocal api_response
            if "subtitleExtract" in response.url:
                try:
                    api_response = await response.json()
                    print(f"✓ 接收到API响应", file=sys.stderr)
                except Exception as e:
                    print(f"✗ 解析响应失败: {e}", file=sys.stderr)
        
        page.on("response", handle_response)
        
        try:
            print(f"正在访问网页...", file=sys.stderr)
            # 访问目标网页
            await page.goto("https://www.feiyudo.com/caption/subtitle/bilibili", 
                          wait_until="networkidle", 
                          timeout=30000)
            
            print(f"正在输入视频链接: {video_url}", file=sys.stderr)
            # 找到输入框并输入视频链接
            # 使用更通用的选择器
            input_selector = 'input[placeholder*="请将链接粘贴到这里"]'
            await page.wait_for_selector(input_selector, timeout=10000)
            await page.fill(input_selector, video_url)
            
            print(f"正在点击提取按钮...", file=sys.stderr)
            # 找到提取按钮并点击
            button_selector = 'button.el-button--primary:has-text("提取")'
            await page.click(button_selector)
            
            print(f"等待字幕提取...", file=sys.stderr)
            # 等待API响应（最多等待30秒）
            wait_time = 0
            max_wait = 30
            while api_response is None and wait_time < max_wait:
                await asyncio.sleep(0.5)
                wait_time += 0.5
            
            if api_response is None:
                print("✗ 等待超时，未收到API响应", file=sys.stderr)
                return None
            
            # 检查响应状态
            if api_response.get("code") != 200:
                print(f"✗ API返回错误: {api_response.get('message', '未知错误')}", file=sys.stderr)
                return None
            
            # 返回API响应数据
            data = api_response.get("data", {})
            subtitle_count = len(data.get('subtitleItemVoList', []))
            
            # 如果需要纯文本模式，处理字幕内容
            if text_only:
                subtitle_list = data.get('subtitleItemVoList', [])
                for subtitle_item in subtitle_list:
                    if 'content' in subtitle_item:
                        # 将 SRT 格式转换为纯文本
                        original_content = subtitle_item['content']
                        text_content = parse_srt_to_text(original_content)
                        subtitle_item['content'] = text_content
                        # 添加原始内容字段（可选）
                        subtitle_item['content_with_timestamp'] = original_content
            
            print(f"✓ 字幕提取成功", file=sys.stderr)
            print(f"  视频ID: {data.get('vid')}", file=sys.stderr)
            print(f"  标题: {data.get('title')}", file=sys.stderr)
            print(f"  状态: {data.get('status')}", file=sys.stderr)
            print(f"  字幕数量: {subtitle_count}", file=sys.stderr)
            print(f"  格式: {'纯文本' if text_only else '完整SRT'}", file=sys.stderr)
            
            return api_response
            
        except PlaywrightTimeoutError as e:
            print(f"✗ 操作超时: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"✗ 发生错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return None
        finally:
            await browser.close()


async def main():
    parser = argparse.ArgumentParser(
        description="获取B站视频字幕（输出JSON到stdout）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python get_bilibili_subtitle.py "https://www.bilibili.com/video/BV1DdDAYfEWQ"
  python get_bilibili_subtitle.py "BV1DdDAYfEWQ"
  python get_bilibili_subtitle.py "BV1DdDAYfEWQ" --no-headless

输出说明:
  - 所有日志信息输出到stderr
  - JSON结果输出到stdout（方便n8n等工具解析）
        """
    )
    
    parser.add_argument(
        "video_url",
        help="B站视频链接或BV号"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="显示浏览器窗口（调试用）"
    )
    parser.add_argument(
        "--keep-timestamp",
        action="store_true",
        help="保留时间戳（默认只返回纯文本）"
    )
    
    args = parser.parse_args()
    
    # 如果只提供了BV号，构建完整URL
    video_url = args.video_url
    if video_url.startswith("BV"):
        video_url = f"https://www.bilibili.com/video/{video_url}"
    
    print(f"B站字幕提取工具", file=sys.stderr)
    print(f"视频链接: {video_url}", file=sys.stderr)
    print("", file=sys.stderr)
    
    result = await get_bilibili_subtitle(
        video_url=video_url,
        headless=not args.no_headless,
        text_only=not args.keep_timestamp
    )
    
    if result:
        # 将JSON结果输出到stdout（方便n8n解析）
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("", file=sys.stderr)
        print("✓ 任务完成！", file=sys.stderr)
    else:
        print("", file=sys.stderr)
        print("✗ 任务失败", file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())

