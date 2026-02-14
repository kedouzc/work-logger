#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作统计报告生成脚本

功能：分析每日工作记录，生成统计报告
用法：python scripts/generate_stats_report.py
"""

# ==============================================================================
# 标准库导入
# ==============================================================================
import os
import re
import sys
from collections import defaultdict
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


def analyze_daily_logs(daily_dir: Path) -> dict:
    """
    分析每日工作记录

    Args:
        daily_dir: 每日记录目录

    Returns:
        统计结果字典
    """
    stats = {
        "total_days": 0,
        "total_tasks": 0,
        "total_files_created": 0,
        "total_files_modified": 0,
        "tags": defaultdict(int),
        "months": defaultdict(int),
        "authors": defaultdict(int),
    }

    if not daily_dir.exists():
        print(f"⚠️  目录不存在: {daily_dir}")
        return stats

    for filename in os.listdir(daily_dir):
        if not filename.endswith(".md") or filename == "README.md":
            continue

        filepath = daily_dir / filename
        if not filepath.is_file():
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            stats["total_days"] += 1

            # 提取日期
            date_match = re.search(r'date:\s*(\d{4}-\d{2}-\d{2})', content)
            if date_match:
                date_str = date_match.group(1)
                month = date_str[:7]  # YYYY-MM
                stats["months"][month] += 1

            # 统计任务数
            tasks = len(re.findall(r'### 任务\d+', content))
            stats["total_tasks"] += tasks

            # 统计标签
            tags_match = re.search(r'tags:\s*\[(.*?)\]', content)
            if tags_match:
                tag_str = tags_match.group(1)
                for tag in tag_str.split(','):
                    tag = tag.strip().strip('"\'')
                    if tag:
                        stats["tags"][tag] += 1

            # 统计作者
            author_match = re.search(r'author:\s*(\w+)', content)
            if author_match:
                author = author_match.group(1)
                stats["authors"][author] += 1

            # 统计新增/修改文件数
            files_created_match = re.search(r'新增文件\s*\|\s*(\d+)', content)
            if files_created_match:
                stats["total_files_created"] += int(files_created_match.group(1))

            files_modified_match = re.search(r'修改文件\s*\|\s*(\d+)', content)
            if files_modified_match:
                stats["total_files_modified"] += int(files_modified_match.group(1))

        except Exception as e:
            print(f"⚠️  处理文件失败 {filename}: {e}")
            continue

    return stats


def generate_report(stats: dict, output_path: Path) -> str:
    """
    生成统计报告

    Args:
        stats: 统计结果
        output_path: 输出文件路径

    Returns:
        生成的报告内容
    """
    report = f"""# 工作统计报告

> 自动生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 总体统计

| 指标 | 数值 |
|------|------|
| 记录天数 | {stats['total_days']} |
| 总任务数 | {stats['total_tasks']} |
| 平均每日任务 | {(stats['total_tasks'] / stats['total_days'] if stats['total_days'] > 0 else 0):.1f} |
| 新增文件总数 | {stats['total_files_created']} |
| 修改文件总数 | {stats['total_files_modified']} |

---

## 月度分布

| 月份 | 记录数 |
|------|--------|
"""

    for month, count in sorted(stats["months"].items(), reverse=True):
        report += f"| {month} | {count} |\n"

    report += """
---

## 标签分布

| 标签 | 出现次数 | 可视化 |
|------|----------|--------|
"""

    max_count = max(stats["tags"].values()) if stats["tags"] else 1
    for tag, count in sorted(stats["tags"].items(), key=lambda x: x[1], reverse=True):
        bar_length = int(20 * count / max_count)
        bar = "█" * bar_length
        report += f"| {tag} | {count} | {bar} |\n"

    report += """
---

## 作者统计

| 作者 | 记录数 |
|------|--------|
"""

    for author, count in sorted(stats["authors"].items(), key=lambda x: x[1], reverse=True):
        report += f"| {author} | {count} |\n"

    report += """
---

## 最近记录

| 日期 | 星期 | 主要任务 | 标签 |
|------|------|----------|------|
"""

    # 获取最近记录（简化版，实际应解析文件）
    daily_dir = output_path.parent / "daily"
    recent_files = []
    for filename in os.listdir(daily_dir):
        if filename.endswith(".md") and filename != "README.md":
            try:
                date_str = filename.replace(".md", "")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                recent_files.append((date_obj, filename))
            except ValueError:
                continue

    recent_files.sort(reverse=True)
    for date_obj, filename in recent_files[:10]:
        report += f"| [{date_obj.strftime('%Y-%m-%d')}](daily/{filename}) | | | |\n"

    report += """
---

## 使用说明

本报告由 `scripts/generate_stats_report.py` 自动生成。

要更新报告，请运行：

```bash
python scripts/generate_stats_report.py
```
"""

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='生成工作统计报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成统计报告
  python generate_stats_report.py

  # 指定输出路径
  python generate_stats_report.py --output mind/STATS_REPORT.md
        """
    )

    parser.add_argument(
        '--output',
        type=str,
        default='mind/STATS_REPORT.md',
        help='输出文件路径 (默认: mind/STATS_REPORT.md)'
    )

    args = parser.parse_args()

    # 确定路径
    base_dir = _current_dir.parent
    daily_dir = base_dir / "mind" / "daily"
    output_path = base_dir / args.output

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 分析日志
    print("📊 正在分析每日工作记录...")
    stats = analyze_daily_logs(daily_dir)

    # 生成报告
    print("📝 正在生成统计报告...")
    generate_report(stats, output_path)

    print(f"✅ 统计报告已生成: {output_path}")
    print(f"\n📈 统计摘要:")
    print(f"   - 记录天数: {stats['total_days']}")
    print(f"   - 总任务数: {stats['total_tasks']}")
    print(f"   - 标签数量: {len(stats['tags'])}")


if __name__ == "__main__":
    main()
