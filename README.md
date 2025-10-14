# n8n Tools - 工具集

为 n8n 工作流提供的实用工具集，支持命令行和 HTTP API 两种方式。

## 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

## 方式一：HTTP API（推荐）

### 启动服务

```bash
# Windows
start-http-tools.bat

# 或直接运行
python n8n-http-tools.py
```

服务地址：http://127.0.0.1:6666

### API 端点

#### 1. 保存 Base64 文件

**POST** `/save-base64`

```json
{
  "data": "base64_encoded_data",
  "path": "C:\\output\\file"
}
```

#### 在 n8n 中使用

**HTTP Request 节点配置：**
- Method: POST
- URL: `http://127.0.0.1:6666/save-base64`
- Body:
  ```json
  {
    "data": "{{$json[\"base64_data\"]}}",
    "path": "C:\\images\\{{$json[\"filename\"]}}"
  }
  ```

## 方式二：命令行

### 查看所有工具

```bash
python n8ntools.py --help
```

### 1. 获取B站字幕

```bash
# 基本用法（返回纯文本，无时间戳）
python n8ntools.py get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"

# 保留时间戳
python n8ntools.py get-subtitle-bilibili "BV1DdDAYfEWQ" --keep-timestamp
```

**在 n8n 中使用：**
- Command: `python`
- Arguments:
  ```
  C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
  get-subtitle-bilibili
  {{$json["video_url"]}}
  ```

### 2. 保存 Base64 文件（命令行，不推荐用于大文件）

```bash
# 基本用法
python n8ntools.py save-base64 "base64_data" "output/file"

# 强制指定扩展名
python n8ntools.py save-base64 --force-ext jpg "base64_data" "output/image"
```

**注意：** Base64 数据较大时，请使用 HTTP API 方式。

## 添加到环境变量（可选）

将 `C:\Users\lenovo\Desktop\n8n-start\scripts` 添加到系统 PATH，即可直接使用 `n8ntools` 命令。

**Windows 设置：**
1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在系统变量中找到 `Path`，添加：`C:\Users\lenovo\Desktop\n8n-start\scripts`
3. 重启终端

## 添加新工具

编辑 `n8ntools.py`，在 `TOOLS` 字典中注册：

```python
TOOLS = {
    'your-tool': {
        'path': 'your-tool/your_script.py',
        'description': '工具描述',
        'main_function': 'main'
    },
}
```

## 支持的文件格式

**图片**: JPG, PNG, GIF, WebP, BMP, ICO  
**音频**: MP3, WAV, OGG, FLAC  
**视频**: MP4, WebM, FLV  
**文档**: PDF, ZIP, JSON, XML

## 许可证

MIT

