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

### 5. 多图片修改（图片+提示词）

支持使用多张图片和提示词生成/修改图片。

**POST** `/modify-image-with-prompt`

**示例 1：简单格式（Base64 字符串数组）- 保存到文件**
```json
{
  "images": [
    "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
    "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
  ],
  "prompt": "将这些图片组合成一张全景图",
  "save_path": "D:/output/images"
}
```

**示例 2：详细格式（包含 MIME 类型）- 保存到文件**
```json
{
  "images": [
    {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
      "mime_type": "image/png"
    },
    {
      "data": "/9j/4AAQSkZJRgABAQAAAQABAAD...",
      "mime_type": "image/jpeg"
    }
  ],
  "prompt": "基于这些图片，生成一个新的设计稿",
  "save_path": "D:/output/images",
  "aspect_ratio": "16:9"
}
```

**示例 3：返回 Base64 数据（不保存文件）**
```json
{
  "images": [
    "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
    "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
  ],
  "prompt": "将这些图片组合成一张全景图",
  "return_base64": true
}
```

**参数说明：**
- `images`（必需）：图片数组，支持两种格式：
  - Base64 字符串数组（自动识别为 PNG）
  - 对象数组，每个对象包含 `data`（Base64）和 `mime_type`（如 "image/png", "image/jpeg"）
- `prompt`（必需）：修改/生成图像的提示词
- `save_path`（可选）：图片保存路径。当 `return_base64=true` 时可不提供
- `return_base64`（可选，默认 false）：
  - `false`：生成的图片保存到本地，必须提供 `save_path` 参数，响应包含 `file_path` 字段
  - `true`：返回生成图片的 Base64 数据，无需提供 `save_path`，响应包含 `base64` 字段
- `aspect_ratio`（可选）：宽高比（如 "16:9", "1:1", "9:16"）

**响应示例（return_base64=true）：**
```json
{
  "success": true,
  "base64": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",
  "prompt": "将这些图片组合成一张全景图",
  "image_count": 2,
  "aspect_ratio": null,
  "generated_text": "图片已生成...",
  "message": "图片生成成功（返回 Base64 格式）"
}
```

## 许可证

MIT
