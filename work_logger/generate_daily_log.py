#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日工作记录生成脚本

功能：自动生成每日工作记录模板
用法：python scripts/generate_daily_log.py
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import os
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

# ==============================================================================
# 模块配置
# ==============================================================================


def get_weekday_cn(weekday: int) -> str:
    """
    获取中文星期

    Args:
        weekday: 星期数字 (0-6)

    Returns:
        中文星期
    """
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return weekdays[weekday]


def generate_daily_log(target_date: datetime = None) -> str:
    """
    生成每日工作记录模板

    Args:
        target_date: 目标日期，默认为今天

    Returns:
        生成的文件路径
    """
    if target_date is None:
        target_date = datetime.now()

    date_str = target_date.strftime("%Y-%m-%d")
    weekday = get_weekday_cn(target_date.weekday())

    template = f"""---
date: {date_str}
weekday: {weekday}
author: developer
tags: []
session: 
---

# {date_str}工作记录

## 今日概览

| 指标 | 数值 |
|------|------|
| 主要任务数 | 0 |
| 子任务数 | 0 |
| 完成率 | 0% |
| 新增文件 | 0 |
| 修改文件 | 0 |

---

## 任务分解

### 任务1：[任务名称]

#### 1.1 面临的主要问题

<!-- 描述遇到的问题 -->

#### 1.2 解决过程

| 节点 | 时间 | 内容 | 产出 |
|------|------|------|------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

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

- [ADR-XXX](../decisions/ADR-XXX-xxx.md)
- [经验教训](../lessons/lessons_learned_xxx.md)

---

## 明日待办

1. [ ] 
2. [ ] 
3. [ ] 
"""

    # 确定目标目录 - 从 scripts/work_logger/ 向上两级到项目根目录
    base_dir = _current_dir.parent.parent
    daily_dir = base_dir / "mind" / "daily"

    # 确保目录存在
    daily_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件路径
    filename = daily_dir / f"{date_str}.md"

    # 检查文件是否已存在
    if filename.exists():
        print(f"⚠️  文件已存在: {filename}")
        overwrite = input("是否覆盖? (y/n): ").lower()
        if overwrite != 'y':
            print("已取消")
            return str(filename)

    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"✅ 已生成: {filename}")
    return str(filename)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='生成每日工作记录模板',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成今天的工作记录
  python generate_daily_log.py

  # 生成指定日期的工作记录
  python generate_daily_log.py --date 2026-02-14
        """
    )

    parser.add_argument(
        '--date',
        type=str,
        help='指定日期 (格式: YYYY-MM-DD)，默认为今天'
    )

    args = parser.parse_args()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    else:
        target_date = None

    generate_daily_log(target_date)


if __name__ == "__main__":
    main()
