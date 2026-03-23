#!/bin/bash

echo "=========================================="
echo "  亚马逊链接生成器 - 依赖安装脚本"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/3] 正在安装 Playwright..."
pip3 install playwright -q
if [ $? -ne 0 ]; then
    echo "[错误] Playwright 安装失败"
    exit 1
fi

echo "[2/3] 正在下载 Chromium 浏览器..."
python3 -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "[错误] Chromium 下载失败，请检查网络连接"
    exit 1
fi

echo "[3/3] 安装完成！"
echo ""
echo "=========================================="
echo "  现在可以运行应用程序了"
echo "=========================================="
