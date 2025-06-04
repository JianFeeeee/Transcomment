# Translated by AI
import httpx
import os
import io
import re
import requests
import time
import datetime
import json
import sys
import configparser
import chardet
from openai import OpenAI
from pathlib import Path

# Create ConfigParser object
# 
# 创建 ConfigParser 对象
config = configparser.ConfigParser()

# Get current script path
# 
# 获取当前脚本路径
current_file = Path(__file__).resolve()

# Get project root directory
# 
# 获取项目根目录
project_root = current_file.parent.parent

# Build configuration file path using Path
# 
# 使用Path构建配置文件路径
config_path = project_root / "config" / "config.ini"
config.read(str(config_path))  # Convert to string for compatibility
# 
# 转换为字符串以兼容
http_client = httpx.Client(transport=httpx.HTTPTransport())

client = OpenAI(
    api_key=config["APIKEY"]["apikey"],
    base_url="https://api.siliconflow.cn/v1",
    http_client=http_client  # 显式禁用代理
)

def get_encoding(file):
    # Read file in binary mode to detect encoding
# 
# 以二进制模式读取文件以检测编码
    with open(file, 'rb') as f:
        data = f.read()
        return chardet.detect(data)['encoding']

def ai_tr(message, module, i=0):
    try:
        response = client.chat.completions.create(  
            model=module[i],  
            messages=[    
                {"role": "system", "content": "你是一个翻译家，你要为接下来的所有输入给出对应的中文翻译，注意保留原有的符号，注意不要给出解释只给出翻译即可"},  
                {"role": "user", "content": message}  
            ],  
            temperature=0.7,  
            max_tokens=4096
        )
        print(f"Token usage: {response.usage.total_tokens}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in translation: {str(e)}")
        if i < len(module) - 1:
            print(f"Trying next model: {module[i+1]}")
            return ai_tr(message, module, i+1)
        else:
            print("All models busy, waiting 10 seconds before retrying")
            time.sleep(10)
            return ai_tr(message, module, 0)

def is_translated(file_path):
    """Check if file has been translated"""
    try:
        with open(file_path, 'r', encoding=get_encoding(file_path)) as file:
            # Check first 50 lines for translation marker
# 
# 检查前50行是否有翻译标记
            for i, line in enumerate(file):
                if i > 50:  # Check only first 50 lines
# 
# 仅检查前50行
                    break
                # Check for marker based on file type
# 
# 根据文件类型检查标记
                if file_path.endswith('.py'):
                    if "# Translated by AI" in line:
# 
# 由AI翻译" 在行中
                        return True
                elif file_path.endswith(('.c', '.h', '.java','.js','.ts','.cpp')):
                    if "// Translated by AI" in line:
                        return True
    except Exception as e:
        print(f"Error checking translation marker: {e}")
    return False

def add_translation_marker(file_path):
    """Add translation marker at file beginning"""
    try:
        with open(file_path, 'r', encoding=get_encoding(file_path)) as file:
            content = file.read()
            
        # Determine marker based on file type
# 
# 根据文件类型确定标记
        if file_path.endswith('.py'):
            marker = "# Translated by AI\n\n"
# 
# 由AI翻译\n\n"
        elif file_path.endswith(('.c', '.h', '.java','.js','.ts','.cpp')):
            marker = "// Translated by AI\n\n"
        else:
            marker = "// Translated by AI\n\n"  # Default to C-style marker
# 
# 默认为C风格标记
        
        # Add marker at beginning of file
# 
# 在文件开头添加标记
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(marker + content)
    except Exception as e:
        print(f"Error adding translation marker: {e}")

def extract_comments(file_path):
    """Extract comments from file"""
    with open(file_path, 'r', encoding=get_encoding(file_path)) as file:
        content = file.read()
    
    # Select regex pattern based on file type
