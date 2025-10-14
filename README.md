# n8ntools - 命令行工具集

统一的命令行工具集，用于 n8n 工作流和其他自动化场景。

## 快速开始

```bash
# 查看所有可用工具
n8ntools --help

# 获取B站视频字幕
n8ntools get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"
```

## 在 n8n 中使用

### 方法一：使用绝对路径（推荐，最可靠）

在 n8n 的 Execute Command 节点中使用完整路径：

**Windows:**
```powershell
# 使用 Python 直接运行
python C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"
```

或使用批处理文件：
```cmd
C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.bat get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"
```

**在 n8n Execute Command 节点中的配置：**
- **Command**: `python`
- **Arguments**: 
  ```
  C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py
  get-subtitle-bilibili
  {{$json["video_url"]}}
  ```

### 方法二：配置系统环境变量（需要重启 n8n）

如果你希望使用简短的 `n8ntools` 命令，需要：

1. **添加到系统环境变量（非用户变量）**
   - 按 `Win + R`，输入 `sysdm.cpl`，回车
   - 点击"高级"标签
   - 点击"环境变量"
   - 在"**系统变量**"（不是用户变量）中找到 `Path`
   - 编辑，添加：`C:\Users\lenovo\Desktop\n8n-start\scripts`
   - 点击确定保存

2. **重启 n8n 服务**
   ```powershell
   # 如果 n8n 在终端运行，需要关闭终端并重新启动
   # 如果 n8n 作为服务运行，需要重启服务
   ```

3. **验证**
   ```bash
   n8ntools --help
   ```

### 方法三：使用 n8n 环境变量

在 n8n 的环境配置中添加工具路径：

```bash
# 在启动 n8n 前设置环境变量
$env:Path += ";C:\Users\lenovo\Desktop\n8n-start\scripts"
n8n start
```

## 可用工具

### get-subtitle-bilibili

获取B站视频字幕，自动去除时间戳返回纯文本。

**用法：**
```bash
n8ntools get-subtitle-bilibili <video_url> [options]
```

**参数：**
- `video_url`: B站视频链接或BV号
- `--keep-timestamp`: 保留时间戳（完整SRT格式）
- `--no-headless`: 显示浏览器窗口（调试用）

**示例：**
```bash
# 使用完整链接（返回纯文本）
n8ntools get-subtitle-bilibili "https://www.bilibili.com/video/BV1DdDAYfEWQ"

# 仅使用BV号
n8ntools get-subtitle-bilibili "BV1DdDAYfEWQ"

# 保留时间戳
n8ntools get-subtitle-bilibili "BV1DdDAYfEWQ" --keep-timestamp
```

**输出：**
- JSON格式输出到 stdout
- 日志信息输出到 stderr
- 默认返回纯文本字幕（无时间戳）

### save-base64

保存Base64数据到本地文件，自动识别文件类型。

**用法：**
```bash
n8ntools save-base64 <base64_data> <output_path> [options]
```

**参数：**
- `base64_data`: Base64编码的数据
- `output_path`: 输出文件路径
- `--input, -i`: 从文件读取Base64数据
- `--stdin`: 从标准输入读取
- `--force-ext, -e`: 强制使用指定的文件扩展名
- `--no-auto-ext`: 不自动添加扩展名

**示例：**
```bash
# 保存图片（自动识别格式）
n8ntools save-base64 "iVBORw0KGgo..." "output/image"

# 指定扩展名
n8ntools save-base64 "iVBORw0KGgo..." "output/image.png"

# 从文件读取
n8ntools save-base64 --input base64.txt "output/file"

# 强制使用JPG格式
n8ntools save-base64 --force-ext jpg "base64data" "output/photo"
```

**支持格式：**
- 图片：JPG, PNG, GIF, WebP, BMP, ICO
- 音频：MP3, WAV, OGG, FLAC
- 视频：MP4, WebM, FLV
- 文档：PDF, ZIP, JSON, XML

**输出：**
- JSON格式输出到 stdout（包含文件路径、大小、类型等信息）
- 日志信息输出到 stderr

**在 n8n 中使用的完整示例：**

Execute Command 节点配置：
```json
{
  "command": "python",
  "arguments": "C:\\Users\\lenovo\\Desktop\\n8n-start\\scripts\\n8ntools.py\nget-subtitle-bilibili\n{{$json[\"video_url\"]}}"
}
```

## 安装依赖

```bash
# 全局依赖（如果有）
pip install -r requirements.txt

# 特定工具的依赖
pip install -r get-subtitle-bilibili/requirements.txt
```

## 项目结构

```
scripts/
├── n8ntools.py              # 主入口脚本
├── n8ntools.bat             # Windows批处理包装器
├── SETUP.md                 # 详细安装配置指南
├── README.md                # 本文件
├── requirements.txt         # 全局依赖（可选）
└── get-subtitle-bilibili/   # 工具目录
    ├── get_bilibili_subtitle.py
    ├── requirements.txt
    └── README.md
```

## 添加新工具

详见 [SETUP.md](SETUP.md) 中的"添加新工具"章节。

简要步骤：

1. 创建工具目录和脚本
2. 在 `n8ntools.py` 的 `TOOLS` 字典中注册工具
3. 测试工具

示例：

```python
# 在 n8ntools.py 中添加
TOOLS = {
    'get-subtitle-bilibili': { ... },
    'your-new-tool': {
        'path': 'your-tool-folder/your_script.py',
        'description': '你的工具描述',
        'main_function': 'main'
    },
}
```

## n8n 集成最佳实践

### 1. 使用绝对路径

在 n8n 中，始终使用绝对路径是最可靠的方式：

```python
python C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py get-subtitle-bilibili "{{$json["url"]}}"
```

### 2. 处理输出

工具将 JSON 输出到 stdout，日志输出到 stderr。在 n8n 中：

- 使用 `JSON.parse()` 解析输出
- 启用 Execute Command 节点的 "Binary Data" 选项（如果需要）

### 3. 错误处理

在 n8n 工作流中添加错误处理：

```javascript
// 在 Set 节点或 Code 节点中
try {
  const result = JSON.parse($json.stdout);
  return result;
} catch (error) {
  console.error('Error parsing output:', $json.stderr);
  throw error;
}
```

### 4. 传递参数

使用表达式传递动态参数：

```
python C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py get-subtitle-bilibili "{{$json["video_url"]}}"
```

## 故障排除

### n8n 中找不到命令

**错误信息：** `'n8ntools' 不是内部或外部命令`

**原因：** n8n 无法在 PATH 中找到 `n8ntools`

**解决方案：**
1. 使用绝对路径（推荐）
2. 将 scripts 目录添加到**系统环境变量**（不是用户变量）
3. 重启 n8n 服务

### 编码问题

如果在 n8n 中看到乱码：

```powershell
# 在 Execute Command 节点前添加
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Python 未找到

确保 Python 在系统 PATH 中：

```bash
# 测试
python --version
```

如果不行，使用 Python 的完整路径：

```
C:\Python39\python.exe C:\Users\lenovo\Desktop\n8n-start\scripts\n8ntools.py ...
```

## 文档

- [SETUP.md](SETUP.md) - 详细的安装和配置指南
- [get-subtitle-bilibili/README.md](get-subtitle-bilibili/README.md) - B站字幕工具文档

## 许可证

MIT

## 更新日志

### 2025-10-12
- ✨ 初始版本
- ✨ 添加 get-subtitle-bilibili 工具
- 📝 添加 n8n 集成文档

