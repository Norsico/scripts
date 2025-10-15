# TTS 语音合成 API 使用说明

## 接口信息

- **URL**: `POST http://127.0.0.1:6666/tts-synthesis`
- **Content-Type**: `application/json`

## 请求参数

```json
{
  "text": {
    "自述文案": ["文案1", "文案2", "文案3", ...]
  },
  "prompt_audio_url": "https://example.com/prompt.wav",
  "save_path": "D:/output/audio",
  "api_key": "your_gitee_api_key"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | Object | 是 | 包含"自述文案"键的字典对象 |
| text.自述文案 | Array | 是 | 需要转换为语音的文案列表 |
| prompt_audio_url | String | 是 | 提示音频的URL（用于声音克隆） |
| save_path | String | 是 | 音频文件保存路径 |
| api_key | String | 是 | Gitee AI 的 API 密钥 |

## 响应格式

### 成功响应

```json
{
  "success": true,
  "message": "成功生成 3 个音频文件",
  "files": [
    "D:/output/audio/1.mp3",
    "D:/output/audio/2.mp3",
    "D:/output/audio/3.mp3"
  ],
  "total": 3
}
```

### 失败响应

```json
{
  "success": false,
  "error": "错误信息",
  "traceback": "详细错误堆栈（如果有）"
}
```

## 使用示例

### Python 示例

```python
import requests
import json

url = "http://127.0.0.1:6666/tts-synthesis"

payload = {
    "text": {
        "自述文案": [
            "我知道自己不是一个人在战斗，有大家的支持和协作。",
            "他的爱像秋天的阳光，看似清冷，却总能在我最需要的时候给予温暖。",
            "这是第三段文案内容。"
        ]
    },
    "prompt_audio_url": "https://example.com/voice_sample.wav",
    "save_path": "D:/tts_output",
    "api_key": "your_api_key_here"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

if result["success"]:
    print(f"成功生成 {result['total']} 个音频文件:")
    for file in result["files"]:
        print(f"  - {file}")
else:
    print(f"错误: {result['error']}")
```

### cURL 示例

```bash
curl -X POST http://127.0.0.1:6666/tts-synthesis \
  -H "Content-Type: application/json" \
  -d '{
    "text": {
      "自述文案": [
        "第一段文案",
        "第二段文案",
        "第三段文案"
      ]
    },
    "prompt_audio_url": "https://example.com/voice.wav",
    "save_path": "D:/audio_output",
    "api_key": "your_api_key"
  }'
```

### n8n 工作流示例

在 n8n 中使用 HTTP Request 节点：

1. **Method**: POST
2. **URL**: `http://127.0.0.1:6666/tts-synthesis`
3. **Body Content Type**: JSON
4. **Body**:
```json
{
  "text": {
    "自述文案": {{ $json.text_array }}
  },
  "prompt_audio_url": {{ $json.prompt_url }},
  "save_path": {{ $json.output_path }},
  "api_key": {{ $json.api_key }}
}
```

## 文件命名规则

生成的音频文件会按照顺序自动编号：
- 第1个文案 → `1.mp3`
- 第2个文案 → `2.mp3`
- 第3个文案 → `3.mp3`
- ...以此类推

## 注意事项

1. **API 密钥安全**: 请妥善保管你的 Gitee AI API 密钥，不要将其提交到代码仓库
2. **保存路径**: 确保保存路径存在或程序有权限创建该目录
3. **提示音频**: `prompt_audio_url` 用于声音克隆，建议使用清晰的音频样本
4. **批量处理**: 如果文案列表很长，处理时间会相应增加
5. **错误处理**: 如果某个文案生成失败，会返回错误信息和已成功生成的文件列表

## 依赖安装

在使用此功能前，请确保已安装 OpenAI 库：

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install openai>=1.0.0
```

## 模型说明

- **模型**: IndexTTS-2
- **基础 URL**: https://ai.gitee.com/v1
- **语音**: alloy（默认）

## 更多配置选项

如需修改情感文本等高级选项，可以编辑 `n8n-http-interface/tts_synthesis.py` 文件中的 `extra_body` 参数：

```python
extra_body={
    "prompt_audio_url": prompt_audio_url,
    "prompt_text": "",  # 提示文本
    "emo_text": "",     # 情感文本
    "use_emo_text": False,  # 是否使用情感文本
}
```

