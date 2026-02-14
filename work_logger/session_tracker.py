#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作会话跟踪器 - 修复版

支持从任意工作目录运行，记录保存到当前项目的 mind/daily/
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 获取当前工作目录（用户项目目录）
WORK_DIR = Path(os.getcwd()).resolve()
MIND_DIR = WORK_DIR / "mind"
DAILY_DIR = MIND_DIR / "daily"


def ensure_directories():
    """确保目录存在"""
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def get_today_file() -> Path:
    """获取今日记录文件路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    return DAILY_DIR / f"{today}.md"


def read_today_log() -> str:
    """读取今日记录"""
    log_file = get_today_file()
    if log_file.exists():
        return log_file.read_text(encoding='utf-8')
    return ""


def write_today_log(content: str):
    """写入今日记录"""
    ensure_directories()
    log_file = get_today_file()
    log_file.write_text(content, encoding='utf-8')
    print(f"[完成] 已保存到: {log_file}")


def detect_activities() -> dict:
    """检测工作活动（简化版）"""
    activities = {
        "files_modified": [],
        "time_now": datetime.now().strftime("%H:%M")
    }
    
    # 检测最近修改的文件
    for ext in ["*.py", "*.md", "*.json", "*.yaml", "*.yml"]:
        for file_path in WORK_DIR.rglob(ext):
            try:
                stat = file_path.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                if mtime.date() == datetime.now().date():
                    rel_path = str(file_path.relative_to(WORK_DIR))
                    # 排除 mind 和缓存目录
                    if not any(x in rel_path for x in ['mind/', '__pycache__', '.git']):
                        activities["files_modified"].append(rel_path)
            except:
                continue
    
    return activities


def generate_log_content(activities: dict) -> str:
    """生成日志内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    time_now = activities.get("time_now", "--:--")
    files = activities.get("files_modified", [])
    
    content = f"""# {today} 工作记录

## 跟踪记录

**时间**: {time_now}

### 活动检测
"""
    
    if files:
        content += "\n**修改的文件**:\n"
        for f in files[:10]:  # 最多显示10个
            content += f"- {f}\n"
    else:
        content += "\n暂无文件修改记录\n"
    
    content += f"""
### 备注

- 自动跟踪时间: {time_now}
- 工作目录: {WORK_DIR}

---
*由 Work Logger 自动生成*
"""
    
    return content


def update_today_log():
    """更新今日记录"""
    print(f"[检测] 工作活动...")
    print(f"   工作目录: {WORK_DIR}")
    
    activities = detect_activities()
    content = generate_log_content(activities)
    write_today_log(content)
    
    print(f"   发现 {len(activities['files_modified'])} 个文件修改")


def main():
    """主函数"""
    print("=" * 50)
    print("Work Logger - 工作跟踪")
    print("=" * 50)
    update_today_log()
    print("=" * 50)


if __name__ == '__main__':
    main()
