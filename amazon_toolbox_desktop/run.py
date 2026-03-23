#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊工具箱 - 启动脚本
用于开发测试和打包
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.server import create_app

def main():
    """主函数"""
    print("="*60)
    print("🚀 亚马逊工具箱 - 开发模式")
    print("="*60)
    print("\n访问地址: http://127.0.0.1:5000")
    print("\n功能模块:")
    print("  - 链接生成器: 生成带追踪参数的亚马逊链接")
    print("  - 排名查询: 查询产品在搜索结果中的排名")
    print("  - 真实链接获取: 获取带dib参数的真实链接")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
