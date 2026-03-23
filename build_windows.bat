@echo off
chcp 65001 >nul
echo ==========================================
echo  亚马逊链接生成器 - Windows 安装脚本
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 正在安装依赖...
pip install -q pyinstaller pywebview requests beautifulsoup4 playwright
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [2/4] 正在安装 Chromium...
playwright install chromium
if errorlevel 1 (
    echo [警告] Chromium 安装可能失败，继续打包...
)

echo [3/4] 正在打包应用程序...
pyinstaller --clean amazon_link_generator.spec
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo [4/4] 打包完成！
echo.
echo 可执行文件位置: dist\亚马逊链接生成器.exe
echo.
pause
