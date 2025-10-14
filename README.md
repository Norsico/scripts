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

**支持格式：** JPG, PNG, GIF, WebP, BMP, MP3, WAV, OGG, FLAC, MP4, WebM, PDF, ZIP, JSON, XML

### 2. 获取B站字幕

获取B站视频字幕，默认返回纯文本（无时间戳）。

**POST** `/get-bilibili-subtitle`

```json
{
  "url": "https://www.bilibili.com/video/BV1DdDAYfEWQ",
  "text_only": true
}
```

## 许可证

MIT