# 
# 根据文件类型选择正则表达式模式
    if file_path.endswith('.py'):
        # 匹配Python注释的正则表达式（单行注释 + 特定条件的三引号注释）
        pattern = r'''
            (?:                     # 开始非捕获分组
                ^                   # 条件1: 行首
                | (?<=[\s)\]}])     # 条件2: 前一个字符是空格/右括号/右方括号/右大括号
            )
            (\"\"\"|\'\'\')         # 匹配三引号（单引号或双引号）
            .*?                     # 非贪婪匹配任意内容（包括换行）
            \1                      # 匹配相同的结束三引号
            |                       # 或
            \#.*$                   # 匹配单行注释（从#到行尾）
        '''
        comment_pattern = re.compile(pattern, re.VERBOSE | re.DOTALL | re.MULTILINE)
    elif file_path.endswith(('.c', '.h', '.java','.js','.ts','.cpp')):
        # C/C++/Java: single and multi-line comments
        comment_pattern = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    else:
        # Default to C/C++ style
        comment_pattern = re.compile(r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)

    return comment_pattern.finditer(content), content

def add_translated_comments(file_path, module):
    """Add translated comments to file"""
    # Skip if file already translated
# 
# 如果文件已经被翻译则跳过
    if is_translated(file_path):
        print(f"Skipping {file_path} (already translated)")
        return
    
    comments, content = extract_comments(file_path)
    if not comments:
        print(f"No comments found in {file_path}")
        return
        
    try:
        with open(file_path, 'r', encoding=get_encoding(file_path)) as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    comment_positions = []

    for match in comments:
        start = match.start()
        end = match.end()
        comment_text = match.group(0)

        # Calculate line number (1-based)
# 
# 计算行号（1-based）
        line_num = content[:start].count('\n') + 1

        # Calculate number of lines the comment spans
# 
# 计算注释跨越的行数
        num_lines = comment_text.count('\n')

        # Insert after the comment ends
# 
# 在注释结束后插入
        insertion_line = line_num + num_lines

        comment_positions.append((start, insertion_line, comment_text))

    # Process from last to first to avoid line number offset issues
# 
# 从后往前处理，以避免行号偏移问题
    comment_positions.sort(key=lambda x: -x[0])

    for start, insertion_line, comment in comment_positions:
        comment_text = comment.strip()
        # Skip empty comments
# 
# 跳过空评论
        if not comment_text:
            continue
            
        # Translate comment
# 
# 翻译评论
        print(f"Translating comment: {comment_text[:50]}...")
        translated = ai_tr(comment_text, module)
        if not translated:
            continue
            
        # Add appropriate comment marker
# 
# 添加适当的注释标记
        if file_path.endswith('.py'):
            translated = f"{translated}"
# 
# {翻译}
        elif file_path.endswith(('.c', '.h', '.java','.js','.ts','.cpp')):
            translated = f"{translated}"
        
        lines.insert(insertion_line, f'{translated}\n')

    # Write back to file
# 
# 写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    # Add translation marker
# 
# 添加翻译标记
    add_translation_marker(file_path)
    print(f"Added translation marker to {file_path}")

def process_file(file, module):
    """Process a single file"""
    if file.endswith(('.c', '.h', '.py', '.java')):
        print(f'Processing: {file}')
        add_translated_comments(file, module)

if __name__ == '__main__':
    if os.name == "nt":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Get current script path
# 
# 获取当前脚本路径
    current_file = Path(__file__).resolve()

    # Get project root directory
# 
# 获取项目根目录
    project_root = current_file.parent.parent

    # Build JSON configuration path
# 
# 构建JSON配置路径
    json_path = project_root / "config" / "models.json"

    # Read and parse JSON file
# 
# 读取并解析JSON文件
    try:
        with open(str(json_path), "r", encoding="utf-8") as f:
            module = json.load(f)
            print("Models in use:")
            print(module)
    except FileNotFoundError:
        print(f"Error: JSON file {json_path} not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_path}")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)
        
    process_file(sys.argv[1], module)
    print(f"{sys.argv[1]} processing completed")
    print(f"Timestamp: {datetime.datetime.today()}")
