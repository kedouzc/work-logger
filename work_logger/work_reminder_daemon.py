#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作提醒守护进程

功能：
    在后台运行，定时检查并提醒工作记录
    - 避免IDE重启时重复触发
    - 22点准时提醒晚间回顾
    - 支持手动触发

用法：
    python scripts/work_reminder_daemon.py --start    # 启动守护进程
    python scripts/work_reminder_daemon.py --stop     # 停止守护进程
    python scripts/work_reminder_daemon.py --status   # 查看状态
    python scripts/work_reminder_daemon.py --once     # 运行一次（用于IDE启动）
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import sys
import os
import time
import json
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path

# ==============================================================================
# 路径处理
# ==============================================================================
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ==============================================================================
# 常量定义
# ==============================================================================
PID_FILE = project_root / "mind" / ".work_reminder.pid"
STATE_FILE = project_root / "mind" / ".work_reminder_state.json"
EVENING_REMINDER_HOUR = 22  # 晚上22点提醒
CHECK_INTERVAL = 60  # 每分钟检查一次


class WorkReminderState:
    """工作提醒状态管理"""
    
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self):
        """加载状态"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_morning_date': None,
            'last_evening_date': None,
            'last_ide_start': None,
            'ide_session_count': 0
        }
    
    def _save_state(self):
        """保存状态"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def should_do_morning(self):
        """检查是否应该做晨间计划"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.state.get('last_morning_date') != today
    
    def should_do_evening(self):
        """检查是否应该做晚间回顾"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.state.get('last_evening_date') != today
    
    def mark_morning_done(self):
        """标记晨间计划已完成"""
        self.state['last_morning_date'] = datetime.now().strftime('%Y-%m-%d')
        self._save_state()
    
    def mark_evening_done(self):
        """标记晚间回顾已完成"""
        self.state['last_evening_date'] = datetime.now().strftime('%Y-%m-%d')
        self._save_state()
    
    def record_ide_start(self):
        """记录IDE启动"""
        now = datetime.now()
        self.state['last_ide_start'] = now.isoformat()
        self.state['ide_session_count'] = self.state.get('ide_session_count', 0) + 1
        self._save_state()
    
    def is_ide_restart(self):
        """
        检查是否是IDE重启（5分钟内再次启动）
        用于避免重启时重复触发
        """
        last_start = self.state.get('last_ide_start')
        if not last_start:
            return False
        
        try:
            last_time = datetime.fromisoformat(last_start)
            time_diff = datetime.now() - last_time
            return time_diff < timedelta(minutes=5)
        except:
            return False


