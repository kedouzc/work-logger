#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式工作记录机器人 - 配置驱动版本

功能：
    通过配置文件驱动，逐个提问收集用户的工作信息
    修改 config/questions.yaml 即可自定义问题，无需修改代码
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path

# 尝试导入 yaml，如果没有则使用标准库 json
from pathlib import Path

# 使用当前工作目录
WORK_DIR = Path(os.getcwd()).resolve()
MIND_DIR = WORK_DIR / "mind"
DAILY_DIR = MIND_DIR / "daily"

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent / "config"
QUESTIONS_FILE = CONFIG_DIR / "questions.yaml"


def load_questions_config():
    """
    加载问题配置文件
    
    Returns:
        dict: 配置数据
    """
    import yaml
    
    if not QUESTIONS_FILE.exists():
        print(f"[错误] 配置文件不存在: {QUESTIONS_FILE}")
        print("[提示] 使用默认配置")
        return get_default_config()
    
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[错误] 读取配置文件失败: {e}")
        print("[提示] 使用默认配置")
        return get_default_config()


def get_default_config():
    """获取默认配置（当配置文件不存在时使用）"""
    return {
        'morning': {
            'title': '晨间计划',
            'description': '让我们规划今天的工作',
            'questions': [
                {
                    'id': 'goal',
                    'text': '今天您的主要工作目标是什么？',
                    'hint': '例如：完成XX功能开发、修复YY问题',
                    'required': True
                },
                {
                    'id': 'tasks',
                    'text': '今天计划完成哪些具体任务？',
                    'hint': '请列出2-3个主要任务',
                    'required': True
                }
            ]
        },
        'evening': {
            'title': '工作回顾',
            'description': '让我们总结今天的工作',
            'questions': [
                {
                    'id': 'completed',
                    'text': '今天实际完成了哪些任务？',
                    'hint': '请列出实际完成的工作',
                    'required': True
                }
            ]
        },
        'templates': {
            'plan_filename': '{date}-plan.md',
            'review_filename': '{date}-review.md',
            'plan_template': '# {date} 工作计划\n\n## 今日目标\n\n{goal}\n\n## 主要任务\n\n{tasks}\n\n---\n*创建于 {time}*\n',
            'review_template': '# {date} 工作回顾\n\n## 今日完成任务\n\n{completed}\n\n---\n*创建于 {time}*\n'
        }
    }


def ensure_directories():
    """确保目录存在"""
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def ask_question(question_config):
    """
    提问并获取用户输入
    
    Args:
        question_config: 问题配置字典
    
    Returns:
        用户输入的内容
    """
    text = question_config.get('text', '')
    hint = question_config.get('hint', '')
    required = question_config.get('required', True)
    
    print(f"\n[问题] {text}")
    if hint:
        print(f"  提示: {hint}")
    if not required:
        print("  (可选，直接回车跳过)")
    print()
    
    while True:
        try:
            answer = input("> ").strip()
            if required and not answer:
                print("  此项为必填，请输入内容:")
                continue
            return answer
        except KeyboardInterrupt:
            print("\n[取消] 用户中断")
            return None
        except EOFError:
            # 非交互式环境（如自动启动）
            return ""


def format_tasks(tasks_text):
    """格式化任务列表"""
    lines = tasks_text.split('\n')
    formatted = []
    for i, line in enumerate(lines, 1):
        if line.strip():
            # 如果行首已经有数字，就不添加序号
            if re.match(r'^\d+\.', line.strip()):
                formatted.append(line.strip())
            else:
                formatted.append(f"{i}. {line.strip()}")
    return '\n'.join(formatted)


def generate_section(title, content):
    """生成 Markdown 章节（如果内容不为空）"""
    if not content or not content.strip():
        return ""
    return f"## {title}\n\n{content}\n\n"


def run_interactive_session(session_type, config):
    """
    运行交互式会话
    
    Args:
        session_type: 'morning' 或 'evening'
        config: 配置字典
    
    Returns:
        bool: 是否成功
    """
    session_config = config.get(session_type, {})
    title = session_config.get('title', '工作记录')
    description = session_config.get('description', '')
    questions = session_config.get('questions', [])
    templates = config.get('templates', {})
    
    # 显示标题
    print("=" * 60)
    print(f"[{session_type}] {title} - {description}")
    print("=" * 60)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    
    print(f"\n今天是 {date_str} {weekday}")
    print("我将逐个问您几个问题，请逐一回答。\n")
    
    # 收集答案
    answers = {}
    for question in questions:
        answer = ask_question(question)
        if answer is None:
            return False
        answers[question['id']] = answer
    
    # 处理特殊字段
    if 'tasks' in answers:
        answers['tasks'] = format_tasks(answers['tasks'])
    
    # 生成可选章节
    answers['challenges_section'] = generate_section('可能的风险', answers.get('challenges', ''))
    answers['problems_section'] = generate_section('遇到的问题', answers.get('problems', ''))
    answers['solutions_section'] = generate_section('解决方案', answers.get('solutions', ''))
    answers['lessons_section'] = generate_section('经验教训', answers.get('lessons', ''))
    answers['tomorrow_section'] = generate_section('明日计划', answers.get('tomorrow', ''))
    
    # 生成文档
    ensure_directories()
    
    if session_type == 'morning':
        filename_template = templates.get('plan_filename', '{date}-plan.md')
        content_template = templates.get('plan_template', get_default_plan_template())
    else:
        filename_template = templates.get('review_filename', '{date}-review.md')
        content_template = templates.get('review_template', get_default_review_template())
    
    filename = filename_template.format(date=date_str)
    output_file = DAILY_DIR / filename
    
    # 填充模板
    answers['date'] = date_str
    answers['time'] = datetime.now().strftime('%H:%M')
    content = content_template.format(**answers)
    
    output_file.write_text(content, encoding='utf-8')
    print(f"\n[完成] 已保存: {output_file}")
    return True


def get_default_plan_template():
    """获取默认计划模板"""
    return '''# {date} 工作计划

## 今日目标

{goal}

## 主要任务

{tasks}

{challenges_section}## 最高优先级

{priority}

---
*创建于 {time}*
'''


def get_default_review_template():
    """获取默认回顾模板"""
    return '''# {date} 工作回顾

## 今日完成任务

{completed}

{problems_section}{solutions_section}{lessons_section}{tomorrow_section}---
*创建于 {time}*
'''


def morning_interactive():
    """晨间计划 - 交互式提问"""
    config = load_questions_config()
    return run_interactive_session('morning', config)


def evening_interactive():
    """晚间回顾 - 交互式提问"""
    config = load_questions_config()
    return run_interactive_session('evening', config)


def main():
    """主函数"""
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        return morning_interactive()
    elif 21 <= hour < 23:
        return evening_interactive()
    else:
        print("[提示] 当前不是计划或回顾时间")
        print("  晨间计划时间: 6:00 - 12:00")
        print("  晚间回顾时间: 21:00 - 23:00")
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
