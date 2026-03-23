@echo off
chcp 65001 >nul
echo ==========================================
echo  亚马逊链接生成器 - 依赖安装脚本
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请务必勾选 "Add Python to PATH"
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python 检测通过
echo.

echo [2/3] 正在安装 Playwright...
pip install playwright
if errorlevel 1 (
    echo.
    echo [错误] Playwright 安装失败
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. pip 版本过旧
    echo.
    echo 请尝试以下命令后重试：
    echo   python -m pip install --upgrade pip
    echo   pip install playwright
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] 正在下载 Chromium 浏览器...
echo 注意：下载约 100MB，可能需要几分钟，请耐心等待...
python -m playwright install chromium
if errorlevel 1 (
    echo.
    echo [错误] Chromium 下载失败
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. 磁盘空间不足
    echo.
    echo 请检查网络后重试，或手动运行：
    echo   python -m playwright install chromium
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  ✅ 安装完成！
echo ==========================================
echo.
echo 现在可以运行 亚马逊链接生成器.exe 了
echo.
pause