class WorkReminderDaemon:
    """工作提醒守护进程"""
    
    def __init__(self):
        self.state = WorkReminderState()
        self.running = False
        self.thread = None
    
    def start(self):
        """启动守护进程"""
        if self.is_running():
            print("⚠️  守护进程已经在运行")
            return False
        
        # 写入PID文件
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        self.running = True
        print("🚀 工作提醒守护进程已启动")
        print(f"   将在每天 {EVENING_REMINDER_HOUR}:00 提醒晚间回顾")
        print("   按 Ctrl+C 停止")
        
        try:
            self._run_loop()
        except KeyboardInterrupt:
            self.stop()
        
        return True
    
    def stop(self):
        """停止守护进程"""
        self.running = False
        if PID_FILE.exists():
            PID_FILE.unlink()
        print("\n✅ 守护进程已停止")
    
    def is_running(self):
        """检查守护进程是否正在运行"""
        if not PID_FILE.exists():
            return False
        
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            # 检查进程是否存在
            os.kill(pid, 0)
            return True
        except:
            # 进程不存在，删除过期的PID文件
            if PID_FILE.exists():
                PID_FILE.unlink()
            return False
    
    def _run_loop(self):
        """主循环"""
        while self.running:
            now = datetime.now()
            
            # 检查是否是22点整（±1分钟）
            if now.hour == EVENING_REMINDER_HOUR and now.minute == 0:
                if self.state.should_do_evening():
                    self._trigger_evening_reminder()
            
            # 每分钟检查一次
            time.sleep(CHECK_INTERVAL)
    
    def _trigger_evening_reminder(self):
        """触发晚间回顾提醒"""
        print("\n" + "=" * 60)
        print("🌙 晚上好！到时间做今日回顾了")
        print("=" * 60)
        
        # 显示通知（如果可能）
        try:
            self._show_notification("工作提醒", "到时间做今日回顾了！")
        except:
            pass
        
        # 运行晚间回顾
        from scripts.orchestrator import WorkflowOrchestrator
        orchestrator = WorkflowOrchestrator()
        orchestrator.evening_routine()
        
        self.state.mark_evening_done()
    
    def _show_notification(self, title, message):
        """显示系统通知"""
        if sys.platform == 'win32':
            # Windows通知
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10)
            except:
                pass
        elif sys.platform == 'darwin':
            # macOS通知
            os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
        else:
            # Linux通知
            os.system(f"notify-send '{title}' '{message}'")
    
    def run_once(self):
        """
        运行一次（用于IDE启动时）
        避免重启时重复触发
        """
        # 记录IDE启动
        self.state.record_ide_start()
        
        # 检查是否是重启（5分钟内再次启动）
        if self.state.is_ide_restart():
            print("🔄 检测到IDE重启，跳过计划触发")
            return
        
        now = datetime.now()
        hour = now.hour
        
        # 今天首次启动IDE
        if self.state.should_do_morning():
            # 还没有做过晨间计划
            if hour >= EVENING_REMINDER_HOUR:
                # 晚上10点后打开，直接做回顾
                if self.state.should_do_evening():
                    print("🌙 晚上好！正在启动晚间回顾...")
                    from scripts.orchestrator import WorkflowOrchestrator
                    orchestrator = WorkflowOrchestrator()
                    orchestrator.evening_routine()
                    self.state.mark_evening_done()
            else:
                # 其他时间，做晨间计划
                print("🌅 早上好！正在启动晨间计划...")
                from scripts.orchestrator import WorkflowOrchestrator
                orchestrator = WorkflowOrchestrator()
                orchestrator.morning_routine()
                self.state.mark_morning_done()
        else:
            # 已经做过计划了，静默跟踪
            print("📊 工作跟踪模式")
            try:
                from scripts.session_tracker import SessionTracker
                tracker = SessionTracker()
                activities = tracker.detect_activities()
                tracker.update_today_log(activities)
                print("✅ 工作活动已自动记录")
            except Exception as e:
                print(f"⚠️  跟踪失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='工作提醒守护进程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用场景:
  1. 启动守护进程（后台运行，22点准时提醒）
     python scripts/work_reminder_daemon.py --start
     
  2. IDE启动时运行一次（避免重复触发）
     python scripts/work_reminder_daemon.py --once
     
  3. 停止守护进程
     python scripts/work_reminder_daemon.py --stop
     
  4. 查看状态
     python scripts/work_reminder_daemon.py --status
        """
    )
    
    parser.add_argument(
        '--start',
        action='store_true',
        help='启动守护进程（后台运行）'
    )
    
    parser.add_argument(
        '--stop',
        action='store_true',
        help='停止守护进程'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='查看守护进程状态'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='运行一次（用于IDE启动）'
    )
    
    args = parser.parse_args()
    
    daemon = WorkReminderDaemon()
    
    if args.start:
        daemon.start()
    elif args.stop:
        daemon.stop()
    elif args.status:
        if daemon.is_running():
            print("✅ 守护进程正在运行")
        else:
            print("⏹️  守护进程未运行")
        
        # 显示详细状态
        state = WorkReminderState()
        print(f"\n📅 今天: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"   - 晨间计划: {'✅ 已完成' if not state.should_do_morning() else '⏳ 待完成'}")
        print(f"   - 晚间回顾: {'✅ 已完成' if not state.should_do_evening() else '⏳ 待完成'}")
        print(f"   - IDE启动次数: {state.state.get('ide_session_count', 0)}")
    elif args.once:
        daemon.run_once()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
