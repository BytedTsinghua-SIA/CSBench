#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: Apache-2.0
"""
对话JSON转HTML可视化脚本
将OpenHands代理的对话记录JSON文件转换为HTML格式的可视化界面
"""

import json
import html
import argparse
from datetime import datetime
from pathlib import Path
import os

def escape_html(text):
    """转义HTML特殊字符"""
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text)

def format_tool_call(tool_call, tool_result_content=None):
    """格式化工具调用，可选包含工具执行结果"""
    tool_name = tool_call.get('function', {}).get('name', '未知工具')
    arguments = tool_call.get('function', {}).get('arguments', '{}')
    
    try:
        args_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
        args_formatted = json.dumps(args_dict, indent=2, ensure_ascii=False)
    except:
        args_formatted = str(arguments)
    
    html = f"""
    <div class="tool-call">
        <div class="tool-header">🔧 工具调用: {escape_html(tool_name)}</div>
        <pre class="tool-args">{escape_html(args_formatted)}</pre>"""
    
    # 如果有工具执行结果，添加到同一个框中
    if tool_result_content:
        cleaned_content = clean_tool_output(tool_result_content)
        html += f"""
        <div class="tool-result-header">⚙️ 工具执行结果</div>
        <pre class="tool-result-content">{escape_html(cleaned_content)}</pre>"""
    
    html += """
    </div>
    """
    
    return html

def clean_tool_output(content):
    """清理工具执行输出，去掉多余的格式化信息"""
    if not content:
        return ""
    
    # 按行分割内容
    lines = content.strip().split('\n')
    cleaned_lines = []
    
    skip_next = False
    for i, line in enumerate(lines):
        # 跳过 "=== Output for xxx ===" 开头
        if line.strip().startswith("=== Output for") and line.strip().endswith("==="):
            continue
            
        # 跳过 "=== End of Output ===" 结尾
        if line.strip() == "=== End of Output ===":
            continue
            
        # 跳过 "Exit code: x" 行
        if line.strip().startswith("Exit code:"):
            continue
            
        cleaned_lines.append(line)
    
    # 合并清理后的内容
    cleaned_content = '\n'.join(cleaned_lines).strip()
    
    # 去掉可能的重复内容
    # 如果内容看起来像是重复的（通过简单的长度检查）
    if cleaned_content:
        # 尝试检测是否有重复的块
        content_parts = cleaned_content.split('\n\n')
        if len(content_parts) >= 2:
            # 检查是否有相同的部分
            unique_parts = []
            seen_parts = set()
            for part in content_parts:
                part_clean = part.strip()
                if part_clean and part_clean not in seen_parts:
                    unique_parts.append(part)
                    seen_parts.add(part_clean)
            cleaned_content = '\n\n'.join(unique_parts)
    
    return cleaned_content

def format_tool_result(content):
    """格式化工具执行结果"""
    cleaned_content = clean_tool_output(content)
    
    return f"""
    <div class="tool-result">
        <div class="tool-result-header">⚙️ 工具执行结果</div>
        <pre class="tool-result-content">{escape_html(cleaned_content)}</pre>
    </div>
    """

def format_message_content(content):
    """格式化消息内容，处理代码块和换行"""
    if not content:
        return ""
    
    content = escape_html(content)
    
    # 简单的代码块检测和高亮
    lines = content.split('\n')
    formatted_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                formatted_lines.append('</pre>')
                in_code_block = False
            else:
                lang = line.strip()[3:].strip()
                formatted_lines.append(f'<pre class="code-block" data-lang="{lang}">')
                in_code_block = True
        elif in_code_block:
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    if in_code_block:
        formatted_lines.append('</pre>')
    
    return '<br>'.join(formatted_lines)

