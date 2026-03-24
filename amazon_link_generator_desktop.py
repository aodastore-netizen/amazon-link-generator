#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊链接生成器 - 桌面版
使用 PyWebview 构建轻量级桌面应用

功能：
1. 生成带追踪参数的亚马逊推广链接
2. 查询产品搜索排名
3. 获取真实亚马逊链接（带 dib 参数）

作者：AI Assistant
日期：2026-03-23
"""

import os
import sys
import json
import time
import random
import re
import threading
from urllib.parse import quote_plus, urlparse, parse_qs
from typing import Optional, Dict, Any

import webview

# ============== 工具函数 ==============

def generate_random_string(length: int) -> str:
    """生成随机字符串"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(length))

def generate_timestamp() -> str:
    """生成 Unix 时间戳"""
    return str(int(time.time()))

def url_friendly_title(title: str) -> str:
    """将标题转换为 URL 友好格式"""
    return re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().replace(' ', '-')[:80]

def extract_asin_from_url(url: str) -> Optional[str]:
    """从 URL 中提取 ASIN"""
    match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


# ============== API 类（供前端调用） ==============

class AmazonAPI:
    """亚马逊链接生成器 API"""
    
    def __init__(self):
        self.playwright_available = self._check_playwright()
        
    def _check_playwright(self) -> bool:
        """检查 Playwright 是否可用"""
        try:
            from playwright.sync_api import sync_playwright
            # 设置浏览器路径环境变量（如果在打包环境中）
            self._setup_playwright_path()
            # 尝试启动浏览器验证
            with sync_playwright() as p:
                browser = p.chromium.launch()
                browser.close()
            return True
        except Exception as e:
            print(f"Playwright 检查失败: {e}")
            return False
    
    def _setup_playwright_path(self):
        """设置 Playwright 浏览器路径"""
        # 如果已经有环境变量，不覆盖
        if os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
            return
        
        # 检查可能的浏览器安装位置
        possible_paths = [
            # Windows 默认安装路径
            os.path.expanduser('~/AppData/Local/ms-playwright'),
            os.path.expanduser('~\\AppData\\Local\\ms-playwright'),
            # 当前用户目录
            os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ms-playwright'),
            # 系统级安装（较少见）
            'C:\\ProgramData\\ms-playwright',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = path
                print(f"设置 PLAYWRIGHT_BROWSERS_PATH: {path}")
                return
    
    def _get_playwright_browsers_path(self) -> str:
        """获取 Playwright 浏览器路径（支持打包后的环境）"""
        # 首先检查环境变量
        env_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # 检查是否在打包环境中
        if getattr(sys, 'frozen', False):
            # 运行在 PyInstaller 打包环境中
            base_path = sys._MEIPASS
            browser_path = os.path.join(base_path, 'browsers')
            if os.path.exists(browser_path):
                return browser_path
        
        # 返回默认路径
        return os.path.expanduser('~/AppData/Local/ms-playwright')
    
    def generate_link(self, mode: str, data: dict) -> dict:
        """生成推广链接"""
        asin = data.get('asin', '').strip().upper()
        tag = data.get('tag', 'jackyfan5-20').strip()
        
        if not asin or len(asin) != 10:
            return {'success': False, 'error': 'ASIN 必须是10位字符'}
        
        # 生成参数
        crid = data.get('crid') or generate_random_string(16)
        xpid = data.get('xpid') or (generate_random_string(12) + generate_random_string(4))
        qid = data.get('qid') or generate_timestamp()
        
        if mode == 'simple':
            link = f"https://www.amazon.com/dp/{asin}"
            if tag:
                link += f"?tag={tag}"
                
        elif mode == 'search':
            keyword = data.get('keyword', 'product')
            rank = data.get('rank', '1-1')
            encoded_keyword = quote_plus(keyword)
            sprefix = quote_plus(keyword) + '%2Caps%2C145'
            
            link = f"https://www.amazon.com/dp/{asin}/ref=sr_&sr={rank}&xpid={xpid}?crid={crid}&sprefix={sprefix}&keywords={encoded_keyword}&qid={qid}"
            if tag:
                link += f"&tag={tag}"
                
        elif mode == 'full':
            title = data.get('title', '')
            keyword = data.get('keyword', 'product')
            rank = data.get('rank', '1-1')
            
            url_title = url_friendly_title(title) + '/' if title else ''
            encoded_keyword = quote_plus(keyword)
            sprefix = quote_plus(keyword) + '%2Caps%2C145'
            
            link = f"https://www.amazon.com/{url_title}dp/{asin}/ref=sr_&sr={rank}&xpid={xpid}?crid={crid}&sprefix={sprefix}&keywords={encoded_keyword}&qid={qid}"
            if tag:
                link += f"&tag={tag}"
        else:
            return {'success': False, 'error': '不支持的 mode 参数'}
        
        return {
            'success': True,
            'link': link,
            'asin': asin,
            'tag': tag,
            'mode': mode,
            'params': {
                'crid': crid,
                'xpid': xpid,
                'qid': qid
            }
        }
    
    def check_rank_simple(self, keyword: str, asin: str, max_pages: int = 5) -> dict:
        """简化的排名查询（使用 requests）"""
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            return {
                'success': False,
                'error': '缺少依赖：pip install requests beautifulsoup4',
                'needs_browser': True
            }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        asin = asin.upper().strip()
        session = requests.Session()
        session.headers.update(headers)
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.amazon.com/s?k={quote_plus(keyword)}&page={page}"
                response = session.get(url, timeout=30)
                
                if response.status_code != 200:
                    continue
                
                if "captcha" in response.text.lower():
                    return {
                        'success': False,
                        'error': '被亚马逊反爬拦截，请使用真实浏览器模式',
                        'needs_browser': True
                    }
                
                soup = BeautifulSoup(response.text, 'html.parser')
                products = soup.select('[data-component-type="s-search-result"]')
                
                for position, product in enumerate(products, start=1):
                    link = product.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        found_asin = extract_asin_from_url(href)
                        if found_asin == asin:
                            overall_position = (page - 1) * 48 + position
                            return {
                                'success': True,
                                'found': True,
                                'rank': f"{page}-{overall_position}",
                                'page': page,
                                'position': position,
                                'overall_position': overall_position,
                                'keyword': keyword,
                                'asin': asin
                            }
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"搜索第{page}页出错: {e}")
                continue
        
        return {
            'success': True,
            'found': False,
            'keyword': keyword,
            'asin': asin,
            'message': f'在前{max_pages}页中未找到该产品'
        }
    
    def get_real_link_simple(self, keyword: str, asin: str, max_pages: int = 5) -> dict:
        """Get real link with dib parameter using requests"""
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            return {'success': False, 'error': 'Missing dependencies', 'needs_browser': True}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        asin = asin.upper().strip()
        session = requests.Session()
        session.headers.update(headers)
        
        # Step 1: Search for the product
        found_product_url = None
        rank_info = None
        
        for page_num in range(1, max_pages + 1):
            try:
                url = f"https://www.amazon.com/s?k={quote_plus(keyword)}&page={page_num}"
                response = session.get(url, timeout=30)
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                products = soup.select('[data-component-type="s-search-result"]')
                
                for position, product in enumerate(products, start=1):
                    link_elem = product.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    href = link_elem.get('href', '')
                    found_asin = extract_asin_from_url(href)
                    
                    if found_asin == asin:
                        found_product_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                        rank_info = {
                            'rank': f"{page_num}-{position}",
                            'page': page_num,
                            'position': position
                        }
                        break
                
                if found_product_url:
                    break
                    
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"Page {page_num} search error: {e}")
                continue
        
        if not found_product_url:
            return {'success': True, 'found': False, 'keyword': keyword, 'asin': asin}
        
        # Step 2: Visit the product page to get the real link with dib
        try:
            # Try to get the product page and follow redirects
            product_url = f"https://www.amazon.com/dp/{asin}"
            response = session.get(product_url, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                final_url = response.url
                parsed = urlparse(final_url)
                params = parse_qs(parsed.query)
                
                # Check if we got dib parameter
                if 'dib' in params:
                    return {
                        'success': True,
                        'found': True,
                        'full_link': final_url,
                        'params': {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                        'rank': rank_info['rank'],
                        'page': rank_info['page'],
                        'position': rank_info['position'],
                        'has_dib': True,
                        'keyword': keyword,
                        'asin': asin,
                        'method': 'requests'
                    }
        except Exception as e:
            print(f"Error getting product page: {e}")
        
        # Fallback: return search result link
        # Use the actual search result URL if available
        if found_product_url:
            parsed = urlparse(found_product_url)
            params = parse_qs(parsed.query)
            
            return {
                'success': True,
                'found': True,
                'full_link': found_product_url,
                'params': {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                'rank': rank_info['rank'],
                'page': rank_info['page'],
                'position': rank_info['position'],
                'has_dib': 'dib' in params,
                'keyword': keyword,
                'asin': asin,
                'method': 'requests',
                'note': 'Search result link'
            }
        
        # Last resort: construct product link
        product_link = f"https://www.amazon.com/dp/{asin}"
        
        return {
            'success': True,
            'found': True,
            'full_link': product_link,
            'params': {},
            'rank': rank_info['rank'] if rank_info else 'N/A',
            'page': rank_info['page'] if rank_info else 0,
            'position': rank_info['position'] if rank_info else 0,
            'has_dib': False,
            'keyword': keyword,
            'asin': asin,
            'method': 'requests',
            'note': 'Direct product link (not found in search)'
        }
    
    def get_real_link_direct(self, asin: str) -> dict:
        """Get real link by directly visiting product page (no search needed)"""
        if not self.playwright_available:
            return {
                'success': False,
                'error': 'Playwright not installed',
                'install_guide': {
                    'title': '需要安装 Playwright',
                    'steps': [
                        '1. 安装 Python（https://www.python.org/downloads/）',
                        '2. 打开命令提示符（CMD）',
                        '3. 运行: pip install playwright',
                        '4. 运行: playwright install chromium',
                        '5. 重新启动本软件'
                    ]
                }
            }
        
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {'success': False, 'error': 'Playwright not installed'}
        
        asin = asin.upper().strip()
        
        try:
            playwright = sync_playwright().start()
            
            browser = playwright.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Directly visit product page
            product_url = f"https://www.amazon.com/dp/{asin}"
            page.goto(product_url, timeout=60000, wait_until='domcontentloaded')
            time.sleep(3)  # Wait for JavaScript to generate dib
            
            # Get the final URL (should have dib parameter)
            final_url = page.url
            parsed = urlparse(final_url)
            params = parse_qs(parsed.query)
            
            browser.close()
            playwright.stop()
            
            return {
                'success': True,
                'found': True,
                'full_link': final_url,
                'params': {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                'has_dib': 'dib' in params,
                'asin': asin,
                'method': 'direct',
                'note': 'Direct product page access'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Direct access failed: {str(e)}'}
    
    def get_real_link(self, keyword: str, asin: str, max_pages: int = 5) -> dict:
        """Get real link with dib (try search first, then direct access)"""
        # Step 1: Try to find product rank via search
        simple_result = self.get_real_link_simple(keyword, asin, max_pages)
        rank_info = None
        if simple_result.get('success') and simple_result.get('found'):
            rank_info = {
                'rank': simple_result.get('rank'),
                'page': simple_result.get('page'),
                'position': simple_result.get('position')
            }
            # If requests got dib, return immediately
            if simple_result.get('has_dib'):
                return simple_result
        
        # Step 2: If not found in search or no dib, try direct access
        direct_result = self.get_real_link_direct(asin)
        if direct_result.get('success') and direct_result.get('found'):
            # Add rank info if we found it earlier
            if rank_info:
                direct_result['rank'] = rank_info['rank']
                direct_result['page'] = rank_info['page']
                direct_result['position'] = rank_info['position']
            else:
                direct_result['rank'] = 'N/A'
                direct_result['page'] = 0
                direct_result['position'] = 0
            return direct_result
        
        # Step 3: If direct access also failed, return search result or error
        if simple_result.get('success'):
            return simple_result
        return direct_result


# ============== 前端 HTML ==============

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>亚马逊链接生成器</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 700px;
            width: 100%;
        }
        h1 { text-align: center; color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; font-size: 14px; }
        input[type="text"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus { outline: none; border-color: #667eea; }
        .hint { font-size: 12px; color: #999; margin-top: 5px; }
        .mode-selector { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .mode-btn {
            flex: 1; min-width: 100px; padding: 12px;
            border: 2px solid #e0e0e0; background: white;
            border-radius: 10px; cursor: pointer;
            transition: all 0.3s; font-size: 14px;
        }
        .mode-btn.active { border-color: #667eea; background: #f0f4ff; color: #667eea; }
        .mode-btn:hover { border-color: #667eea; }
        .mode-content { display: none; }
        .mode-content.active { display: block; }
        .btn {
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; border-radius: 10px;
            font-size: 16px; font-weight: 600; cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 10px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        .btn-secondary { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
        .btn-warning { background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); color: #333; }
        .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; display: none; }
        .result.show { display: block; }
        .result-title { font-weight: 600; color: #333; margin-bottom: 10px; font-size: 14px; }
        .result-link {
            background: white; padding: 12px; border-radius: 8px;
            border: 1px solid #e0e0e0; word-break: break-all;
            font-size: 13px; color: #667eea; margin-bottom: 10px;
            font-family: monospace;
        }
        .copy-btn {
            background: #667eea; color: white; border: none;
            padding: 8px 16px; border-radius: 6px; cursor: pointer;
            font-size: 13px; margin-right: 10px; margin-bottom: 10px;
        }
        .copy-btn:hover { background: #5a6fd6; }
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.show { display: block; }
        .spinner {
            border: 3px solid #f3f3f3; border-top: 3px solid #667eea;
            border-radius: 50%; width: 40px; height: 40px;
            animation: spin 1s linear infinite; margin: 0 auto 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .status { margin-top: 10px; padding: 10px; border-radius: 8px; font-size: 13px; display: none; }
        .status.show { display: block; }
        .status.success { background: #d4edda; color: #155724; }
        .status.error { background: #f8d7da; color: #721c24; }
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        @media (max-width: 600px) { .two-col { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 亚马逊链接生成器</h1>
        <p class="subtitle">生成带追踪参数的亚马逊产品链接</p>

        <div class="mode-selector">
            <button class="mode-btn active" onclick="switchMode('simple')">简单模式</button>
            <button class="mode-btn" onclick="switchMode('search')">搜索模式</button>
            <button class="mode-btn" onclick="switchMode('full')">完整模拟</button>
            <button class="mode-btn" onclick="switchMode('rank')">排名查询</button>
        </div>

        <div id="simple-mode" class="mode-content active">
            <div class="form-group">
                <label for="simple-asin">ASIN</label>
                <input type="text" id="simple-asin" placeholder="例如: B0GPVLJC3B">
                <p class="hint">亚马逊产品唯一标识，10位字符</p>
            </div>
            <div class="form-group">
                <label for="simple-tag">联盟标签 (可选)</label>
                <input type="text" id="simple-tag" placeholder="例如: jackyfan5-20" value="jackyfan5-20">
            </div>
        </div>

        <div id="search-mode" class="mode-content">
            <div class="form-group">
                <label for="search-keyword">搜索关键词</label>
                <input type="text" id="search-keyword" placeholder="例如: deer camera">
            </div>
            <div class="form-group">
                <label for="search-asin">目标 ASIN</label>
                <input type="text" id="search-asin" placeholder="例如: B0GPVLJC3B">
            </div>
            <div class="two-col">
                <div class="form-group">
                    <label for="search-tag">联盟标签</label>
                    <input type="text" id="search-tag" placeholder="例如: jackyfan5-20" value="jackyfan5-20">
                </div>
                <div class="form-group">
                    <label for="search-rank">搜索排名</label>
                    <input type="text" id="search-rank" placeholder="例如: 1-1" value="1-1">
                </div>
            </div>
        </div>

        <div id="full-mode" class="mode-content">
            <div class="form-group">
                <label for="full-title">产品标题</label>
                <input type="text" id="full-title" placeholder="例如: Trail Camera Night Vision">
            </div>
            <div class="form-group">
                <label for="full-asin">ASIN</label>
                <input type="text" id="full-asin" placeholder="例如: B0GPVLJC3B">
            </div>
            <div class="form-group">
                <label for="full-keyword">搜索关键词</label>
                <input type="text" id="full-keyword" placeholder="例如: deer camera">
            </div>
            <div class="two-col">
                <div class="form-group">
                    <label for="full-rank">搜索排名</label>
                    <input type="text" id="full-rank" placeholder="例如: 1-1" value="1-1">
                </div>
                <div class="form-group">
                    <label for="full-tag">联盟标签</label>
                    <input type="text" id="full-tag" placeholder="例如: jackyfan5-20" value="jackyfan5-20">
                </div>
            </div>
        </div>

        <div id="rank-mode" class="mode-content">
            <div class="form-group">
                <label for="rank-keyword">搜索关键词</label>
                <input type="text" id="rank-keyword" placeholder="例如: deer camera">
            </div>
            <div class="form-group">
                <label for="rank-asin">目标 ASIN</label>
                <input type="text" id="rank-asin" placeholder="例如: B0GPVLJC3B">
            </div>
            <div class="form-group">
                <label for="rank-max-pages">最大搜索页数</label>
                <input type="text" id="rank-max-pages" placeholder="例如: 5" value="5">
            </div>
        </div>

        <button class="btn" onclick="generateLink()">生成链接</button>
        <button class="btn btn-secondary" id="real-link-btn" onclick="fetchRealLink()" style="display:none;">获取真实链接（带dib）</button>
        <button class="btn btn-warning" id="check-rank-btn" onclick="checkRank()" style="display:none;">查询排名</button>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p id="loading-text">正在处理...</p>
        </div>

        <div class="status" id="status"></div>

        <div class="result" id="result">
            <div class="result-title">生成的链接：</div>
            <div class="result-link" id="result-link"></div>
            <button class="copy-btn" onclick="copyLink()">复制链接</button>
            <div id="real-link-section" style="display:none; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0;">
                <div class="result-title">真实链接：</div>
                <div class="result-link" id="real-link"></div>
                <button class="copy-btn" onclick="copyRealLink()">复制真实链接</button>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'simple';

        function switchMode(mode) {
            currentMode = mode;
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.mode-content').forEach(content => content.classList.remove('active'));
            document.getElementById(mode + '-mode').classList.add('active');
            document.getElementById('real-link-btn').style.display = (mode === 'search' || mode === 'full') ? 'block' : 'none';
            document.getElementById('check-rank-btn').style.display = mode === 'rank' ? 'block' : 'none';
            document.querySelector('.btn:not(.btn-secondary):not(.btn-warning)').style.display = mode === 'rank' ? 'none' : 'block';
            document.getElementById('result').classList.remove('show');
            document.getElementById('status').classList.remove('show');
        }

        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = 'status show ' + type;
        }

        function showLoading(text) {
            document.getElementById('loading-text').textContent = text;
            document.getElementById('loading').classList.add('show');
            document.getElementById('result').classList.remove('show');
            document.getElementById('status').classList.remove('show');
        }

        function hideLoading() {
            document.getElementById('loading').classList.remove('show');
        }

        async function generateLink() {
            let data = {};
            if (currentMode === 'simple') {
                data.asin = document.getElementById('simple-asin').value.trim();
                data.tag = document.getElementById('simple-tag').value.trim();
            } else if (currentMode === 'search') {
                data.keyword = document.getElementById('search-keyword').value.trim();
                data.asin = document.getElementById('search-asin').value.trim();
                data.tag = document.getElementById('search-tag').value.trim();
                data.rank = document.getElementById('search-rank').value.trim();
            } else if (currentMode === 'full') {
                data.title = document.getElementById('full-title').value.trim();
                data.asin = document.getElementById('full-asin').value.trim();
                data.keyword = document.getElementById('full-keyword').value.trim();
                data.rank = document.getElementById('full-rank').value.trim();
                data.tag = document.getElementById('full-tag').value.trim();
            }
            if (!data.asin) { showStatus('请输入 ASIN', 'error'); return; }
            
            showLoading('正在生成链接...');
            try {
                const result = await window.pywebview.api.generate_link(currentMode, data);
                hideLoading();
                if (result.success) {
                    document.getElementById('result-link').textContent = result.link;
                    document.getElementById('result').classList.add('show');
                    document.getElementById('real-link-section').style.display = 'none';
                } else {
                    showStatus(result.error || '生成失败', 'error');
                }
            } catch (error) {
                hideLoading();
                showStatus('错误: ' + error.message, 'error');
            }
        }

        async function fetchRealLink() {
            let keyword, asin;
            if (currentMode === 'search') {
                keyword = document.getElementById('search-keyword').value.trim();
                asin = document.getElementById('search-asin').value.trim();
            } else {
                keyword = document.getElementById('full-keyword').value.trim();
                asin = document.getElementById('full-asin').value.trim();
            }
            if (!keyword || !asin) { showStatus('请先填写关键词和 ASIN', 'error'); return; }
            
            showLoading('正在获取真实链接...');
            try {
                const result = await window.pywebview.api.get_real_link(keyword, asin, 5);
                hideLoading();
                if (result.success) {
                    if (result.found) {
                        document.getElementById('real-link').textContent = result.full_link;
                        document.getElementById('real-link-section').style.display = 'block';
                        showStatus('找到产品！排名: ' + result.rank, 'success');
                    } else {
                        showStatus(result.message || '未找到产品', 'error');
                    }
                } else {
                    showStatus(result.error || '获取失败', 'error');
                }
            } catch (error) {
                hideLoading();
                showStatus('错误: ' + error.message, 'error');
            }
        }

        async function checkRank() {
            const keyword = document.getElementById('rank-keyword').value.trim();
            const asin = document.getElementById('rank-asin').value.trim();
            const maxPages = parseInt(document.getElementById('rank-max-pages').value) || 5;
            if (!keyword || !asin) { showStatus('请输入关键词和 ASIN', 'error'); return; }
            
            showLoading('正在查询排名...');
            try {
                const result = await window.pywebview.api.check_rank_simple(keyword, asin, maxPages);
                hideLoading();
                if (result.success) {
                    if (result.found) {
                        showStatus('找到产品！排名: ' + result.rank, 'success');
                    } else {
                        showStatus(result.message || '未找到产品', 'error');
                    }
                } else {
                    showStatus(result.error || '查询失败', 'error');
                }
            } catch (error) {
                hideLoading();
                showStatus('错误: ' + error.message, 'error');
            }
        }

        function copyLink() {
            const link = document.getElementById('result-link').textContent;
            navigator.clipboard.writeText(link).then(() => {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '已复制!';
                setTimeout(() => btn.textContent = '复制链接', 2000);
            });
        }

        function copyRealLink() {
            const link = document.getElementById('real-link').textContent;
            navigator.clipboard.writeText(link).then(() => {
                const btn = document.querySelectorAll('.copy-btn')[1];
                btn.textContent = '已复制!';
                setTimeout(() => btn.textContent = '复制真实链接', 2000);
            });
        }
    </script>
</body>
</html>'''


# ============== 主程序 ==============

def main():
    """主函数"""
    # 创建 API 实例
    api = AmazonAPI()
    
    # 创建窗口
    window = webview.create_window(
        title='亚马逊链接生成器',
        html=HTML_CONTENT,
        js_api=api,
        width=900,
        height=800,
        resizable=True,
        min_size=(700, 600)
    )
    
    # 启动应用
    webview.start(debug=False)


if __name__ == '__main__':
    main()
