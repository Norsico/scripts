# n8n HTTP Tools

为 n8n 工作流提供的 HTTP API 工具集。

## 快速开始

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
2. 启动服务
   ```bash
   python n8n-http-tools.py
   ```
   默认服务地址：`http://127.0.0.1:6666`

## 配置

根目录的 `config.example.json` 自己创建一个 `config.json` 并填好参数：

```json
{
  "gemini": {
    "base_url": "",   
    "model": "gemini-2.5-flash-image-preview",
    "api_key": "",
    "return_base64_default": false
  }
}
```

接口未显式传入 `base_url` / `model` / `api_key` / `return_base64` 时，会自动使用这里的配置值。

## API 接口

### 1. 保存 Base64 文件

`POST /save-base64`

```json
{
  "data": "base64_encoded_data",
  "path": "C:\\\\output\\\\file"
}
```

可选参数：`force_ext`、`auto_extension`(默认 true)、`mime_type`。自动识别常见图片、音频、视频和文档格式。

### 2. 获取 B 站字幕

`POST /get-bilibili-subtitle`

```json
{
  "url": "https://www.bilibili.com/video/BV号",
  "text_only": true
}
```

### 3. TTS 语音合成

`POST /tts-synthesis`

```json
{
  "text": { "自述文案": ["文案1", "文案2"] },
  "prompt_audio_url": "https://example.com/prompt.wav",
  "save_path": "D:/output/audio",
  "api_key": "your_api_key"
}
```

### 4. Gemini 图像生成

`POST /generate-image-gemini`

```json
{
  "prompt": "Create a picture of a nano banana dish in a fancy restaurant",
  "save_path": "D:/output/images",
  "aspect_ratio": "16:9",
  "added_prompt": "refine with cinematic lighting"
}
```

如果不传 `base_url` / `model` / `api_key`，会使用 `config.json` 中的值。

### 5. 多图片修改（图片 + 提示词）

`POST /modify-image-with-prompt`

示例（返还 Base64，不落盘）：

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

参数说明：
- `images`（必需）：Base64 字符串数组，或带 `data` / `mime_type` 的对象数组。
- `prompt`（必需）：生成/修改提示词。
- `save_path`（可选）：保存路径；当 `return_base64=true` 时可不提供。
- `return_base64`（可选）：默认读取 `config.json` 中的 `return_base64_default`（未配置则为 false）。为 false 时必须提供 `save_path`。
- `aspect_ratio`（可选）：宽高比，如 `"16:9"`、`"1:1"`、`"9:16"`。

## 许可证

MIT
