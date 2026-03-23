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
    pause
    exit /b 1
)

echo [1/3] 正在安装 Playwright...
pip install playwright -q
if errorlevel 1 (
    echo [错误] Playwright 安装失败
    pause
    exit /b 1
)

echo [2/3] 正在下载 Chromium 浏览器...
playwright install chromium
if errorlevel 1 (
    echo [错误] Chromium 下载失败，请检查网络连接
    pause
    exit /b 1
)

echo [3/3] 安装完成！
echo.
echo ==========================================
echo  现在可以运行 亚马逊链接生成器.exe 了
echo ==========================================
echo.
pause
