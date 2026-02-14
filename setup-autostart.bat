@echo off
echo Work Logger 全自动配置
echo ========================================
echo.

:: 创建启动项目录（如果不存在）
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

:: 创建启动脚本
echo [创建] 开机启动脚本...
(
echo @echo off
echo echo [启动] Work Logger...
echo python "d:\AI\work-logger\launch.py" --once
echo exit
) > "%STARTUP%\work-logger.bat"

echo [完成] 已添加到开机启动
echo    位置: %STARTUP%\work-logger.bat
echo.

:: 创建桌面快捷方式
echo [创建] 桌面快捷方式...
set "DESKTOP=%USERPROFILE%\Desktop"
(
echo @echo off
echo echo [启动] Work Logger...
echo python "d:\AI\work-logger\launch.py"
echo pause
) > "%DESKTOP%\Work Logger.bat"

echo [完成] 已创建桌面快捷方式
echo    位置: %DESKTOP%\Work Logger.bat
echo.

echo ========================================
echo [完成] 配置完成！
echo.
echo 现在你可以：
echo   1. 重启电脑 - 自动启动 Work Logger
echo   2. 双击桌面 "Work Logger.bat" - 手动启动
echo   3. 打开 IDE - 自动运行
echo.
echo 功能：
echo   - 早上自动晨间计划（逐个提问）
echo   - 全天后台跟踪工作
echo   - 晚上22点自动提醒回顾
echo.
pause
