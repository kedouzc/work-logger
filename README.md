# Work Logger - 智能工作记录助手

自动化管理工作日志，让每天的工作都有迹可循。

## 核心功能

- [早晨] **晨间计划** - 逐个提问，生成今日工作计划
- [全天] **工作跟踪** - 自动检测文件修改，记录工作活动
- [晚上] **晚间回顾** - 逐个提问，总结今日工作
- [自动] **智能提醒** - 22:00 自动提醒做回顾

---

## 快速开始（全自动配置）

### 方式一：IDE 打开自动启动（推荐）

让 Work Logger 在打开 VS Code 时自动运行：

**步骤：**

1. **打开 VS Code 全局设置**
   - 按 `Ctrl+Shift+P`
   - 输入 `Preferences: Open User Settings (JSON)`
   - 回车打开

2. **添加以下配置**
   ```json
   {
     "terminal.integrated.profiles.windows": {
       "PowerShell": {
         "source": "PowerShell",
         "args": ["-NoExit", "-Command", "python d:\\AI\\work-logger\\launch.py --once"]
       }
     },
     "terminal.integrated.defaultProfile.windows": "PowerShell",
     "workbench.startupEditor": "none"
   }
   ```

3. **保存并重启 VS Code**

**效果：** 以后打开任何项目，Work Logger 都会自动启动

---

### 方式二：开机自动启动

让 Work Logger 在电脑开机时自动运行：

**步骤：**

1. **手动创建启动脚本**
   
   打开文件资源管理器，在地址栏输入：
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
   ```

2. **在该目录创建 `work-logger.bat` 文件，内容如下：**
   ```bat
   @echo off
   echo [启动] Work Logger...
   python "d:\AI\work-logger\launch.py" --once
   exit
   ```

3. **重启电脑测试**

**效果：** 每次开机自动启动 Work Logger（如果是早上6-12点，会提问晨间计划；如果是晚上21-23点，会提问晚间回顾）

---

### 方式三：桌面快捷方式（手动启动）

1. **在桌面创建 `Work Logger.bat` 文件，内容如下：**
   ```bat
   @echo off
   echo [启动] Work Logger...
   python "d:\AI\work-logger\launch.py"
   pause
   ```

2. **需要时双击运行**

---

## 手动运行（当自动配置失败时）

如果自动配置无法工作，可以手动运行：

### 基本命令

```bash
# 进入你的项目目录
cd d:\AI\你的项目

# 运行 Work Logger
python d:\AI\work-logger\launch.py
```

### 参数说明

```bash
# 仅启动守护进程（22:00提醒）
python d:\AI\work-logger\launch.py --daemon

# 仅运行一次（不启动守护进程）
python d:\AI\work-logger\launch.py --once

# 完整启动（守护进程 + 自动启动）
python d:\AI\work-logger\launch.py
```

### 直接运行特定功能

```bash
# 强制运行晨间计划（交互式提问）
cd d:\AI\你的项目
python -c "import sys; sys.path.insert(0, 'd:\\AI\\work-logger\\work_logger'); from interactive_bot import morning_interactive; morning_interactive()"

# 强制运行晚间回顾（交互式提问）
cd d:\AI\你的项目
python -c "import sys; sys.path.insert(0, 'd:\\AI\\work-logger\\work_logger'); from interactive_bot import evening_interactive; evening_interactive()"

# 仅跟踪工作（无交互）
cd d:\AI\你的项目
python -c "import sys; sys.path.insert(0, 'd:\\AI\\work-logger\\work_logger'); from session_tracker import update_today_log; update_today_log()"
```

---

## 工作流程

### 早上（6:00 - 12:00）

1. 打开 IDE / 开机
2. Work Logger 自动启动
3. **逐个提问：**
   - 今天的主要工作目标是什么？
   - 今天计划完成哪些具体任务？
   - 今天可能遇到什么挑战或风险？
   - 今天最重要的一件事是什么？
4. 回答完成后，自动生成 `mind/daily/YYYY-MM-DD-plan.md`

### 全天

- Work Logger 在后台静默运行
- 自动检测文件修改
- 记录到 `mind/daily/YYYY-MM-DD.md`

### 晚上（21:00 - 23:00）

1. 如果还在工作，Work Logger 会启动
2. **逐个提问：**
   - 今天实际完成了哪些任务？
   - 今天遇到了什么问题或困难？
   - 这些问题是如何解决的？
   - 今天有什么收获或经验教训？
   - 明天计划做什么？
3. 回答完成后，自动生成 `mind/daily/YYYY-MM-DD-review.md`

### 22:00 提醒

- 如果此时还在工作，会弹出提醒
- 提示你开始做晚间回顾

---

## 文件保存位置

Work Logger 会在**当前工作目录**（你运行命令时所在的目录）创建：

```
你的项目/
└── mind/
    └── daily/
        ├── 2026-02-14-plan.md      # 晨间计划
        ├── 2026-02-14.md            # 工作记录
        └── 2026-02-14-review.md     # 晚间回顾
