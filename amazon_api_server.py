#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊链接生成器后端 API

功能：
1. 提供 HTTP API 供前端调用
2. 查询产品搜索排名
3. 获取带 dib 的真实亚马逊链接
4. 生成各种格式的推广链接

启动方式：
    python amazon_api_server.py
    
默认端口：5000
访问地址：http://localhost:5000

作者：AI Assistant
日期：2026-03-23
"""

import json
import time
import random
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, quote_plus
from typing import Optional, Dict, Any

from flask import Flask, request, jsonify
from flask_cors import CORS

# 尝试导入 Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("警告：Playwright 未安装，真实链接获取功能将不可用")
    print("安装命令：pip install playwright && playwright install chromium")

# 尝试导入 BeautifulSoup
try:
    from bs4 import BeautifulSoup
    import requests
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # 允许跨域请求


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


# ============== 排名查询（简化版，不使用浏览器） ==============

def check_rank_simple(keyword: str, asin: str, max_pages: int = 5) -> Optional[Dict]:
    """
    简化的排名查询（使用 requests）
    注意：可能会被亚马逊反爬拦截
    """
    if not BS4_AVAILABLE:
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    
    asin = asin.upper().strip()
    session = requests.Session()
    session.headers.update(headers)
    
    for page in range(1, max_pages + 1):
        try:
            # 构建搜索 URL
            url = f"https://www.amazon.com/s?k={quote_plus(keyword)}&page={page}"
            
            response = session.get(url, timeout=30)
            
            if response.status_code != 200:
                continue
            
            # 检查是否被拦截
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                return {
                    'error': '被亚马逊反爬拦截，请使用真实浏览器模式',
                    'needs_browser': True
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找产品
            products = soup.select('[data-component-type="s-search-result"]')
            
            for position, product in enumerate(products, start=1):
                link = product.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    found_asin = extract_asin_from_url(href)
                    if found_asin == asin:
                        overall_position = (page - 1) * 48 + position
                        return {
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
        'found': False,
        'keyword': keyword,
        'asin': asin,
        'message': f'在前{max_pages}页中未找到该产品'
    }


# ============== 真实链接获取（使用 Playwright） ==============

class RealLinkFetcher:
    """真实链接获取器"""
    
    def __init__(self):
        self.browser = None
        self.page = None
        
    def start(self):
        """启动浏览器"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright 未安装")
            
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = context.new_page()
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
    def stop(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            
    def fetch_real_link(self, keyword: str, target_asin: str, max_pages: int = 5) -> Optional[Dict]:
        """获取真实链接"""
        if not self.page:
            raise RuntimeError("浏览器未启动")
            
        target_asin = target_asin.upper().strip()
        
        # 访问亚马逊
        self.page.goto('https://www.amazon.com', wait_until='networkidle')
        time.sleep(random.uniform(2, 4))
        
        # 搜索
        self.page.locator('#twotabsearchtextbox').fill(keyword)
        time.sleep(random.uniform(0.5, 1.5))
        self.page.locator('#nav-search-submit-button').click()
        self.page.wait_for_load_state('networkidle')
        time.sleep(random.uniform(3, 5))
        
        # 逐页搜索
        for page_num in range(1, max_pages + 1):
            product_links = self.page.locator('[data-component-type="s-search-result"] h2 a').all()
            
            for position, link in enumerate(product_links, start=1):
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                found_asin = extract_asin_from_url(href)
                if found_asin == target_asin:
                    # 构建完整 URL
                    full_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                    
                    # 解析参数
                    parsed = urlparse(full_url)
                    params = parse_qs(parsed.query)
                    
                    # 构建基础链接
                    base_link = full_url.replace(found_asin, '{ASIN}')
                    
                    return {
                        'found': True,
                        'full_link': full_url,
                        'base_link': base_link,
                        'params': {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                        'rank': f"{page_num}-{position}",
                        'page': page_num,
                        'position': position,
                        'has_dib': 'dib' in params,
                        'keyword': keyword,
                        'asin': target_asin
                    }
            
            # 翻页
            if page_num < max_pages:
                next_button = self.page.locator('a.s-pagination-next')
                if next_button.count() > 0 and next_button.is_visible():
                    next_button.click()
                    self.page.wait_for_load_state('networkidle')
                    time.sleep(random.uniform(3, 5))
                else:
                    break
        
        return {
            'found': False,
            'keyword': keyword,
            'asin': target_asin,
            'message': f'在前{max_pages}页中未找到该产品'
        }


# ============== API 路由 ==============

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'service': '亚马逊链接生成器 API',
        'version': '1.0.0',
        'endpoints': [
            '/api/check-rank - 查询产品排名',
            '/api/get-real-link - 获取真实链接（带dib）',
            '/api/generate-link - 生成推广链接'
        ]
    })


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
    
    # 使用简化版查询
    result = check_rank_simple(keyword, asin, max_pages)
    
    if result and result.get('needs_browser'):
        return jsonify({
            'error': result['error'],
            'needs_browser': True,
            'alternative': '请使用 /api/get-real-link 接口'
        }), 429
    
    return jsonify(result or {'error': '查询失败'})


@app.route('/api/get-real-link', methods=['POST'])
def api_get_real_link():
    """获取真实链接（带dib）"""
    if not PLAYWRIGHT_AVAILABLE:
        return jsonify({
            'error': 'Playwright 未安装',
            'install_command': 'pip install playwright && playwright install chromium'
        }), 503
    
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
    
    fetcher = RealLinkFetcher()
    
    try:
        fetcher.start()
        result = fetcher.fetch_real_link(keyword, asin, max_pages)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        fetcher.stop()


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
        return jsonify({'error': '不支持的 mode 参数'}), 400
    
    return jsonify({
        'link': link,
        'asin': asin,
        'tag': tag,
        'mode': mode
    })


# ============== 启动服务器 ==============

if __name__ == '__main__':
    print("="*60)
    print("🚀 亚马逊链接生成器 API 服务")
    print("="*60)
    print(f"\n访问地址: http://localhost:5000")
    print(f"API 文档: http://localhost:5000/")
    print("\n可用接口:")
    print("  POST /api/check-rank      - 查询产品排名")
    print("  POST /api/get-real-link   - 获取真实链接（带dib）")
    print("  POST /api/generate-link   - 生成推广链接")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
