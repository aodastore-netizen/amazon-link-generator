#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排名查询模块
查询指定ASIN在亚马逊搜索结果中的排名位置
"""

import requests
import time
import random
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from typing import Optional, Dict, Any


class RankChecker:
    """亚马逊产品搜索排名查询类"""
    
    AMAZON_BASE_URL = "https://www.amazon.com/s"
    ITEMS_PER_PAGE = 48
    MAX_PAGES = 10
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]
    
    def __init__(self):
        """初始化请求会话"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """配置请求会话"""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session.headers.update(headers)
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """添加随机延迟"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """构建搜索URL"""
        encoded_keyword = quote_plus(keyword)
        return f"{self.AMAZON_BASE_URL}?k={encoded_keyword}&page={page}"
    
    def _extract_asin_from_element(self, element) -> Optional[str]:
        """从HTML元素中提取ASIN"""
        asin = element.get("data-asin")
        if asin:
            return asin
        
        link = element.find("a", href=True)
        if link:
            href = link.get("href", "")
            match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', href)
            if match:
                return match.group(1)
        
        return None
    
    def _search_page(self, keyword: str, page: int) -> tuple:
        """搜索指定页面"""
        url = self._build_search_url(keyword, page)
        self.session.headers.update({"User-Agent": self._get_random_user_agent()})
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                return None, False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item',
                '[data-asin]',
            ]
            
            products = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        asin = self._extract_asin_from_element(element)
                        if asin and len(asin) == 10:
                            products.append(asin)
                    break
            
            return products, True
            
        except requests.exceptions.RequestException as e:
            return None, False
    
    def find_product_rank(self, keyword: str, target_asin: str, max_pages: int = 5) -> Dict[str, Any]:
        """
        查找产品在搜索结果中的排名
        
        返回：
            包含查询结果的字典
        """
        target_asin = target_asin.upper().strip()
        
        for page in range(1, min(max_pages, self.MAX_PAGES) + 1):
            products, success = self._search_page(keyword, page)
            
            if not success:
                continue
            
            if products is None:
                continue
            
            for position, asin in enumerate(products, start=1):
                if asin.upper() == target_asin:
                    overall_position = (page - 1) * self.ITEMS_PER_PAGE + position
                    return {
                        'found': True,
                        'rank': f"{page}-{overall_position}",
                        'page': page,
                        'position': position,
                        'overall_position': overall_position,
                        'keyword': keyword,
                        'asin': target_asin
                    }
            
            if page < max_pages:
                self._random_delay(2.0, 5.0)
        
        return {
            'found': False,
            'keyword': keyword,
            'asin': target_asin,
            'message': f'在前{max_pages}页中未找到该产品'
        }
