#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日回顾助手 - 晚上10点提醒完善工作记录

功能：
    1. 检测当天工作活动
    2. 生成需要确认的关键问题
    3. 协助完善每日记录

用法：
    python scripts/daily_review_bot.py
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 路径处理（支持 IDE 直接运行）
# ==============================================================================
_current_file = Path(__file__).resolve()
_current_dir = _current_file.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

# 导入 session_tracker
from session_tracker import SessionTracker

# ==============================================================================
# 模块配置
# ==============================================================================


class DailyReviewBot:
    """
    每日回顾助手

    协助用户完善每日工作记录
    """

    def __init__(self):
        self.tracker = SessionTracker()
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.tracker.get_today_log()

    def analyze_today_work(self) -> dict:
        """
        分析今天的工作内容

        Returns:
            工作分析结果
        """
        activities = self.tracker.detect_activities()
        log_content = self.tracker.read_today_log()

        analysis = {
            "has_tasks": False,
            "has_problems": False,
            "has_solutions": False,
            "has_lessons": False,
            "has_tech_debt": False,
            "files_count": len(activities['files_created']) + len(activities['files_modified']),
            "decisions_count": len(activities['decisions']),
            "missing_sections": []
        }

        # 检查是否已填写任务
        if "[待填写]" in log_content or "任务1：[待填写]" in log_content:
            analysis["missing_sections"].append("任务描述")
        else:
            analysis["has_tasks"] = True

        # 检查是否已填写问题
        if "<!-- 描述遇到的问题 -->" in log_content:
            analysis["missing_sections"].append("问题描述")
        else:
            analysis["has_problems"] = True

        # 检查是否已填写解决过程
        if "| 1 | | | |" in log_content:
            analysis["missing_sections"].append("解决过程")
        else:
            analysis["has_solutions"] = True

        # 检查是否已填写启示教训
        if "- ✅" in log_content and "- ✅ \n" not in log_content:
            analysis["has_lessons"] = True
        else:
            analysis["missing_sections"].append("启示教训")

        # 检查是否已填写技术债务
        if "| | | | |" in log_content:
            analysis["missing_sections"].append("技术债务")
        else:
            analysis["has_tech_debt"] = True

        return analysis

    def generate_questions(self, analysis: dict) -> list:
        """
        生成需要询问的问题

        Args:
            analysis: 工作分析结果

        Returns:
            问题列表
        """
        questions = []

        if "任务描述" in analysis["missing_sections"]:
            questions.append({
                "id": "tasks",
                "category": "任务描述",
                "question": "今天您主要完成了哪些任务？",
                "prompt": "请简要描述今天的主要工作任务，例如：\n- 完成了XX功能的开发\n- 修复了YY问题\n- 优化了ZZ模块",
                "example": "1. 完成了文件结构重构\n2. 开发了智能路径解析器\n3. 修复了政策转译双前缀问题"
            })

        if "问题描述" in analysis["missing_sections"]:
            questions.append({
                "id": "problems",
                "category": "问题描述",
                "question": "今天工作中遇到了哪些主要问题？",
                "prompt": "请描述遇到的技术难题或挑战，例如：\n- 遇到了什么错误？\n- 什么功能无法实现？\n- 性能瓶颈在哪里？",
                "example": "1. 文件结构重构后路径错误\n2. 政策转译出现params.params双前缀\n3. Rk/Rg单位被错误转换"
            })

        if "解决过程" in analysis["missing_sections"]:
            questions.append({
                "id": "solutions",
                "category": "解决过程",
                "question": "您是如何解决这些问题的？",
                "prompt": "请描述解决问题的关键步骤，例如：\n- 第一步：定位问题\n- 第二步：尝试方案A\n- 第三步：采用方案B并验证",
                "example": "1. 通过debug脚本定位到阶段二替换问题\n2. 尝试正则表达式修复（未完全解决）\n3. 重构为分离映射表策略（彻底解决）"
            })

        if "启示教训" in analysis["missing_sections"]:
            questions.append({
                "id": "lessons",
                "category": "启示教训",
                "question": "今天的工作给您带来了哪些启示或教训？",
                "prompt": "请总结今天的收获，例如：\n- 学到了什么新技术？\n- 有什么最佳实践？\n- 应该避免什么？",
                "example": "启示：\n- 分层处理的重要性\n- 配置驱动的价值\n\n教训：\n- 不要过早优化正则\n- 避免简单字符串替换"
            })

        if "技术债务" in analysis["missing_sections"]:
            questions.append({
                "id": "tech_debt",
                "category": "技术债务",
                "question": "有哪些文件或代码需要后续处理？",
                "prompt": "请列出需要清理或改进的技术债务，例如：\n- 临时调试脚本\n- 待重构的代码\n- 待补充的测试",
                "example": "| 临时脚本 | test_fix.py系列 | 评估后删除 | 低 |\n| 调试脚本 | debug_params.py | 保留核心3个 | 中 |"
            })

        return questions

    def generate_review_report(self) -> str:
        """
        生成回顾报告

        Returns:
            回顾报告文本
        """
        analysis = self.analyze_today_work()
        questions = self.generate_questions(analysis)

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           📋 每日工作回顾 - {self.today_str}                    ║
╚══════════════════════════════════════════════════════════════╝

