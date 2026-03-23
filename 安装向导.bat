@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ==========================================
echo  亚马逊链接生成器 - 完整安装向导
echo ==========================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] 管理员权限检测通过
) else (
    echo [警告] 建议以管理员身份运行此安装程序
    echo 右键点击安装程序，选择"以管理员身份运行"
    echo.
    pause
)

echo.
echo ==========================================
echo  步骤 1/4: 检查 Python
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] 未检测到 Python
    echo.
    echo 正在打开 Python 下载页面...
    echo 请下载并安装 Python 3.8 或更高版本
    echo 安装时请务必勾选 "Add Python to PATH"
    echo.
    start https://www.python.org/downloads/windows/
    echo 安装完成后，请重新运行此安装程序
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%a in ('python --version') do (
        echo [✓] 检测到: %%a
    )
)

echo.
echo ==========================================
echo  步骤 2/4: 升级 pip
echo ==========================================
echo.

python -m pip install --upgrade pip
if errorlevel 1 (
    echo [警告] pip 升级失败，继续尝试安装...
) else (
    echo [✓] pip 升级成功
)

echo.
echo ==========================================
echo  步骤 3/4: 安装 Playwright
echo ==========================================
echo.

echo 正在安装 Playwright（约需 1-2 分钟）...
pip install playwright
if errorlevel 1 (
    echo.
    echo [✗] Playwright 安装失败
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. 防火墙阻止
    echo.
    echo 请尝试手动运行：
    echo   pip install playwright
    echo.
    pause
    exit /b 1
)
echo [✓] Playwright 安装成功

echo.
echo ==========================================
echo  步骤 4/4: 下载 Chromium 浏览器
echo ==========================================
echo.

echo 正在下载 Chromium 浏览器（约 100MB，可能需要几分钟）...
echo 请耐心等待，不要关闭窗口...
echo.
python -m playwright install chromium
if errorlevel 1 (
    echo.
    echo [✗] Chromium 下载失败
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. 磁盘空间不足
    echo.
    echo 请检查网络后，手动运行：
    echo   python -m playwright install chromium
    echo.
    pause
    exit /b 1
)
echo [✓] Chromium 浏览器安装成功

echo.
echo ==========================================
echo  ✅ 所有依赖安装完成！
echo ==========================================
echo.
echo 现在可以运行 亚马逊链接生成器.exe 了
echo.
echo 功能说明：
echo   - 生成亚马逊推广链接
.echo   - 查询产品搜索排名
.echo   - 获取真实链接（带dib参数）
echo.
pause
