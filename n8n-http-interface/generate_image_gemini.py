"""
Google Gemini 图像生成模块
使用 Gemini 2.5 Flash Image 模型生成图片
"""

import base64
import requests
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


def _request_with_retry(
    endpoint: str,
    request_body: dict,
    headers: dict,
    max_retries: int,
    step_name: str = "生成"
) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[Any, Any]]]:
    """
    带重试的图片生成请求
    
    Args:
        endpoint: API 端点
        request_body: 请求体
        headers: 请求头
        max_retries: 最大重试次数
        step_name: 步骤名称（用于日志）
    
    Returns:
        (成功标志, 图片数据base64, 生成的文本, 错误信息)
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                endpoint,
                json=request_body,
                headers=headers,
                timeout=120
            )
            
            # 检查响应状态
            if response.status_code != 200:
                if attempt < max_retries:
                    print(f"{step_name} 第 {attempt} 次尝试失败 (HTTP {response.status_code})，正在重试...")
                    time.sleep(1)  # 短暂延迟后重试
                    continue
                else:
                    return False, None, None, {
                        "error": f"{step_name} API 请求失败: HTTP {response.status_code}",
                        "details": response.text,
                        "attempts": attempt
                    }
            
            # 解析响应
            response_data = response.json()
            
            # 检查是否有 candidates
            if "candidates" not in response_data or len(response_data["candidates"]) == 0:
                if attempt < max_retries:
                    print(f"{step_name} 第 {attempt} 次尝试：API 未返回图像候选项，正在重试...")
                    time.sleep(1)
                    continue
                else:
                    return False, None, None, {
                        "error": f"{step_name}：API 响应中没有找到图像候选项",
                        "response": response_data,
                        "attempts": attempt
                    }
            
            candidate = response_data["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                if attempt < max_retries:
                    print(f"{step_name} 第 {attempt} 次尝试：API 响应格式不正确，正在重试...")
                    time.sleep(1)
                    continue
                else:
                    return False, None, None, {
                        "error": f"{step_name}：API 响应格式不正确",
                        "response": response_data,
                        "attempts": attempt
                    }
            
            # 查找图像数据
            image_data = None
            generated_text = None
            
            for part in candidate["content"]["parts"]:
                if "inlineData" in part and "data" in part["inlineData"]:
                    image_data = part["inlineData"]["data"]
                elif "text" in part:
                    generated_text = part["text"]
            
            # 检查是否找到了图像数据
            if not image_data:
                if attempt < max_retries:
                    print(f"{step_name} 第 {attempt} 次尝试：未找到有效图像数据，正在重试...")
                    time.sleep(1)
                    continue
                else:
                    return False, None, None, {
                        "error": f"{step_name}：未找到有效图像数据（已重试{attempt}次）",
                        "text": generated_text,
                        "response": response_data,
                        "attempts": attempt
                    }
            
            # 成功获取图像数据
            if attempt > 1:
                print(f"{step_name} 第 {attempt} 次尝试成功！")
            return True, image_data, generated_text, None
            
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(f"{step_name} 第 {attempt} 次尝试超时，正在重试...")
                time.sleep(2)
                continue
            else:
                return False, None, None, {
                    "error": f"{step_name}：请求超时（已重试{attempt}次）",
                    "attempts": attempt
                }
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                print(f"{step_name} 第 {attempt} 次尝试网络错误: {str(e)}，正在重试...")
                time.sleep(2)
                continue
            else:
                return False, None, None, {
                    "error": f"{step_name}：网络请求失败: {str(e)}",
                    "attempts": attempt
                }
        except Exception as e:
            # 对于其他异常，不重试
            return False, None, None, {
                "error": f"{step_name}：发生错误: {str(e)}",
                "attempts": attempt
            }
    
    # 不应该到达这里
    return False, None, None, {
        "error": f"{step_name}：未知错误",
        "attempts": max_retries
    }


def generate_image_gemini_core(
    prompt: str,
    save_path: str,
    aspect_ratio: Optional[str] = None,
    added_prompt: Optional[str] = None,
    base_url: str = "http://127.0.0.1:5345",
    api_key: str = "123456Ab@",
    max_retries: int = 5
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
        max_retries: 最大重试次数（默认5次），用于处理未返回有效图片的情况
    
    Returns:
        包含操作结果的字典
    """
    try:
        # 构建完整的 API 端点
        endpoint = f"{base_url.rstrip('/')}/v1beta/models/gemini-2.5-flash-image:generateContent"
        
        # 设置请求头
        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # ========== 第一步：使用 prompt 生成初始图片（带重试） ==========
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
        
        # 使用重试机制发送第一次请求
        success_step1, image_data_step1, generated_text_step1, error_step1 = _request_with_retry(
            endpoint=endpoint,
            request_body=request_body_step1,
            headers=headers,
            max_retries=max_retries,
            step_name="第一步"
        )
        
        if not success_step1:
            return {
                "success": False,
                **error_step1
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
            
            # 使用重试机制发送第二次请求
            success_step2, image_data_step2, generated_text_step2, error_step2 = _request_with_retry(
                endpoint=endpoint,
                request_body=request_body_step2,
                headers=headers,
                max_retries=max_retries,
                step_name="第二步"
            )
            
            if not success_step2:
                error_result = {
                    "success": False,
                    "step1_completed": True,
                    **error_step2
                }
                return error_result
            
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

