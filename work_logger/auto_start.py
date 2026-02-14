#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDE启动自动触发器 - 修复版

功能：
    在IDE启动时触发工作记录流程
    - 自动检测当前工作目录
    - 在当前项目创建记录
    - 避免重复触发
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# 使用当前工作目录（用户项目目录）
WORK_DIR = Path(os.getcwd()).resolve()
MIND_DIR = WORK_DIR / "mind"
DAILY_DIR = MIND_DIR / "daily"


def ensure_directories():
    """确保目录存在"""
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_state_file():
    """获取状态文件路径"""
    return MIND_DIR / ".work_logger_state.json"


def load_state():
    """加载状态"""
    import json
    state_file = get_state_file()
    if state_file.exists():
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'last_morning_date': None,
        'last_evening_date': None,
    }


def save_state(state):
    """保存状态"""
    import json
    ensure_directories()
    state_file = get_state_file()
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def should_do_morning():
    """检查是否应该做晨间计划"""
    state = load_state()
    today = datetime.now().strftime('%Y-%m-%d')
    return state.get('last_morning_date') != today


def should_do_evening():
    """检查是否应该做晚间回顾"""
    state = load_state()
    today = datetime.now().strftime('%Y-%m-%d')
    return state.get('last_evening_date') != today


def mark_morning_done():
    """标记晨间计划已完成"""
    state = load_state()
    state['last_morning_date'] = datetime.now().strftime('%Y-%m-%d')
    save_state(state)


def mark_evening_done():
    """标记晚间回顾已完成"""
    state = load_state()
    state['last_evening_date'] = datetime.now().strftime('%Y-%m-%d')
    save_state(state)


def get_greeting_and_action():
    """获取问候语和对应的动作"""
    now = datetime.now()
    hour = now.hour
    weekday = now.strftime("%A")
    date_str = now.strftime("%Y-%m-%d")
    
    # 早上 6-12 点：晨间计划
    if 6 <= hour < 12:
        if not should_do_morning():
            return f"[完成] 今天已完成晨间计划，开始工作吧！", None
            
        greeting = f"""
[早晨] 早上好！今天是 {date_str} {weekday}

检测到晨间时间，我已为您准备好今日计划模板。

您可以直接告诉我：
- 今天的主要任务
- 预期完成的目标
- 可能遇到的风险

我会帮您记录并跟踪全天工作。
"""
        
        def morning_action():
            # 使用交互式提问
            from interactive_bot import morning_interactive
            morning_interactive()
            mark_morning_done()
        
        return greeting, morning_action
    
    # 工作时间 12-21 点：工作跟踪
    elif 12 <= hour < 21:
        greeting = f"""
[工作] 您好！现在是工作时间

工作目录: {WORK_DIR}

我会自动检测文件变更和工作活动。

需要我做什么？
- 说"做计划" - 生成今日计划
- 说"跟踪工作" - 手动触发工作跟踪
- 说"做回顾" - 生成今日回顾
- 或者直接开始工作，我会自动记录
"""
        
        def track_action():
            # 使用工作跟踪器
            from session_tracker import update_today_log
            update_today_log()
        
        return greeting, track_action
    
    # 晚上 21-23 点：晚间回顾
    elif 21 <= hour < 23:
        if not should_do_evening():
            return f"[完成] 今天已完成晚间回顾，早点休息！", None
            
        greeting = f"""
[晚间] 晚上好！今天工作辛苦了

检测到晚间时间，是时候做今日回顾了。

我可以帮您：
- 总结今日完成的任务
- 记录遇到的问题和解决方案
- 整理经验教训
- 列出技术债务

让我们开始回顾吧？
"""
        
        def evening_action():
            # 使用交互式提问
            from interactive_bot import evening_interactive
            evening_interactive()
            mark_evening_done()
        
        return greeting, evening_action
    
    # 深夜 23-6 点：休息提醒
    else:
        greeting = f"""
[深夜] 夜深了，该休息了

现在是 {hour}:00，建议您保存工作并休息。

如果还有紧急任务需要处理，我可以：
- 快速记录当前进度
- 生成明日待办清单
- 或者只是陪您完成最后的工作

注意身体，早点休息！
"""
        return greeting, None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Work Logger 自动启动')
    parser.add_argument('--manual', action='store_true', help='手动模式')
    parser.add_argument('--morning', action='store_true', help='强制晨间计划')
    parser.add_argument('--evening', action='store_true', help='强制晚间回顾')
    parser.add_argument('--track', action='store_true', help='强制工作跟踪')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Work Logger 自动启动")
    print(f"   工作目录: {WORK_DIR}")
    print("=" * 60)
    
    greeting, action = get_greeting_and_action()
    print(greeting)
    
    if action:
        print("\n正在执行相应动作...")
        print("-" * 60)
        try:
            action()
        except Exception as e:
            print(f"[错误] 执行出错: {e}")
    else:
        print("\n无需执行动作")
    
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
