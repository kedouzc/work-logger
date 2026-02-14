#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work Logger 命令行入口

提供统一的命令行接口
"""

import sys
import argparse
from datetime import datetime

from .interactive_bot import morning_interactive, evening_interactive
from .session_tracker import update_today_log
from .work_reminder_daemon import main as daemon_main


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='Work Logger - 智能工作记录助手',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  work-logger --morning          # 运行晨间计划
  work-logger --evening          # 运行晚间回顾
  work-logger --track            # 跟踪工作
  work-logger --daemon           # 启动守护进程
  work-logger --auto             # 自动模式（根据时间选择）
        """
    )
    
    parser.add_argument(
        '--morning', '-m',
        action='store_true',
        help='运行晨间计划（交互式提问）'
    )
    
    parser.add_argument(
        '--evening', '-e',
        action='store_true',
        help='运行晚间回顾（交互式提问）'
    )
    
    parser.add_argument(
        '--track', '-t',
        action='store_true',
        help='跟踪工作（记录文件修改）'
    )
    
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='启动守护进程（22:00提醒）'
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='自动模式（根据时间自动选择功能）'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Work Logger 1.0.0'
    )
    
    args = parser.parse_args()
    
    # 如果没有参数，显示帮助
    if not any([args.morning, args.evening, args.track, args.daemon, args.auto]):
        parser.print_help()
        return 0
    
    try:
        if args.morning:
            print("[启动] 晨间计划...")
            return 0 if morning_interactive() else 1
        
        elif args.evening:
            print("[启动] 晚间回顾...")
            return 0 if evening_interactive() else 1
        
        elif args.track:
            print("[启动] 工作跟踪...")
            update_today_log()
            return 0
        
        elif args.daemon:
            print("[启动] 守护进程...")
            return daemon_main()
        
        elif args.auto:
            hour = datetime.now().hour
            if 6 <= hour < 12:
                print("[自动] 检测到晨间时间，启动晨间计划...")
                return 0 if morning_interactive() else 1
            elif 21 <= hour < 23:
                print("[自动] 检测到晚间时间，启动晚间回顾...")
                return 0 if evening_interactive() else 1
            else:
                print("[自动] 工作时间，启动跟踪...")
                update_today_log()
                return 0
        
    except KeyboardInterrupt:
        print("\n[取消] 用户中断")
        return 130
    except Exception as e:
        print(f"[错误] {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
