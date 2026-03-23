#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实链接获取模块
使用Playwright模拟浏览器获取带dib参数的真实链接
"""

import time
import random
import re
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any

# 尝试导入Playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class RealLinkFetcher:
    """真实链接获取器"""
    
    @staticmethod
    def is_available() -> bool:
        """检查Playwright是否可用"""
        return PLAYWRIGHT_AVAILABLE
    
    def __init__(self, headless: bool = True):
        """
        初始化
        
        参数：
            headless: 是否无头模式
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright未安装，请运行: pip install playwright && playwright install chromium")
        
        self.headless = headless
        self.browser = None
        self.page = None
    
    def start(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=self.headless,
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
    
    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def search_and_get_link(self, keyword: str, target_asin: str, max_pages: int = 5) -> Dict[str, Any]:
        """
        搜索并获取真实链接
        
        返回：
            包含链接信息的字典
        """
        if not self.page:
            raise RuntimeError("浏览器未启动，请先调用start()")
        
        target_asin = target_asin.upper().strip()
        
        # 访问亚马逊首页
        self.page.goto('https://www.amazon.com', wait_until='networkidle')
        self._random_delay(2, 4)
        
        # 搜索
        self.page.locator('#twotabsearchtextbox').fill(keyword)
        self._random_delay(0.5, 1.5)
        self.page.locator('#nav-search-submit-button').click()
        self.page.wait_for_load_state('networkidle')
        self._random_delay(3, 5)
        
        # 逐页搜索
        for page_num in range(1, max_pages + 1):
            product_links = self.page.locator('[data-component-type="s-search-result"] h2 a').all()
            
            for position, link in enumerate(product_links, start=1):
                href = link.get_attribute('href')
                if not href:
                    continue
                
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if not asin_match:
                    continue
                
                found_asin = asin_match.group(1)
                
                if found_asin == target_asin:
                    full_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                    
                    parsed = urlparse(full_url)
                    params = parse_qs(parsed.query)
                    
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
                    self._random_delay(3, 5)
                else:
                    break
        
        return {
            'found': False,
            'keyword': keyword,
            'asin': target_asin,
            'message': f'在前{max_pages}页中未找到该产品'
        }
