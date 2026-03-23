#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask后端服务器
整合所有功能模块
"""

import os
import json
import time
import random
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, quote_plus
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# 导入功能模块
from .link_generator import LinkGenerator
from .rank_checker import RankChecker
from .real_link_fetcher import RealLinkFetcher


def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    CORS(app)
    
    # 初始化功能模块
    link_gen = LinkGenerator()
    rank_checker = RankChecker()
    
    # ============== 页面路由 ==============
    
    @app.route('/')
    def index():
        """主页面"""
        return render_template('index.html')
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """静态文件服务"""
        return send_from_directory(app.static_folder, filename)
    
    # ============== API路由 - 链接生成 ==============
    
    @app.route('/api/generate-link', methods=['POST'])
    def api_generate_link():
        """生成推广链接"""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        
        mode = data.get('mode', 'simple')
        asin = data.get('asin', '').strip()
        tag = data.get('tag', 'jackyfan5-20').strip()
        
        if not asin:
            return jsonify({'error': '缺少必要参数: asin'}), 400
            
        if len(asin) != 10:
            return jsonify({'error': 'ASIN 必须是10位字符'}), 400
        
        try:
            result = link_gen.generate_link(
                mode=mode,
                asin=asin,
                tag=tag,
                title=data.get('title', ''),
                keyword=data.get('keyword', ''),
                rank=data.get('rank', '1-1'),
                crid=data.get('crid'),
                xpid=data.get('xpid'),
                qid=data.get('qid')
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============== API路由 - 排名查询 ==============
    
    @app.route('/api/check-rank', methods=['POST'])
    def api_check_rank():
        """查询产品排名"""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
            
        keyword = data.get('keyword', '').strip()
        asin = data.get('asin', '').strip()
        max_pages = data.get('max_pages', 5)
        
        if not keyword or not asin:
            return jsonify({'error': '缺少必要参数: keyword 或 asin'}), 400
            
        if len(asin) != 10:
            return jsonify({'error': 'ASIN 必须是10位字符'}), 400
        
        try:
            result = rank_checker.find_product_rank(keyword, asin, max_pages)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # ============== API路由 - 真实链接获取 ==============
    
    @app.route('/api/get-real-link', methods=['POST'])
    def api_get_real_link():
        """获取真实链接（带dib）"""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
            
        keyword = data.get('keyword', '').strip()
        asin = data.get('asin', '').strip()
        max_pages = data.get('max_pages', 5)
        headless = data.get('headless', True)
        
        if not keyword or not asin:
            return jsonify({'error': '缺少必要参数: keyword 或 asin'}), 400
            
        if len(asin) != 10:
            return jsonify({'error': 'ASIN 必须是10位字符'}), 400
        
        fetcher = RealLinkFetcher(headless=headless)
        
        try:
            fetcher.start()
            result = fetcher.search_and_get_link(keyword, asin, max_pages)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            fetcher.stop()
    
    # ============== API路由 - 系统信息 ==============
    
    @app.route('/api/status', methods=['GET'])
    def api_status():
        """获取系统状态"""
        return jsonify({
            'status': 'running',
            'version': '1.0.0',
            'features': {
                'link_generator': True,
                'rank_checker': True,
                'real_link_fetcher': RealLinkFetcher.is_available()
            }
        })
    
    return app