📊 今日工作统计
─────────────────────────────────────────────────────────────
  文件变更: {analysis['files_count']} 个
  决策记录: {analysis['decisions_count']} 个
  完成度: {5 - len(analysis['missing_sections'])}/5

✅ 已完成部分
─────────────────────────────────────────────────────────────
"""
        if analysis["has_tasks"]:
            report += "  ✓ 任务描述\n"
        if analysis["has_problems"]:
            report += "  ✓ 问题描述\n"
        if analysis["has_solutions"]:
            report += "  ✓ 解决过程\n"
        if analysis["has_lessons"]:
            report += "  ✓ 启示教训\n"
        if analysis["has_tech_debt"]:
            report += "  ✓ 技术债务\n"

        if analysis["missing_sections"]:
            report += """
📝 待完善部分
─────────────────────────────────────────────────────────────
"""
            for section in analysis["missing_sections"]:
                report += f"  ⏳ {section}\n"

        if questions:
            report += """
💬 需要确认的问题
═══════════════════════════════════════════════════════════════
"""
            for i, q in enumerate(questions, 1):
                report += f"""
【{i}】{q['category']}
问题: {q['question']}

提示: {q['prompt']}

示例: 
{q['example']}

─────────────────────────────────────────────────────────────
"""

        report += """
🎯 下一步行动
─────────────────────────────────────────────────────────────
  1. 回答上述问题，完善今日记录
  2. 运行: python scripts/generate_stats_report.py
  3. 确认明日待办事项

💡 提示
─────────────────────────────────────────────────────────────
  您可以直接告诉我答案，例如：
  "任务1：完成了XX功能的开发"
  "问题：遇到了YY错误"
  
  我会帮您更新到今日记录中。
"""

        return report

    def update_log_section(self, section: str, content: str):
        """
        更新记录的特定部分

        Args:
            section: 部分名称（tasks/problems/solutions/lessons/tech_debt）
            content: 内容
        """
        log_content = self.tracker.read_today_log()

        if section == "tasks":
            # 替换任务1标题
            log_content = re.sub(
                r'### 任务1：\[待填写\]',
                f'### 任务1：{content.split(chr(10))[0] if chr(10) in content else content}',
                log_content
            )

        elif section == "problems":
            # 替换问题描述
            log_content = re.sub(
                r'#### 1\.1 面临的主要问题\n\n<!-- 描述遇到的问题 -->',
                f'#### 1.1 面临的主要问题\n\n{content}',
                log_content
            )

        elif section == "solutions":
            # 解析解决过程表格
            lines = content.strip().split('\n')
            table_rows = []
            for i, line in enumerate(lines, 1):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 2:
                        time_part = parts[0].strip() if len(parts) > 0 else ""
                        content_part = parts[1].strip() if len(parts) > 1 else line.strip()
                        output_part = parts[2].strip() if len(parts) > 2 else ""
                        table_rows.append(f"| {i} | {time_part} | {content_part} | {output_part} |")

            if table_rows:
                new_table = '\n'.join(table_rows)
                log_content = re.sub(
                    r'\| 1 \| \| \| \|',
                    new_table,
                    log_content
                )

        elif section == "lessons":
            # 替换启示教训
            if "启示：" in content or "教训：" in content:
                # 用户提供了完整格式
                log_content = re.sub(
                    r'\*\*启示：\*\*\n- ✅',
                    f'**启示：**\n{content.split("教训：")[0].replace("启示：", "").strip()}',
                    log_content
                )
                if "教训：" in content:
                    log_content = re.sub(
                        r'\*\*教训：\*\*\n- ⚠️',
                        f'**教训：**\n{content.split("教训：")[1].strip()}',
                        log_content
                    )
            else:
                # 简单替换
                log_content = re.sub(
                    r'- ✅',
                    f'- ✅ {content}',
                    log_content,
                    count=1
                )

        elif section == "tech_debt":
            # 替换技术债务表格
            if "|" in content:
                log_content = re.sub(
                    r'\| \| \| \| \|',
                    content.strip(),
                    log_content
                )

        self.tracker.write_today_log(log_content)
        print(f"✅ 已更新: {section}")


def main():
    """主函数"""
    bot = DailyReviewBot()
    print(bot.generate_review_report())


if __name__ == "__main__":
    main()
