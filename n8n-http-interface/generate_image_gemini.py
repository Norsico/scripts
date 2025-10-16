"""
Google Gemini 图像生成模块
使用 Gemini 2.5 Flash Image 模型生成图片
"""

import base64
import requests
from pathlib import Path
from typing import Optional


def generate_image_gemini_core(
    prompt: str,
    save_path: str,
    aspect_ratio: Optional[str] = None,
    added_prompt: Optional[str] = None,
    base_url: str = "https://ai.xiangcao.de",
    model: str = "gemini-2.5-flash-image-preview",
    api_key: str = "sk-kMwO7Pqz0tcv0DtPIUjAFGlGA1IvEGMjOD3ObO7oFWiKuf6A"
) -> dict:
    """
    使用 Gemini 生成图片（核心函数）
    
    Args:
        prompt: 用于生成图像的提示词
        save_path: 图片保存路径
        aspect_ratio: 图片宽高比（可选），如 "16:9", "1:1", "9:16" 等
        added_prompt: 附加提示词（可选）。如果提供，将先用 prompt 生成图片，再用生成的图片+added_prompt 生成最终图片
        base_url: API 基础地址
        api_key: API 密钥
    
    Returns:
        包含操作结果的字典
    """
    try:
        # 构建完整的 API 端点
        endpoint = f"{base_url.rstrip('/')}/v1beta/models/{model}:generateContent"
        
        # 设置请求头
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # ========== 第一步：使用 prompt 生成初始图片 ==========
        request_body_step1 = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }]
        }
        
        # 如果指定了宽高比，添加到配置中
        if aspect_ratio:
            request_body_step1["generationConfig"] = {
                "imageConfig": {
                    "aspectRatio": aspect_ratio
                }
            }
        
        # 发送第一次请求
        response_step1 = requests.post(
            endpoint,
            json=request_body_step1,
            headers=headers,
            timeout=120
        )
        
        # 检查第一次响应状态
        if response_step1.status_code != 200:
            return {
                "success": False,
                "error": f"第一步 API 请求失败: HTTP {response_step1.status_code}",
                "details": response_step1.text
            }
        
        # 解析第一次响应
        response_data_step1 = response_step1.json()
        
        # 提取第一次生成的图像数据
        if "candidates" not in response_data_step1 or len(response_data_step1["candidates"]) == 0:
            return {
                "success": False,
                "error": "第一步：API 响应中没有找到生成的图像",
                "response": response_data_step1
            }
        
        candidate_step1 = response_data_step1["candidates"][0]
        if "content" not in candidate_step1 or "parts" not in candidate_step1["content"]:
            return {
                "success": False,
                "error": "第一步：API 响应格式不正确",
                "response": response_data_step1
            }
        
        # 查找第一次生成的图像数据
        image_data_step1 = None
        generated_text_step1 = None
        
        for part in candidate_step1["content"]["parts"]:
            if "inlineData" in part and "data" in part["inlineData"]:
                image_data_step1 = part["inlineData"]["data"]
            elif "text" in part:
                generated_text_step1 = part["text"]
        
        if not image_data_step1:
            return {
                "success": False,
                "error": "第一步：未找到图像数据",
                "text": generated_text_step1,
                "response": response_data_step1
            }
        
        # ========== 第二步：如果有 added_prompt，使用图片+文字生成最终图片 ==========
        final_image_data = image_data_step1
        final_generated_text = generated_text_step1
        
        if added_prompt:
            # 构建第二次请求体：图片 + 附加提示词
            request_body_step2 = {
                "contents": [{
                    "parts": [
                        {
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": image_data_step1
                            }
                        },
                        {"text": added_prompt}
                    ]
                }]
            }
            
            # 如果指定了宽高比，添加到配置中
            if aspect_ratio:
                request_body_step2["generationConfig"] = {
                    "imageConfig": {
                        "aspectRatio": aspect_ratio
                    }
                }
            
            # 发送第二次请求
            response_step2 = requests.post(
                endpoint,
                json=request_body_step2,
                headers=headers,
                timeout=120
            )
            
            # 检查第二次响应状态
            if response_step2.status_code != 200:
                return {
                    "success": False,
                    "error": f"第二步 API 请求失败: HTTP {response_step2.status_code}",
                    "details": response_step2.text,
                    "step1_completed": True
                }
            
            # 解析第二次响应
            response_data_step2 = response_step2.json()
            
            # 提取第二次生成的图像数据
            if "candidates" not in response_data_step2 or len(response_data_step2["candidates"]) == 0:
                return {
                    "success": False,
                    "error": "第二步：API 响应中没有找到生成的图像",
                    "response": response_data_step2,
                    "step1_completed": True
                }
            
            candidate_step2 = response_data_step2["candidates"][0]
            if "content" not in candidate_step2 or "parts" not in candidate_step2["content"]:
                return {
                    "success": False,
                    "error": "第二步：API 响应格式不正确",
                    "response": response_data_step2,
                    "step1_completed": True
                }
            
            # 查找第二次生成的图像数据
            image_data_step2 = None
            generated_text_step2 = None
            
            for part in candidate_step2["content"]["parts"]:
                if "inlineData" in part and "data" in part["inlineData"]:
                    image_data_step2 = part["inlineData"]["data"]
                elif "text" in part:
                    generated_text_step2 = part["text"]
            
            if not image_data_step2:
                return {
                    "success": False,
                    "error": "第二步：未找到图像数据",
                    "text": generated_text_step2,
                    "response": response_data_step2,
                    "step1_completed": True
                }
            
            # 使用第二次生成的图像作为最终结果
            final_image_data = image_data_step2
            final_generated_text = generated_text_step2
        
        # ========== 保存最终图像 ==========
        # 解码并保存图像
        image_bytes = base64.b64decode(final_image_data)
        
        # 处理保存路径
        save_path = Path(save_path)
        
        # 如果路径是目录或没有扩展名，自动生成按序编号的文件名
        if save_path.is_dir() or not save_path.suffix or str(save_path).endswith(('/', '\\')):
            # 确定目标目录
            if save_path.is_file():
                # 如果路径是一个已存在的文件，使用其父目录
                target_dir = save_path.parent
            else:
                # 如果路径是目录或不存在，当作目录处理
                target_dir = save_path
            
            # 创建目录（如果不存在）
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取目录中已有的 .png 文件数量
            existing_files = list(target_dir.glob("*.png"))
            file_count = len(existing_files)
            
            # 生成新的编号（从1开始）
            next_number = file_count + 1
            
            # 生成新的文件名：编号.png
            save_path = target_dir / f"{next_number}.png"
        else:
            # 如果是完整的文件路径，确保有 .png 扩展名
            if not save_path.suffix:
                save_path = save_path.with_suffix('.png')
            
            # 创建目标目录（如果不存在）
            save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存图像
        with open(save_path, 'wb') as f:
            f.write(image_bytes)
        
        file_size = len(image_bytes)
        
        result = {
            "success": True,
            "file_path": str(save_path.absolute()),
            "file_size": file_size,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "generated_text": final_generated_text,
            "message": f"图片生成成功: {save_path.absolute()}"
        }
        
        # 如果使用了两步生成，添加相关信息
        if added_prompt:
            result["two_step_generation"] = True
            result["added_prompt"] = added_prompt
            result["step1_text"] = generated_text_step1
            result["step2_text"] = final_generated_text
        
        return result
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "请求超时，图像生成时间过长"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"网络请求失败: {str(e)}"
        }
    except base64.binascii.Error as e:
        return {
            "success": False,
            "error": f"Base64 解码失败: {str(e)}"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

