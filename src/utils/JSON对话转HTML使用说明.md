# JSON对话记录转HTML可视化工具

这个工具集可以将OpenHands代理的JSON格式对话记录转换为美观的HTML可视化界面。

## 功能特点

- 🎨 美观的可视化界面，不同角色使用不同颜色主题
- 📱 响应式设计，支持移动设备
- 🔧 支持工具调用和响应的专门显示
- 📊 统计信息展示（消息数量统计）
- 🖥️ 代码块语法高亮
- 📦 批量转换支持

## 文件说明

- `json_to_html_converter.py` - 单文件转换脚本
- `batch_convert.py` - 批量转换脚本
- `JSON对话转HTML使用说明.md` - 本说明文档

## 使用方法

### 1. 单文件转换

```bash
# 基本用法（输出文件自动命名）
python json_to_html_converter.py path/to/conversation_history.json

# 指定输出文件名
python json_to_html_converter.py path/to/conversation_history.json -o output.html
```

### 2. 批量转换

```bash
# 转换logs目录下所有conversation_history.json文件
python batch_convert.py logs/

# 指定输出目录
python batch_convert.py logs/ -o html_output/

# 自定义文件匹配模式（转换所有.json文件）
python batch_convert.py logs/ -p "**/*.json"
```

### 3. 命令行参数说明

#### json_to_html_converter.py
- `json_file`: 输入的JSON文件路径（必需）
- `-o, --output`: 输出HTML文件路径（可选）

#### batch_convert.py
- `input_dir`: 输入目录路径（必需）
- `-o, --output`: 输出目录路径（可选，默认在原文件目录）
- `-p, --pattern`: 文件匹配模式（默认：`**/conversation_history.json`）

## 输出效果

生成的HTML文件包含：

1. **头部信息**：生成时间、源文件名
2. **对话内容**：
   - 🔧 系统消息（紫色渐变）
   - 👤 用户消息（粉红色渐变，右对齐）
   - 🤖 助手消息（蓝色渐变，左对齐）
   - ⚙️ 工具响应（绿色渐变，居中）
3. **工具调用展示**：格式化的工具名称和参数
4. **统计信息**：各类消息数量统计
5. **响应式布局**：适配不同屏幕尺寸

## 样式特点

- **现代化设计**：使用渐变色彩和阴影效果
- **易读性**：合适的字体、间距和颜色对比
- **代码友好**：工具调用和结果使用等宽字体
- **移动适配**：在手机上也能良好显示

## 示例

转换CSBench项目中的对话记录：

```bash
# 转换单个文件
python json_to_html_converter.py logs/20250831_123808_code_act_agent_cmu-cs-ics-attack-lab-phase1/conversation_history.json

# 批量转换所有对话记录
python batch_convert.py logs/ -o html_conversations/
```

## 依赖要求

- Python 3.6+
- 标准库模块：json, html, argparse, datetime, pathlib

无需安装额外的第三方包！

## 故障排除

1. **编码问题**：确保JSON文件使用UTF-8编码
2. **权限问题**：确保有读取源文件和写入目标目录的权限
3. **JSON格式**：确保输入文件是有效的JSON格式

## 自定义样式

如需修改样式，编辑 `json_to_html_converter.py` 中的 `get_css_styles()` 函数。

---

**提示**：生成的HTML文件可以直接在浏览器中打开，无需web服务器。
