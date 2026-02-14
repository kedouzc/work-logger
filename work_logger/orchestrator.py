#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流编排器 - 全天自动化管理工作记录

功能：
    1. 早晨：生成今日计划（标准模式或交互模式）
    2. 全天：自动跟踪工作活动
    3. 晚上：回顾并完善记录（标准模式或交互模式）

用法：
    python scripts/work_logger/orchestrator.py --morning              # 晨间计划（标准）
    python scripts/work_logger/orchestrator.py --morning-interactive  # 晨间计划（交互式）
    python scripts/work_logger/orchestrator.py --track                # 跟踪工作
    python scripts/work_logger/orchestrator.py --evening              # 晚间回顾（标准）
    python scripts/work_logger/orchestrator.py --evening-interactive  # 晚间回顾（交互式）
    python scripts/work_logger/orchestrator.py --auto                 # 自动模式

注意：
    本脚本已合并 interactive_bot.py 的功能。
    原 interactive_bot.py 中的交互式问答功能现在通过 --morning-interactive 
    和 --evening-interactive 参数提供。
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 路径处理（支持 IDE 直接运行）
# ==============================================================================
_current_file = Path(__file__).resolve()
_current_dir = _current_file.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from daily_planning_bot import DailyPlanningBot
from daily_review_bot import DailyReviewBot
from session_tracker import SessionTracker

# ==============================================================================
# 模块配置
# ==============================================================================


class InteractiveMode:
    """
    交互模式 - 逐问收集信息
    
    从 interactive_bot.py 合并的功能
    """
    
    def __init__(self):
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 晨间问题列表
        self.morning_questions = [
            {
                "id": "tasks",
                "question": "🎯 今天您计划完成哪些主要任务？",
                "hint": "例如：完成XX功能开发、修复YY问题",
                "required": True
            },
            {
                "id": "goals",
                "question": "✅ 今天结束时希望达到什么状态？",
                "hint": "例如：功能A能正常运行、通过测试",
                "required": False
            },
            {
                "id": "risks",
                "question": "⚠️ 今天可能遇到什么困难或风险？",
                "hint": "例如：依赖模块不稳定、时间不够",
                "required": False
            },
            {
                "id": "priority",
                "question": "🔥 如果今天只能完成一件事，是什么？",
                "hint": "例如：最高优先级是修复阻塞性bug",
                "required": False
            }
        ]
        
        # 晚间问题列表
        self.evening_questions = [
            {
                "id": "tasks",
                "question": "📝 今天实际完成了哪些任务？",
                "hint": "简要描述今天完成的主要工作",
                "required": True
            },
            {
                "id": "problems",
                "question": "❓ 今天遇到了什么问题或挑战？",
                "hint": "描述遇到的技术难题",
                "required": False
            },
            {
                "id": "solutions",
                "question": "💡 您是如何解决这些问题的？",
                "hint": "描述关键解决步骤",
                "required": False
            },
            {
                "id": "lessons",
                "question": "📚 今天有什么收获或教训？",
                "hint": "学到了什么？应该避免什么？",
                "required": False
            },
            {
                "id": "tech_debt",
                "question": "🔧 有哪些需要后续处理的技术债务？",
                "hint": "例如：临时脚本、待重构代码",
                "required": False
            }
        ]
    
    def morning_interactive(self):
        """晨间交互模式"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║              🌅 晨间计划 - 交互模式                            ║
╚══════════════════════════════════════════════════════════════╝

我会逐个问您几个问题，请逐一回答。
输入 "跳过" 可以跳过可选问题，输入 "结束" 随时结束。
""")
        
        answers = {}
        for i, q in enumerate(self.morning_questions, 1):
            print(f"\n【问题 {i}/{len(self.morning_questions)}】")
            print(f"{q['question']}")
            print(f"💡 提示: {q['hint']}")
            
            if not q['required']:
                print("(可选问题，输入'跳过'跳过)")
            
            print()
            print("⏳ 等待您的回答...")
            print("-" * 50)
            
            # 在实际使用中，这里会等待用户输入
            # 在AI协作场景中，用户会直接告诉AI答案
            answers[q['id']] = None
        
        return answers
    
    def evening_interactive(self):
        """晚间交互模式"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║              🌙 晚间回顾 - 交互模式                            ║
╚══════════════════════════════════════════════════════════════╝

我会逐个问您几个问题，请逐一回答。
输入 "跳过" 可以跳过可选问题，输入 "结束" 随时结束。
""")
        
        answers = {}
        for i, q in enumerate(self.evening_questions, 1):
            print(f"\n【问题 {i}/{len(self.evening_questions)}】")
            print(f"{q['question']}")
            print(f"💡 提示: {q['hint']}")
            
            if not q['required']:
                print("(可选问题，输入'跳过'跳过)")
            
            print()
            print("⏳ 等待您的回答...")
            print("-" * 50)
            
            answers[q['id']] = None
        
        return answers


class WorkflowOrchestrator:
    """
    工作流编排器

    协调全天的工作记录流程
    """

    def __init__(self):
        self.tracker = SessionTracker()
        self.planning_bot = DailyPlanningBot()
        self.review_bot = DailyReviewBot()

    def morning_routine(self):
        """
        晨间流程

        生成今日计划模板
        """
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🌅 晨间计划时间                            ║
╚══════════════════════════════════════════════════════════════╝
""")

        # 检查昨日待办
        yesterday_todos = self.planning_bot.check_yesterday_todos()
        if yesterday_todos:
            print("⚠️  昨日有待办未完成：")
            for todo in yesterday_todos:
                print(f"   - {todo}")
            print()

        # 生成今日计划
        print(self.planning_bot.generate_planning_template())

        print("""
