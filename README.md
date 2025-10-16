# n8n HTTP Tools

为 n8n 工作流提供的 HTTP API 工具集。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 启动服务

```bash
start-http-tools.bat
```

服务地址：http://127.0.0.1:6666

## API 接口

### 1. 保存 Base64 文件

自动识别文件类型并保存到本地。

**POST** `/save-base64`

```json
{
  "data": "base64_encoded_data",
  "path": "C:\\output\\file"
}
```

**可选参数：**
- `force_ext`: 强制指定文件扩展名
- `auto_extension`: 是否自动添加扩展名（默认 true）
- `mime_type`: 指定 MIME 类型来确定文件扩展名

**支持格式：** JPG, PNG, GIF, WebP, BMP, MP3, WAV, OGG, FLAC, MP4, WebM, PDF, ZIP, JSON, XML

### 2. 获取B站字幕

**POST** `/get-bilibili-subtitle`

```json
{
  "url": "https://www.bilibili.com/video/BV1DdDAYfEWQ",
  "text_only": true
}
```

### 3. TTS 语音合成

**POST** `/tts-synthesis`

```json
{
  "text": {
    "自述文案": ["文案1", "文案2", "文案3"]
  },
  "prompt_audio_url": "https://example.com/prompt.wav",
  "save_path": "D:/output/audio",
  "api_key": "your_api_key"
}
```

### 4. Gemini 图像生成

**POST** `/generate-image-gemini`

```json
{
  "prompt": "Create a picture of a nano banana dish in a fancy restaurant",
  "save_path": "D:/output/images"
}
```

**可选参数：**
- `aspect_ratio`: 宽高比（如 "16:9", "1:1", "9:16"）
- `added_prompt`: 附加提示词（启用两步生成：先用 prompt 生成初始图，再用初始图+added_prompt 生成最终图）

**说明：** 
- 图片会自动按序编号保存（1.png, 2.png, 3.png...）
- 使用 `added_prompt` 时会进行两步串行生成，第一步图片不保存，只保存最终优化后的图片
- 内置智能重试机制：如果 API 未返回有效图片，会自动重试（最多5次），确保每次都能生成有效图片

## 许可证

MIT
