#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊工具箱 - 桌面版主程序

启动桌面应用，包含内嵌的Flask后端
"""

import sys
import os
import threading
import webview
from flask import Flask

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import create_app

# 全局变量
flask_app = None
server_thread = None


def start_flask_server():
    """在后台线程启动Flask服务器"""
    global flask_app
    flask_app = create_app()
    # 使用127.0.0.1:0让系统自动分配端口
    flask_app.run(host='127.0.0.1', port=0, debug=False, threaded=True)


def get_server_port():
    """获取Flask服务器实际端口"""
    if flask_app and hasattr(flask_app, 'port'):
        return flask_app.port
    return 5000  # 默认端口


def main():
    """主函数"""
    # 启动Flask服务器（后台线程）
    server_thread = threading.Thread(target=start_flask_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    import time
    time.sleep(1)
    
    # 获取实际端口
    port = get_server_port()
    
    # 创建桌面窗口
    window = webview.create_window(
        title='亚马逊工具箱',
        url=f'http://127.0.0.1:{port}',
        width=1200,
        height=800,
        min_size=(1000, 600),
        resizable=True,
        text_select=True
    )
    
    # 启动WebView
    webview.start(
        debug=False,
        gui='default'
    )


if __name__ == '__main__':
    main()