💡 提示：
   您可以直接告诉我今日计划，例如：
   "今日任务：1. 完成XX 2. 修复YY"
   "预期目标：功能A正常运行"
   "风险：可能遇到ZZ问题"
   
   我会帮您更新到今日记录中。
""")

    def track_work(self, continuous: bool = False, interval: int = 300):
        """
        跟踪工作流程

        Args:
            continuous: 是否持续跟踪
            interval: 跟踪间隔（秒）
        """
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    📊 工作跟踪模式                            ║
╚══════════════════════════════════════════════════════════════╝
""")

        if continuous:
            print(f"🔄 持续跟踪模式（每 {interval} 秒检查一次）")
            print("按 Ctrl+C 停止\n")

            try:
                while True:
                    self._do_tracking()
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\n\n✅ 跟踪已停止")
        else:
            self._do_tracking()

    def _do_tracking(self):
        """执行一次跟踪"""
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] 正在检测工作活动...")

        activities = self.tracker.detect_activities()

        # 检查是否有新活动
        log_content = self.tracker.read_today_log()

        # 简单的活动统计
        total_files = len(activities['files_created']) + len(activities['files_modified'])

        if total_files > 0:
            print(f"  📁 检测到 {total_files} 个文件变更")
        if activities['executions']:
            print(f"  🚀 检测到 {len(activities['executions'])} 次执行")
        if activities['decisions']:
            print(f"  📋 检测到 {len(activities['decisions'])} 个决策")

        # 更新记录
        self.tracker.update_today_log(activities)

        print(f"  ✅ 记录已更新\n")

    def evening_routine(self):
        """
        晚间流程

        生成回顾报告并协助完善记录
        """
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    🌙 晚间回顾时间                            ║
╚══════════════════════════════════════════════════════════════╝
""")

        # 生成回顾报告
        print(self.review_bot.generate_review_report())

        print("""
💡 提示：
   您可以直接告诉我需要完善的内容，例如：
   "任务1：完成了XX功能的开发"
   "问题：遇到了YY错误"
   "解决：第一步...第二步..."
   "启示：学到了... 教训：应该避免..."
   "技术债务：test_fix.py需要删除"
   
   我会帮您更新到今日记录中。
""")

    def morning_interactive(self):
        """
        晨间交互模式
        
        逐个询问今日计划问题
        """
        interactive = InteractiveMode()
        return interactive.morning_interactive()
    
    def evening_interactive(self):
        """
        晚间交互模式
        
        逐个询问今日回顾问题
        """
        interactive = InteractiveMode()
        return interactive.evening_interactive()

    def auto_mode(self):
        """
        自动模式

        根据当前时间自动选择流程
        """
        now = datetime.now()
        hour = now.hour

        if 6 <= hour < 10:
            print("🌅 检测到晨间时间，启动晨间计划...")
            self.morning_routine()
        elif 10 <= hour < 21:
            print("📊 检测到工作时间，启动工作跟踪...")
            self.track_work(continuous=False)
        elif hour >= 21 or hour < 6:
            print("🌙 检测到晚间时间，启动晚间回顾...")
            self.evening_routine()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='工作流编排器 - 全天自动化管理工作记录',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 晨间计划（生成今日计划模板）
  python orchestrator.py --morning

  # 工作跟踪（检测并记录工作活动）
  python orchestrator.py --track

  # 持续跟踪（每5分钟检查一次）
  python orchestrator.py --track --continuous

  # 晚间回顾（生成回顾报告）
  python orchestrator.py --evening

  # 自动模式（根据时间自动选择）
  python orchestrator.py --auto

  # 交互模式 - 晨间计划（逐个提问）
  python orchestrator.py --morning-interactive

  # 交互模式 - 晚间回顾（逐个提问）
  python orchestrator.py --evening-interactive
        """
    )

    parser.add_argument(
        '--morning',
        action='store_true',
        help='晨间计划模式（标准）'
    )

    parser.add_argument(
        '--morning-interactive',
        action='store_true',
        help='晨间计划模式（交互式，逐个提问）'
    )

    parser.add_argument(
        '--track',
        action='store_true',
        help='工作跟踪模式'
    )

    parser.add_argument(
        '--continuous',
        action='store_true',
        help='持续跟踪（配合 --track 使用）'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='跟踪间隔（秒），默认300秒（5分钟）'
    )

    parser.add_argument(
        '--evening',
        action='store_true',
        help='晚间回顾模式（标准）'
    )

    parser.add_argument(
        '--evening-interactive',
        action='store_true',
        help='晚间回顾模式（交互式，逐个提问）'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='自动模式（根据时间自动选择）'
    )

    args = parser.parse_args()

    orchestrator = WorkflowOrchestrator()

    if args.morning:
        orchestrator.morning_routine()
    elif args.morning_interactive:
        orchestrator.morning_interactive()
    elif args.track:
        orchestrator.track_work(continuous=args.continuous, interval=args.interval)
    elif args.evening:
        orchestrator.evening_routine()
    elif args.evening_interactive:
        orchestrator.evening_interactive()
    elif args.auto:
        orchestrator.auto_mode()
    else:
        # 默认根据时间自动选择
        orchestrator.auto_mode()


if __name__ == "__main__":
    main()