```

**重要：** 确保在正确的项目目录下运行 Work Logger，这样记录才会保存到对应项目的 `mind/daily/` 中。

---

## 故障排除

### 问题1：命令找不到

**现象：**
```
'python' 不是内部或外部命令
```

**解决：**
- 确保 Python 已安装并添加到 PATH
- 使用完整路径：`C:\Python311\python.exe d:\AI\work-logger\launch.py`

### 问题2：编码错误（中文乱码）

**现象：**
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**解决：**
- 已修复，所有输出使用 ASCII 字符
- 如果仍有问题，设置终端编码：`chcp 65001`

### 问题3：没有自动启动

**现象：** 打开 IDE 或开机后 Work Logger 没有自动运行

**解决：**
1. 检查配置是否正确（参考上面的"全自动配置"部分）
2. 手动运行测试：`python d:\AI\work-logger\launch.py --once`
3. 查看错误信息，根据提示修复

### 问题4：记录保存到了错误的位置

**现象：** 记录在 `d:\AI\work-logger\mind\daily\` 而不是项目目录

**解决：**
- 确保先 `cd` 到项目目录，再运行 Work Logger
- Work Logger 使用 `os.getcwd()` 获取当前目录

---

## 目录结构

```
d:\AI\work-logger\                    # 工具根目录
├── launch.py                          # 主启动器（入口）
├── pyproject.toml                     # 现代 Python 配置
├── README.md                          # 本文件
└── work_logger\                       # 核心代码包
    ├── __init__.py
    ├── interactive_bot.py             # 交互式提问（核心）
    ├── auto_start.py                  # 自动启动逻辑
    ├── session_tracker.py             # 工作跟踪
    ├── orchestrator.py                # 工作流编排
    ├── work_reminder_daemon.py        # 守护进程（22:00提醒）
    ├── daily_planning_bot.py          # 晨间计划（旧版）
    ├── daily_review_bot.py            # 晚间回顾（旧版）
    ├── generate_daily_log.py          # 日志生成
    ├── generate_stats_report.py       # 统计报告
    └── update_daily_index.py          # 索引更新
```

---

## 自定义提问内容（配置驱动）

Work Logger 支持通过配置文件自定义提问内容，**无需修改代码**。

### 配置文件位置

```
d:\AI\work-logger\config\questions.yaml
```

### 修改示例

**添加新问题：**
```yaml
questions:
  - id: "goal"
    text: "今天您的主要工作目标是什么？"
    hint: "例如：完成XX功能开发"
    required: true
  
  # 添加这个新问题
  - id: "mood"
    text: "今天心情如何？"
    hint: "好/一般/差"
    required: false
```

**修改问题文本：**
```yaml
# 修改前
- id: "goal"
  text: "今天您的主要工作目标是什么？"

# 修改后
- id: "goal"
  text: "今天最想完成的一件事是什么？"
```

**修改模板：**
```yaml
plan_template: |
  # {date} 工作计划
  
  ## 我的目标
  {goal}
  
  ## 任务清单
  {tasks}
  
  ## 心情
  {mood}
  
  ---
  创建于 {time}
```

### 配置说明

- **id**: 问题标识（用于模板变量，必须唯一）
- **text**: 问题文本（显示给用户）
- **hint**: 提示信息（可选）
- **required**: 是否必填（`true` 或 `false`）
- **模板变量**: 使用 `{变量名}` 格式，如 `{date}`, `{time}`, `{goal}`

---

## 提示

1. **晨间计划** 和 **晚间回顾** 只在特定时间段运行（早上6-12点，晚上21-23点）
2. 如果错过时间，可以手动运行特定功能（见"手动运行"部分）
3. 工作记录是增量更新的，可以多次运行不会丢失数据
4. 所有记录都是 Markdown 格式，可以用任何编辑器打开
5. **自定义提问**: 修改 `config/questions.yaml` 即可，无需改代码

---

## 许可证

MIT License
