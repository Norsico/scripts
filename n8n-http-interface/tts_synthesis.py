"""
TTS 语音合成模块
使用 OpenAI API 进行文本转语音合成
"""

import os
from pathlib import Path
from openai import OpenAI


def tts_synthesis_core(text_dict, prompt_audio_url, save_path, api_key):
    """
    TTS 语音合成核心函数
    
    参数:
        text_dict: 包含 "自述文案" 键的字典，值为字符串数组
        prompt_audio_url: 提示音频的URL
        save_path: 保存路径
        api_key: API密钥
    
    返回:
        {
            "success": True/False,
            "message": "处理信息",
            "files": ["生成的文件路径列表"],
            "error": "错误信息（如果有）"
        }
    """
    try:
        # 验证参数
        if not isinstance(text_dict, dict):
            return {
                "success": False,
                "error": "text 参数必须是字典类型"
            }
        
        if "自述文案" not in text_dict:
            return {
                "success": False,
                "error": "text 字典中缺少 '自述文案' 键"
            }
        
        text_list = text_dict["自述文案"]
        
        if not isinstance(text_list, list):
            return {
                "success": False,
                "error": "'自述文案' 的值必须是列表类型"
            }
        
        if len(text_list) == 0:
            return {
                "success": False,
                "error": "'自述文案' 列表不能为空"
            }
        
        # 创建保存目录
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 OpenAI 客户端
        client = OpenAI(
            base_url="https://ai.gitee.com/v1",
            api_key=api_key,
        )
        
        generated_files = []
        
        # 遍历文案列表，逐个生成音频
        for index, text_content in enumerate(text_list, start=1):
            # 生成文件名: 1.mp3, 2.mp3, 3.mp3...
            output_file = save_dir / f"{index}.mp3"
            
            try:
                # 调用 TTS API
                response = client.audio.speech.create(
                    input=text_content,
                    model="IndexTTS-2",
                    extra_body={
                        "prompt_audio_url": prompt_audio_url,
                        "prompt_text": "",  # 可以根据需要调整
                        "emo_text": "",
                        "use_emo_text": False,
                    },
                    voice="alloy",
                )
                
                # 保存音频文件
                response.stream_to_file(str(output_file))
                
                generated_files.append(str(output_file))
                
            except Exception as e:
                # 如果某个文件生成失败，记录错误但继续处理其他文件
                print(f"生成第 {index} 个文件时出错: {str(e)}")
                return {
                    "success": False,
                    "error": f"生成第 {index} 个音频文件时失败: {str(e)}",
                    "files": generated_files  # 返回已成功生成的文件
                }
        
        return {
            "success": True,
            "message": f"成功生成 {len(generated_files)} 个音频文件",
            "files": generated_files,
            "total": len(generated_files)
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

