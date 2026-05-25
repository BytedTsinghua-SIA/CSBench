#!/usr/bin/env python3
"""
Visualization tool for conversation history.
Generates an HTML file from conversation_history.json in the same directory.

Usage:
    python scripts/visualize_conversation.py <path_to_conversation_history.json>
    
Example:
    python scripts/visualize_conversation.py logs/20251106_054514_code_act_agent_cs000007-stanford-cs110-six-degrees/conversation_history.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import html


def escape_html(text):
    """Escape HTML special characters."""
    return html.escape(str(text))


def format_tool_call(tool_call):
    """Format a tool call object into HTML."""
    if isinstance(tool_call, dict):
        name = tool_call.get('function', {}).get('name', 'unknown')
        args = tool_call.get('function', {}).get('arguments', '{}')
        try:
            args_obj = json.loads(args) if isinstance(args, str) else args
            args_formatted = json.dumps(args_obj, indent=2)
        except:
            args_formatted = str(args)
        
        return f"""
        <div class="tool-call">
            <div class="tool-name">🔧 {escape_html(name)}</div>
            <pre class="tool-args">{escape_html(args_formatted)}</pre>
        </div>
        """
    return f'<div class="tool-call">{escape_html(str(tool_call))}</div>'


def format_message(msg, index):
    """Format a single message into HTML."""
    role = msg.get('role', 'unknown')
    content = msg.get('content', '')
    tool_calls = msg.get('tool_calls', [])
    tool_call_id = msg.get('tool_call_id', '')
    
    # Role-specific styling
    role_class = f"message-{role}"
    role_icon = {
        'system': '⚙️',
        'user': '👤',
        'assistant': '🤖',
        'tool': '🔨'
    }.get(role, '❓')
    
    # Format content
    content_html = ''
    if content:
        # Truncate very long content for readability
        if len(content) > 10000:
            content_display = content[:5000] + '\n\n... [truncated] ...\n\n' + content[-5000:]
        else:
            content_display = content
        content_html = f'<pre class="message-content">{escape_html(content_display)}</pre>'
    
    # Format tool calls
    tool_calls_html = ''
    if tool_calls:
        tool_calls_html = '<div class="tool-calls-section">'
        for tc in tool_calls:
            tool_calls_html += format_tool_call(tc)
        tool_calls_html += '</div>'
    
    # Tool call ID for tool responses
    tool_id_html = ''
    if tool_call_id:
        tool_id_html = f'<div class="tool-call-id">↩️ Response to: {escape_html(tool_call_id)}</div>'
    
    return f"""
    <div class="message {role_class}" id="msg-{index}">
        <div class="message-header">
            <span class="role-icon">{role_icon}</span>
            <span class="role-name">{escape_html(role.upper())}</span>
            <span class="message-index">#{index}</span>
        </div>
        {tool_id_html}
        {content_html}
        {tool_calls_html}
    </div>
    """


def generate_html(conversation_data, output_path):
    """Generate HTML visualization from conversation data."""
    
    # Count messages by role
    role_counts = {}
    for msg in conversation_data:
        role = msg.get('role', 'unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    # Generate statistics
    stats_html = '<div class="stats">'
    stats_html += f'<div class="stat-item">Total Messages: <strong>{len(conversation_data)}</strong></div>'
    for role, count in sorted(role_counts.items()):
        stats_html += f'<div class="stat-item">{role.capitalize()}: <strong>{count}</strong></div>'
    stats_html += '</div>'
    
    # Generate messages HTML
    messages_html = ''
    for i, msg in enumerate(conversation_data):
        messages_html += format_message(msg, i)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Complete HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Conversation History Visualization</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .stat-item {{
            padding: 10px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-item strong {{
            color: #667eea;
            font-size: 1.2em;
        }}
        
        .messages {{
            padding: 20px;
        }}
        
        .message {{
            margin-bottom: 20px;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .message:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .message-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .role-icon {{
            font-size: 1.5em;
        }}
        
        .role-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .message-index {{
            margin-left: auto;
            background: #e9ecef;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9em;
            color: #495057;
        }}
        
        .message-system {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}
        
        .message-user {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}
        
        .message-assistant {{
            background: #d4edda;
            border-left: 4px solid #28a745;
        }}
        
        .message-tool {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }}
        
        .message-content {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            margin-top: 10px;
        }}
        
        .tool-calls-section {{
            margin-top: 15px;
        }}
        
        .tool-call {{
            background: #e7f3ff;
            border: 1px solid #b3d9ff;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }}
        
        .tool-name {{
            font-weight: bold;
            color: #0056b3;
            margin-bottom: 8px;
        }}
        
        .tool-args {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }}
        
        .tool-call-id {{
            background: #fff3cd;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #856404;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 2px solid #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗨️ Conversation History</h1>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>
        
        {stats_html}
        
        <div class="messages">
            {messages_html}
        </div>
        
        <div class="footer">
            <p>Generated by CSBench Conversation Visualizer</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML visualization generated: {output_path}")
    print(f"📊 Total messages: {len(conversation_data)}")
    print(f"📂 Open the file in your browser to view the conversation")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/visualize_conversation.py <path_to_conversation_history.json>")
        print("\nExample:")
        print("  python scripts/visualize_conversation.py logs/20251106_054514_code_act_agent_cs000007-stanford-cs110-six-degrees/conversation_history.json")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    
    if not input_path.exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix == '.json':
        print(f"⚠️  Warning: File does not have .json extension: {input_path}")
    
    # Generate output path in the same directory
    output_path = input_path.parent / f"{input_path.stem}.html"
    
    try:
        # Load conversation data
        print(f"📖 Reading conversation from: {input_path}")
        with open(input_path, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        
        if not isinstance(conversation_data, list):
            print("❌ Error: conversation_history.json should contain a list of messages")
            sys.exit(1)
        
        # Generate HTML
        generate_html(conversation_data, output_path)
        
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