def get_css_styles():
    """返回CSS样式"""
    return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .conversation {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .message {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }
        
        .message.system {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.user {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-left: 10%;
        }
        
        .message.assistant {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            margin-right: 10%;
        }
        
        .message.tool {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: #333;
            margin-left: 5%;
            margin-right: 5%;
        }
        
        .role-label {
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .message-content {
            font-size: 15px;
            line-height: 1.7;
        }
        
        .tool-call {
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid rgba(255,255,255,0.3);
        }
        
        .tool-header {
            font-weight: bold;
            margin-bottom: 10px;
            color: inherit;
        }
        
        .tool-args {
            background: rgba(0,0,0,0.1);
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            white-space: pre-wrap;
            color: inherit;
            margin-bottom: 10px;
        }
        
        .tool-result-header {
            font-weight: bold;
            margin-bottom: 10px;
            margin-top: 15px;
            color: inherit;
        }
        
        .tool-result-content {
            background: rgba(0,0,0,0.15);
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            white-space: pre-wrap;
            color: inherit;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .code-block {
            background: rgba(0,0,0,0.1);
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            margin: 10px 0;
            color: inherit;
        }
        
        .timestamp {
            position: absolute;
            top: 5px;
            right: 10px;
            font-size: 11px;
            opacity: 0.7;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: bold;
            color: #4facfe;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .message.user {
                margin-left: 5%;
            }
            
            .message.assistant {
                margin-right: 5%;
            }
        }
    """

def convert_json_to_html(json_file_path, output_file_path=None):
    """将JSON对话记录转换为HTML"""
    
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        conversation_data = json.load(f)
    
    # 如果没有指定输出文件，则使用默认名称
    if output_file_path is None:
        # output_file_path = Path(json_file_path).with_suffix('.html')
        output_file_path = json_file_path.replace('.json', '.html')
    
    # HTML模板开始
    html_start = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>对话记录可视化</title>
    <style>
{get_css_styles()}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI对话记录可视化</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>文件来源: {Path(json_file_path).name}</p>
    </div>
    
    <div class="conversation">"""
    
    # 角色标签映射
    role_labels = {
        'system': '🔧 系统',
        'user': '👤 用户',
        'assistant': '🤖 助手',
        'tool': '⚙️ 工具'
    }
    
    # 统计信息
    stats = {
        'system': 0,
        'user': 0, 
        'assistant': 0,
        'tool': 0,
        'total': len(conversation_data)
    }
    
    # 生成对话HTML
    conversation_html = []
    tool_results_map = {}
    
    # 首先构建工具结果映射
    for message in conversation_data:
        if message.get('role') == 'tool' and message.get('tool_call_id'):
            tool_results_map[message.get('tool_call_id')] = message.get('content', '')
    
    # 处理消息时跳过已处理的工具响应
    processed_tool_results = set()
    
    for i, message in enumerate(conversation_data):
        role = message.get('role', 'unknown')
        content = message.get('content', '')
        tool_calls = message.get('tool_calls', [])
        tool_call_id = message.get('tool_call_id', '')
        
        # 如果是工具响应且已经被处理过，跳过
        if role == 'tool' and tool_call_id in processed_tool_results:
            continue
            
        # 统计角色消息数量
        if role in stats:
            stats[role] += 1
        
        # 构建消息HTML
        message_html = f'<div class="message {role}">'
        message_html += f'<div class="timestamp">#{i+1}</div>'
        message_html += f'<div class="role-label">{role_labels.get(role, role.upper())}</div>'
        
        # 处理消息内容
        if content and role != 'tool':  # 工具消息的内容会在工具调用框中显示
            message_html += f'<div class="message-content">{format_message_content(content)}</div>'
        
        # 处理工具调用，包含对应的工具结果
        if tool_calls:
            for tool_call in tool_calls:
                tool_call_id = tool_call.get('id')
                tool_result_content = tool_results_map.get(tool_call_id) if tool_call_id else None
                if tool_call_id and tool_result_content:
                    processed_tool_results.add(tool_call_id)
                message_html += format_tool_call(tool_call, tool_result_content)
        
        # 如果是单独的工具响应（没有对应的工具调用），仍然显示
        if role == 'tool' and tool_call_id and tool_call_id not in processed_tool_results:
            message_html += format_tool_result(content)
            processed_tool_results.add(tool_call_id)
        
        message_html += '</div>'
        conversation_html.append(message_html)
    
    # HTML结束部分
    html_end = f"""
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-number">{stats['total']}</div>
            <div class="stat-label">消息总数</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{stats['system']}</div>
            <div class="stat-label">系统消息</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{stats['user']}</div>
            <div class="stat-label">用户消息</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{stats['assistant']}</div>
            <div class="stat-label">助手消息</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">{stats['tool']}</div>
            <div class="stat-label">工具响应</div>
        </div>
    </div>
</body>
</html>"""
    
    # 组合完整的HTML
    final_html = html_start + '\n'.join(conversation_html) + html_end
    
    # 写入HTML文件到原目录
    # with open(os.path.join(os.path.dirname(json_file_path), output_file_path), 'w', encoding='utf-8') as f:
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"✅ HTML文件已生成: {output_file_path}")
    print(f"📊 统计信息: 总消息数 {stats['total']}, 用户消息 {stats['user']}, 助手消息 {stats['assistant']}, 工具消息 {stats['tool']}")
    
    return output_file_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将JSON对话记录转换为HTML可视化')
    parser.add_argument('json_file', help='输入的JSON文件路径')
    parser.add_argument('-o', '--output', help='输出HTML文件路径（可选）')
    
    args = parser.parse_args()
    
    if not Path(args.json_file).exists():
        print(f"❌ 错误: 文件 '{args.json_file}' 不存在")
        return
    
    try:
        convert_json_to_html(args.json_file, args.output)
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()