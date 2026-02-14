#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work Logger 启动器

功能：
    1. 启动守护进程（22点提醒）
    2. 执行自动启动（晨间计划/工作跟踪/晚间回顾）
    3. 后台静默跟踪

用法：
    python launch.py              # 完整启动
    python launch.py --daemon     # 仅启动守护进程
    python launch.py --once       # 仅运行一次（用于IDE启动）
"""

import subprocess
import sys
import time
from pathlib import Path

# work_logger 目录
WORK_LOGGER_DIR = Path(__file__).parent / "work_logger"


def start_daemon():
    """启动守护进程"""
    daemon_script = WORK_LOGGER_DIR / "work_reminder_daemon.py"
    
    # 先检查状态
    result = subprocess.run(
        [sys.executable, str(daemon_script), "--status"],
        capture_output=True,
        text=True
    )
    
    if "守护进程未运行" in result.stdout:
        print("[启动] 启动守护进程...")
        subprocess.Popen(
            [sys.executable, str(daemon_script), "--start"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        time.sleep(2)
        print("[完成] 守护进程已启动")
    else:
        print("[完成] 守护进程已在运行")


def run_auto_start():
    """运行自动启动"""
    auto_start_script = WORK_LOGGER_DIR / "auto_start.py"
    
    print("[启动] 执行自动启动...")
    result = subprocess.run(
        [sys.executable, str(auto_start_script)],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Work Logger 启动器')
    parser.add_argument('--daemon', action='store_true', help='仅启动守护进程')
    parser.add_argument('--once', action='store_true', help='仅运行一次')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Work Logger 启动器")
    print("=" * 60)
    
    if args.daemon:
        start_daemon()
    elif args.once:
        run_auto_start()
    else:
        # 完整启动
        start_daemon()
        print()
        run_auto_start()
        print()
        print("[完成] 启动完成！")
        print("   - 守护进程运行中（22点提醒）")
        print("   - 自动启动已完成")
        print("   - 工作跟踪已激活")
    
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
