#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日计划助手 - 早晨开始时设定今日计划

功能：
    1. 生成今日计划模板
    2. 协助设定今日目标
    3. 预测可能的风险

用法：
    python scripts/daily_planning_bot.py
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ==============================================================================
# 路径处理（支持 IDE 直接运行）
# ==============================================================================
_current_file = Path(__file__).resolve()
_current_dir = _current_file.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from session_tracker import SessionTracker

# ==============================================================================
# 模块配置
# ==============================================================================


class DailyPlanningBot:
    """
    每日计划助手

    协助用户设定今日工作计划
    """

    def __init__(self):
        self.tracker = SessionTracker()
        self.today = datetime.now()
        self.today_str = self.today.strftime("%Y-%m-%d")
        self.yesterday_str = (self.today - timedelta(days=1)).strftime("%Y-%m-%d")

    def check_yesterday_todos(self) -> list:
        """
        检查昨日待办

        Returns:
            昨日未完成的待办事项
        """
        yesterday_log = self.tracker.daily_dir / f"{self.yesterday_str}.md"
        todos = []

        if yesterday_log.exists():
            content = yesterday_log.read_text(encoding='utf-8')
            # 查找明日待办部分
            match = re.search(r'## 明日待办\n\n(.*?)(?=\n---|\n## |\Z)', content, re.DOTALL)
            if match:
                todos_text = match.group(1)
                for line in todos_text.split('\n'):
                    if line.strip().startswith('- [ ]'):
                        todos.append(line.strip().replace('- [ ]', '').strip())

        return todos

    def analyze_recent_work(self) -> dict:
        """
        分析近期工作趋势

        Returns:
            工作趋势分析
        """
        analysis = {
            "recent_tags": [],
            "unfinished_sessions": [],
            "tech_debt_count": 0
        }

        # 检查最近3天的记录
        for i in range(1, 4):
            date = (self.today - timedelta(days=i)).strftime("%Y-%m-%d")
            log_file = self.tracker.daily_dir / f"{date}.md"
            if log_file.exists():
                content = log_file.read_text(encoding='utf-8')

                # 提取标签
                tags_match = re.search(r'tags: \[(.*?)\]', content)
                if tags_match:
                    tags = [t.strip().strip('"\'') for t in tags_match.group(1).split(',')]
                    analysis["recent_tags"].extend(tags)

                # 检查未完成的会话
                if "session:" in content:
                    session_match = re.search(r'session:\s*(\S+)', content)
                    if session_match and session_match.group(1):
                        analysis["unfinished_sessions"].append({
                            "date": date,
                            "session": session_match.group(1)
                        })

        # 去重标签
        analysis["recent_tags"] = list(set(analysis["recent_tags"]))

        return analysis

    def generate_planning_template(self) -> str:
        """
        生成计划模板

        Returns:
            计划模板文本
        """
        yesterday_todos = self.check_yesterday_todos()
        recent_analysis = self.analyze_recent_work()
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][self.today.weekday()]

        template = f"""
╔══════════════════════════════════════════════════════════════╗
║           🌅 每日计划 - {self.today_str} ({weekday})              ║
╚══════════════════════════════════════════════════════════════╝

📋 昨日回顾
─────────────────────────────────────────────────────────────
"""

        if yesterday_todos:
            template += "昨日待办（建议优先处理）：\n"
            for todo in yesterday_todos:
                template += f"  ⏳ {todo}\n"
        else:
            template += "  昨日无遗留待办\n"

        if recent_analysis["unfinished_sessions"]:
            template += "\n未完成的会话：\n"
            for session in recent_analysis["unfinished_sessions"][:3]:
                template += f"  🔄 {session['date']}: {session['session']}\n"

        if recent_analysis["recent_tags"]:
            template += f"\n近期工作标签：{', '.join(recent_analysis['recent_tags'][:5])}\n"

        template += """
─────────────────────────────────────────────────────────────

🎯 今日计划设定
═══════════════════════════════════════════════════════════════

请回答以下问题，我会帮您生成今日计划：

【1】今日主要任务
    您计划今天完成哪些主要任务？
    示例：
    - 完成XX模块的开发
    - 修复YY问题
    - 优化ZZ性能

【2】预期目标
    今天结束时希望达到什么状态？
    示例：
    - 功能A能够正常运行
    - 通过所有单元测试
    - 完成代码审查

【3】风险预估
    今天可能遇到什么困难或风险？
    示例：
    - 依赖模块可能不稳定
    - 需要学习新技术
    - 时间可能不够

【4】资源需求
    需要什么资源或支持？
    示例：
    - 需要查阅XX文档
    - 需要测试数据
    - 需要同事协助

【5】优先级排序
    如果今天只能完成一件事，是什么？
    示例：
    - 最高优先级：修复阻塞性bug
    - 次要：优化代码结构

─────────────────────────────────────────────────────────────

💡 提示
─────────────────────────────────────────────────────────────
  您可以直接告诉我答案，例如：
  "今日任务：1. 完成XX 2. 修复YY"
  "预期目标：功能A正常运行"
  
  我会帮您更新到今日记录中。

📝 今日记录位置
─────────────────────────────────────────────────────────────
  {self.tracker.get_today_log()}
"""

        return template

    def update_today_plan(self, plan_data: dict):
        """
        更新今日计划到记录中

        Args:
            plan_data: 计划数据字典
        """
        log_file = self.tracker.get_today_log()

        if not log_file.exists():
            # 创建新记录
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][self.today.weekday()]
            content = f"""---
date: {self.today_str}
weekday: {weekday}
author: developer
tags: []
session: 
---

# {self.today_str}工作记录

## 今日概览

| 指标 | 数值 |
|------|------|
| 主要任务数 | {len(plan_data.get('tasks', []))} |
| 子任务数 | 待更新 |
| 完成率 | 0% |
| 新增文件 | 0 |
| 修改文件 | 0 |

---

## 今日计划

### 主要任务
{self._format_tasks(plan_data.get('tasks', []))}

### 预期目标
{plan_data.get('goals', '待填写')}

### 风险预估
{plan_data.get('risks', '待填写')}

### 资源需求
{plan_data.get('resources', '待填写')}

### 优先级
{plan_data.get('priority', '待填写')}

---

## 任务分解

### 任务1：[待填写]

#### 1.1 面临的主要问题

<!-- 描述遇到的问题 -->

#### 1.2 解决过程

| 节点 | 时间 | 内容 | 产出 |
|------|------|------|------|
| 1 | | | |

#### 1.3 结果

<!-- 描述最终结果 -->

#### 1.4 启示与教训

**启示：**
- ✅ 

**教训：**
- ⚠️ 

---

## 技术债务清单

| 类型 | 文件 | 处理建议 | 优先级 |
|------|------|----------|--------|
| | | | |

---

## 关联文档

- [待补充](../decisions/)

---

## 明日待办

1. [ ] 待填写
"""
            log_file.write_text(content, encoding='utf-8')
        else:
            # 更新现有记录
            content = log_file.read_text(encoding='utf-8')

            # 插入今日计划部分
            plan_section = f"""## 今日计划

### 主要任务
{self._format_tasks(plan_data.get('tasks', []))}

### 预期目标
{plan_data.get('goals', '待填写')}

### 风险预估
{plan_data.get('risks', '待填写')}

### 资源需求
{plan_data.get('resources', '待填写')}

### 优先级
{plan_data.get('priority', '待填写')}

---

## 任务分解"""

            if "## 今日计划" not in content:
                content = content.replace("## 任务分解", plan_section)
                log_file.write_text(content, encoding='utf-8')

        print(f"✅ 已更新今日计划: {log_file}")

    def _format_tasks(self, tasks: list) -> str:
        """格式化任务列表"""
        if not tasks:
            return "- 待填写"
        return '\n'.join([f"- {task}" for task in tasks])


def main():
    """主函数"""
    bot = DailyPlanningBot()
    print(bot.generate_planning_template())


if __name__ == "__main__":
    main()
