#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Work Logger - 安装配置
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="work-logger-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="智能工作记录助手 - 自动化管理工作日志",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/work-logger-bot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 这里列出依赖，目前只用标准库，所以为空
    ],
    entry_points={
        "console_scripts": [
            "work-logger=work_logger.cli:main",
            "wl=work_logger.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
