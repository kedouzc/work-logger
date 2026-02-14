#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work Logger - 智能工作记录助手

自动化管理工作日志，支持晨间计划、工作跟踪、晚间回顾。

用法:
    from work_logger import orchestrator
    orchestrator.main()

命令行:
    work-logger --morning      # 晨间计划
    work-logger --evening      # 晚间回顾
    work-logger --auto         # 自动模式
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 导出主要模块
from . import orchestrator
from . import auto_start
from . import daily_planning_bot
from . import daily_review_bot

__all__ = [
    'orchestrator',
    'auto_start',
    'daily_planning_bot',
    'daily_review_bot',
]
