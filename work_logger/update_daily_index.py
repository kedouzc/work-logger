#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新 mind/daily/README.md 索引

功能：
    自动扫描 mind/daily/ 目录下的所有工作记录文件
    更新 README.md 中的索引表格

用法：
    python scripts/update_daily_index.py
    python scripts/update_daily_index.py --watch  # 持续监控
"""

import os
import re
import argparse
from datetime import datetime
from pathlib import Path


def extract_metadata(file_path):
    """从markdown文件提取元数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取YAML front matter
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None
        
        metadata = match.group(1)
        
        # 解析元数据
        data = {}
        for line in metadata.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 处理数组格式 [tag1, tag2]
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                
                data[key] = value
        
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def get_main_task(content):
    """提取主要任务（从第一个任务标题）"""
    # 查找任务分解部分
    task_match = re.search(r'### 任务1：(.+?)(?:\n|$)', content)
    if task_match:
        return task_match.group(1).strip()
    
    # 备选：查找第一个##标题
    title_match = re.search(r'^## (.+?)(?:\n|$)', content, re.MULTILINE)
    if title_match:
        return title_match.group(1).strip()
    
    return "待补充"


def get_status(content):
    """判断记录状态"""
    has_plan = '## 任务分解' in content
    has_review = '启示与教训' in content or '## 明日待办' in content
    
    if has_plan and has_review:
        return '✅ 完成'
    elif has_plan:
        return '📝 已计划'
    else:
        return '⏳ 待开始'


def scan_daily_files(daily_dir):
    """扫描daily目录下的所有记录文件"""
    files = []
    
    for file_path in daily_dir.glob('*.md'):
        if file_path.name == 'README.md' or file_path.name == 'TEMPLATE.md':
            continue
        
        # 解析文件名 YYYY-MM-DD.md
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})\.md', file_path.name)
        if not match:
            continue
        
        year, month, day = match.groups()
        date_str = f"{year}-{month}-{day}"
        
        # 提取元数据
        metadata = extract_metadata(file_path)
        
        # 读取内容获取任务和状态
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        weekday = metadata.get('weekday', '') if metadata else ''
        tags = metadata.get('tags', []) if metadata else []
        main_task = get_main_task(content)
        status = get_status(content)
        
        files.append({
            'date': date_str,
            'weekday': weekday,
            'main_task': main_task,
            'tags': tags,
            'status': status,
            'filename': file_path.name
        })
    
    # 按日期倒序排列
    files.sort(key=lambda x: x['date'], reverse=True)
    
    return files


def generate_index_content(files):
    """生成索引内容"""
    lines = [
        "# 每日工作记录索引",
        "",
        "> 按日期归档的每日工作记录",
        "",
        "---",
        "",
        "## 2026年",
        "",
        "### 2月",
        "",
        "| 日期 | 星期 | 主要任务 | 标签 | 状态 |",
        "|------|------|----------|------|------|",
    ]
    
    for file_info in files:
        date = file_info['date']
        weekday = file_info['weekday']
        main_task = file_info['main_task'][:30] + '...' if len(file_info['main_task']) > 30 else file_info['main_task']
        tags = ', '.join(file_info['tags'][:3]) if file_info['tags'] else ''
        status = file_info['status']
        filename = file_info['filename']
        
        lines.append(f"| [{date}]({filename}) | {weekday} | {main_task} | {tags} | {status} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## 记录规范",
        "",
        "### 文件名格式",
        "",
        "```",
        "YYYY-MM-DD.md",
        "```",
        "",
        "### 文件头模板",
        "",
        "```markdown",
        "---",
        "date: YYYY-MM-DD",
        "weekday: 周X",
        "author: developer",
        "tags: [tag1, tag2, tag3]",
        "session: SESSION_名称",
        "---",
        "```",
        "",
        "### 内容结构",
        "",
        "1. **今日概览**：关键指标统计",
        "2. **任务分解**：",
        "   - 面临的主要问题",
        "   - 解决过程（节点表格）",
        "   - 结果",
        "   - 启示与教训",
        "3. **技术债务清单**：待清理的文件",
        "4. **关联文档**：相关ADR、经验教训",
        "5. **明日待办**：后续任务",
        "",
        "---",
        "",
        "## 标签说明",
        "",
        "| 标签 | 含义 |",
        "|------|------|",
        "| file-structure | 文件结构重构 |",
        "| path-resolver | 路径解析器 |",
        "| quality-bot | 质检机器人 |",
        "| policy-transpilation | 政策转译 |",
        "| unit-conversion | 单位转换 |",
        "| schema-validation | Schema验证 |",
        "| data-engine | 数据引擎 |",
        "| settlement | 结算体系 |",
        "| optimization | 优化求解 |",
        "",
        "---",
        "",
        "## 生成新记录",
        "",
        "使用脚本自动生成：",
        "",
        "```bash",
        "python ../scripts/generate_daily_log.py",
        "```",
        "",
        "或手动复制模板：",
        "",
        "```bash",
        "cp TEMPLATE.md 2026-02-14.md",
        "```",
        "",
        "---",
        "",
        f"> 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ])
    
    return '\n'.join(lines)


def update_index():
    """更新索引文件"""
    # 从 scripts/work_logger/ 向上两级到 refactored_models/
    daily_dir = Path(__file__).parent.parent.parent / 'mind' / 'daily'
    readme_path = daily_dir / 'README.md'
    
    # 扫描文件
    files = scan_daily_files(daily_dir)
    
    # 生成内容
    content = generate_index_content(files)
    
    # 写入文件
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 索引已更新：{readme_path}")
    print(f"   共 {len(files)} 条记录")


def watch_mode():
    """监控模式"""
    import time
    
    print("👀 监控模式已启动，按 Ctrl+C 停止")
    print("   每30秒检查一次文件变化")
    
    daily_dir = Path(__file__).parent.parent.parent / 'mind' / 'daily'
    last_mtime = {}
    
    try:
        while True:
            changed = False
            
            for file_path in daily_dir.glob('*.md'):
                if file_path.name == 'README.md':
                    continue
                
                current_mtime = file_path.stat().st_mtime
                
                if file_path.name not in last_mtime:
                    last_mtime[file_path.name] = current_mtime
                    changed = True
                elif last_mtime[file_path.name] != current_mtime:
                    last_mtime[file_path.name] = current_mtime
                    changed = True
            
            if changed:
                print(f"\n📝 检测到文件变化，更新索引...")
                update_index()
            
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n👋 监控已停止")


def main():
    parser = argparse.ArgumentParser(
        description='自动更新每日工作记录索引'
    )
    
    parser.add_argument(
        '--watch',
        action='store_true',
        help='监控模式：持续监控文件变化并自动更新'
    )
    
    args = parser.parse_args()
    
    if args.watch:
        watch_mode()
    else:
        update_index()


if __name__ == '__main__':
    main()
