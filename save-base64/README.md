# Base64 文件保存工具

自动识别 Base64 编码数据的文件类型，并保存到本地文件系统。支持图片、音频、视频等多种格式。

## 功能特点

- 🔍 **自动识别文件类型**：通过魔术字节自动检测文件格式
- 📁 **智能扩展名**：自动添加正确的文件扩展名
- 🎨 **支持多种格式**：
  - 图片：JPG, PNG, GIF, WebP, BMP, ICO
  - 音频：MP3, WAV, OGG, FLAC, MP4
  - 视频：MP4, WebM, FLV
  - 文档：PDF, ZIP
  - 文本：JSON, XML, HTML, TXT
- 🔧 **灵活输入**：支持命令行参数、文件或标准输入
- 📤 **JSON 输出**：输出结构化结果，方便集成到工作流

## 安装

无需额外依赖，使用 Python 标准库即可。

## 使用方法

### 通过 n8ntools（推荐）

```bash
# 基本用法
n8ntools save-base64 "<base64_data>" "output/file"

# 指定扩展名
n8ntools save-base64 "<base64_data>" "output/file.png"

# 强制使用特定扩展名
n8ntools save-base64 --force-ext jpg "<base64_data>" "output/image"
```

### 直接使用脚本

```bash
# 从命令行参数
python save_base64_file.py "iVBORw0KGgo..." "output/image"

# 从文件读取
python save_base64_file.py --input base64.txt "output/image"

# 从标准输入
echo "iVBORw0KGgo..." | python save_base64_file.py --stdin "output/image"
```

### 命令行参数

- `base64_data`: Base64 编码的数据（或使用 --input / --stdin）
- `output_path`: 输出文件路径
- `--input, -i`: 从文件读取 Base64 数据
- `--stdin`: 从标准输入读取
- `--force-ext, -e`: 强制使用指定的文件扩展名
- `--no-auto-ext`: 不自动添加扩展名

## 在 n8n 中使用

### 方法 1：使用 Execute Command 节点

**配置：**
```
Command: python
Arguments:
C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
save-base64
{{$json["base64_data"]}}
{{$json["output_path"]}}
```

### 方法 2：从前一个节点获取 Base64

假设前面节点输出了 Base64 数据：

```json
{
  "data": "iVBORw0KGgoAAAANSUhEUgA...",
  "filename": "image.png"
}
```

Execute Command 配置：
```
Command: python
Arguments:
C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
save-base64
{{$json["data"]}}
C:\output\{{$json["filename"]}}
```

### 方法 3：处理 Data URL

如果数据是 Data URL 格式（如 `data:image/png;base64,...`），工具会自动提取 Base64 部分：

```
Command: python
Arguments:
C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
save-base64
{{$json["dataUrl"]}}
output/image
```

## 输出格式

### 成功响应

```json
{
  "success": true,
  "file_path": "C:\\output\\image.png",
  "file_size": 45678,
  "file_type": "png",
  "mime_type": "image/png"
}
```

### 失败响应

```json
{
  "success": false,
  "error": "Base64 解码失败: Invalid base64-encoded string"
}
```

## 示例

### 示例 1：保存图片

```bash
# Base64 数据（PNG 图片）
BASE64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

n8ntools save-base64 "$BASE64" "output/pixel"
```

输出：
```
检测到文件类型: png (image/png)
正在保存文件到: output/pixel.png
✓ 文件保存成功
  路径: C:\Users\lenovo\Desktop\n8n-start\scripts\output\pixel.png
  大小: 95 字节 (0.09 KB)
  类型: image/png
```

### 示例 2：保存音频文件

```bash
# 从文件读取 Base64（MP3 音频）
n8ntools save-base64 --input audio_base64.txt "music/song.mp3"
```

### 示例 3：在 n8n 工作流中使用

**场景**：从 HTTP 请求获取图片的 Base64，保存到本地

1. **HTTP Request 节点**：获取包含 Base64 的 JSON
2. **Execute Command 节点**：
   - Command: `python`
   - Arguments:
     ```
     C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
     save-base64
     {{$json["image_data"]}}
     C:\images\{{$json["image_name"]}}
     ```
3. **Set 节点**：处理返回的 JSON 结果

## 支持的文件格式

### 图片格式

| 格式 | 扩展名 | MIME 类型 |
|------|--------|-----------|
| JPEG | .jpg | image/jpeg |
| PNG | .png | image/png |
| GIF | .gif | image/gif |
| WebP | .webp | image/webp |
| BMP | .bmp | image/bmp |
| ICO | .ico | image/x-icon |

### 音频格式

| 格式 | 扩展名 | MIME 类型 |
|------|--------|-----------|
| MP3 | .mp3 | audio/mpeg |
| WAV | .wav | audio/wav |
| OGG | .ogg | audio/ogg |
| FLAC | .flac | audio/flac |

### 视频格式

| 格式 | 扩展名 | MIME 类型 |
|------|--------|-----------|
| MP4 | .mp4 | video/mp4 |
| WebM | .webm | video/webm |
| FLV | .flv | video/x-flv |

### 其他格式

| 格式 | 扩展名 | MIME 类型 |
|------|--------|-----------|
| PDF | .pdf | application/pdf |
| ZIP | .zip | application/zip |
| JSON | .json | application/json |
| XML | .xml | application/xml |
| HTML | .html | text/html |
| 文本 | .txt | text/plain |

## 注意事项

1. **路径权限**：确保对目标目录有写入权限
2. **自动创建目录**：如果目标目录不存在，会自动创建
3. **文件覆盖**：如果文件已存在，会被覆盖
4. **Base64 格式**：支持纯 Base64 和 Data URL 格式
5. **大文件**：处理大文件时注意内存占用

## 故障排除

### Base64 解码失败

**原因**：Base64 数据格式不正确

**解决方案**：
- 检查 Base64 数据是否完整
- 确认没有包含额外的空格或换行符
- 如果是 Data URL，确保格式正确

### 文件保存失败

**原因**：权限不足或路径不存在

**解决方案**：
- 检查目标目录的写入权限
- 使用绝对路径
- 确保磁盘空间充足

### 文件类型识别错误

**原因**：文件头部数据不标准

**解决方案**：
- 使用 `--force-ext` 手动指定扩展名
- 检查原始 Base64 数据是否正确

## 技术细节

### 文件类型检测原理

工具通过读取文件的**魔术字节**（Magic Bytes）来识别文件类型。魔术字节是文件开头的特定字节序列，用于标识文件格式。

例如：
- PNG 文件以 `89 50 4E 47 0D 0A 1A 0A` 开头
- JPEG 文件以 `FF D8 FF` 开头
- MP3 文件以 `ID3` 或 `FF FB` 开头

### Data URL 支持

Data URL 格式：`data:[<mediatype>][;base64],<data>`

示例：
```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB...
```

工具会自动提取其中的 Base64 部分。

## 更新日志

### 2025-10-14
- ✨ 初始版本
- 🔍 支持自动文件类型识别
- 📁 支持多种输入方式
- 🎨 支持常见的图片、音频、视频格式

## 许可证

MIT

