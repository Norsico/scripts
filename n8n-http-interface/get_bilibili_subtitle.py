"""
B站字幕提取模块
提供核心功能，供 HTTP API 调用
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


def parse_srt_to_text(srt_content: str) -> str:
    """将 SRT 格式字幕转换为纯文本（去除序号和时间戳）"""
    if not srt_content:
        return ""
    
    lines = srt_content.strip().split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or '-->' in line:
            continue
        text_lines.append(line)
    
    return '\n'.join(text_lines)


async def get_bilibili_subtitle_core(video_url: str, text_only: bool = True) -> dict:
    """
    获取B站视频字幕（核心功能）
    
    Args:
        video_url: B站视频链接或BV号
        text_only: 是否只返回纯文本（去除时间戳）
    
    Returns:
        包含字幕数据的字典
    """
    # 如果只提供了BV号，构建完整URL
    if video_url.startswith("BV"):
        video_url = f"https://www.bilibili.com/video/{video_url}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        api_response = None
        
        async def handle_response(response):
            nonlocal api_response
            if "subtitleExtract" in response.url:
                try:
                    api_response = await response.json()
                except:
                    pass
        
        page.on("response", handle_response)
        
        try:
            await page.goto(
                "https://www.feiyudo.com/caption/subtitle/bilibili",
                wait_until="networkidle",
                timeout=30000
            )
            
            input_selector = 'input[placeholder*="请将链接粘贴到这里"]'
            await page.wait_for_selector(input_selector, timeout=10000)
            await page.fill(input_selector, video_url)
            
            button_selector = 'button.el-button--primary:has-text("提取")'
            await page.click(button_selector)
            
            # 等待API响应
            wait_time = 0
            max_wait = 30
            while api_response is None and wait_time < max_wait:
                await asyncio.sleep(0.5)
                wait_time += 0.5
            
            if api_response is None:
                return {
                    "success": False,
                    "error": "等待超时，未收到API响应"
                }
            
            if api_response.get("code") != 200:
                return {
                    "success": False,
                    "error": api_response.get('message', '未知错误')
                }
            
            # 处理字幕内容
            data = api_response.get("data", {})
            if text_only:
                subtitle_list = data.get('subtitleItemVoList', [])
                for subtitle_item in subtitle_list:
                    if 'content' in subtitle_item:
                        original_content = subtitle_item['content']
                        text_content = parse_srt_to_text(original_content)
                        subtitle_item['content'] = text_content
                        subtitle_item['content_with_timestamp'] = original_content
            
            return {
                "success": True,
                "data": api_response
            }
            
        except PlaywrightTimeoutError:
            return {
                "success": False,
                "error": "操作超时"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await browser.close()
