# B站字幕提取工具

一个使用无头浏览器自动从B站视频中提取字幕的Python脚本。输出JSON格式结果，方便与n8n等工作流工具集成。

## 功能特点

- 🚀 自动化提取B站视频字幕
- 🌐 使用Playwright无头浏览器技术
- 📝 支持多语言字幕
- 📤 输出JSON格式数据到stdout
- 🔧 方便与n8n等工作流工具集成
- 🎯 支持BV号或完整视频链接

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Playwright浏览器

```bash
playwright install chromium
```

或者安装所有浏览器：

```bash
playwright install
```

## 使用方法

### 基本用法

使用完整视频链接：
```bash
python get_bilibili_subtitle.py "https://www.bilibili.com/video/BV1DdDAYfEWQ"
```

使用BV号：
```bash
python get_bilibili_subtitle.py "BV1DdDAYfEWQ"
```

### 高级选项

显示浏览器窗口（调试模式）：
```bash
python get_bilibili_subtitle.py "BV1DdDAYfEWQ" --no-headless
```

保留时间戳（完整SRT格式）：
```bash
python get_bilibili_subtitle.py "BV1DdDAYfEWQ" --keep-timestamp
```

默认情况下，脚本会自动去除时间戳，只返回纯文本字幕，方便进一步处理。如果需要完整的SRT格式（包含时间戳），请使用 `--keep-timestamp` 参数。

查看帮助：
```bash
python get_bilibili_subtitle.py --help
```

### 在n8n中使用

在n8n的 "Execute Command" 节点中：

1. **命令**：`python`
2. **参数**：
   - `get_bilibili_subtitle.py`
   - `{{ $json.video_url }}`
3. **工作目录**：脚本所在目录

脚本会将JSON结果输出到stdout，n8n会自动解析为JSON对象。

## 输出说明

### 输出流分离

脚本采用标准的输出流分离设计：

- **stdout（标准输出）**：仅输出JSON格式的结果数据
- **stderr（标准错误）**：输出所有日志和进度信息

这样设计的好处是，n8n等工具可以直接捕获stdout中的JSON数据，而不会被日志信息干扰。

### JSON数据结构

**默认模式（纯文本，无时间戳）：**

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "vid": "BV1DdDAYfEWQ",
    "host": "bilibili_zm",
    "hostAlias": "哔哩哔哩",
    "title": "视频标题.srt",
    "status": "解析完成",
    "subtitleItemVoList": [
      {
        "lang": "中文",
        "langDesc": "中文",
        "content": "兄弟们有人在游戏里面交过朋友吗\n前段时间打游戏\n遇到一个哥们给自己起了个名字叫季沧海\n...",
        "content_with_timestamp": "1\n0:0:7,42 --> 0:0:11,54\n兄弟们有人在游戏里面交过朋友吗\n\n2\n...",
        "srcUrl": null,
        "isTranslatable": null
      }
    ]
  }
}
```

说明：
- `content`: 纯文本字幕（默认，去除了序号和时间戳）
- `content_with_timestamp`: 原始SRT格式（包含完整时间戳信息）

**使用 `--keep-timestamp` 时（完整SRT格式）：**

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "vid": "BV1DdDAYfEWQ",
    "host": "bilibili_zm",
    "hostAlias": "哔哩哔哩",
    "title": "视频标题.srt",
    "status": "解析完成",
    "subtitleItemVoList": [
      {
        "lang": "中文",
        "langDesc": "中文",
        "content": "1\n0:0:7,42 --> 0:0:11,54\n兄弟们有人在游戏里面交过朋友吗\n\n2\n0:0:11,87 --> 0:0:13,15\n前段时间打游戏\n...",
        "srcUrl": null,
        "isTranslatable": null
      }
    ]
  }
}
```

## 示例输出

运行命令：
```bash
python get_bilibili_subtitle.py "BV1DdDAYfEWQ"
```

**stderr输出（日志）：**
```
B站字幕提取工具
视频链接: https://www.bilibili.com/video/BV1DdDAYfEWQ

正在访问网页...
正在输入视频链接: https://www.bilibili.com/video/BV1DdDAYfEWQ
正在点击提取按钮...
等待字幕提取...
✓ 接收到API响应
✓ 字幕提取成功
  视频ID: BV1DdDAYfEWQ
  标题: 关于我帮打游戏认识的中二病好友，追他女神这件事.srt
  状态: 解析完成
  字幕数量: 1

✓ 任务完成！
```

**stdout输出（JSON数据）：**
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "vid": "BV1DdDAYfEWQ",
    ...
  }
}
```

## 技术实现

本脚本通过以下步骤工作：

1. 使用Playwright启动无头Chromium浏览器
2. 访问[飞鱼视频下载助手](https://www.feiyudo.com/caption/subtitle/bilibili)
3. 自动填写视频链接并点击提取按钮
4. 监听并拦截API请求 (`https://www.feiyudo.com/api/video/subtitleExtract`)
5. 解析API响应并输出JSON到stdout

## 常见问题

### Q: 提示"playwright: command not found"

A: 请先安装playwright：`pip install playwright`，然后运行 `playwright install chromium`

### Q: 等待超时或无法获取字幕

A: 可能的原因：
- 网络连接问题
- 视频没有字幕
- 网站结构发生变化

建议使用 `--no-headless` 参数查看浏览器实际操作过程进行调试。

### Q: 如何在n8n中解析字幕内容？

A: 脚本输出的JSON中，字幕内容在 `data.subtitleItemVoList[0].content` 字段，格式为SRT。你可以在n8n中使用以下表达式访问：

```javascript
{{ $json.data.subtitleItemVoList[0].content }}
```

### Q: 如何处理多语言字幕？

A: `subtitleItemVoList` 是一个数组，包含所有可用的字幕语言。遍历该数组即可获取所有语言的字幕：

```javascript
{{ $json.data.subtitleItemVoList.map(item => ({
  lang: item.lang,
  content: item.content
})) }}
```

## 依赖项

- Python 3.8+
- Playwright 1.40.0+

## 声明

本工具仅供学习和研究使用。请尊重视频创作者的版权，合理使用字幕内容。

字幕数据来源于[飞鱼视频下载助手](https://www.feiyudo.com/caption/subtitle/bilibili)。

## 许可证

MIT License

