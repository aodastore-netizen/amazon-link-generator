#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊产品搜索排名查询工具

功能：查询指定ASIN在亚马逊搜索结果中的排名位置
作者：AI Assistant
日期：2026-03-23

使用示例：
    python amazon_rank_checker.py --keyword "deer camera" --asin "B0GPVLJC3B"
"""

import requests
import time
import random
import re
import argparse
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from typing import Optional, Tuple


class AmazonRankChecker:
    """
    亚马逊产品搜索排名查询类
    
    功能：
    - 模拟浏览器请求亚马逊搜索结果
    - 在搜索结果中查找指定ASIN
    - 返回排名位置（页码-位置）
    
    限制：
    - 最多搜索前10页
    - 添加了随机延迟以避免触发反爬
    """
    
    # 亚马逊搜索基础URL
    AMAZON_BASE_URL = "https://www.amazon.com/s"
    
    # 每页显示的产品数量（亚马逊通常为48或60）
    ITEMS_PER_PAGE = 48
    
    # 最大搜索页数
    MAX_PAGES = 10
    
    # 用户代理列表（随机选择以模拟不同浏览器）
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    ]
    
    def __init__(self):
        """初始化请求会话"""
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """
        配置请求会话
        
        设置请求头以模拟真实浏览器行为，包括：
        - 随机User-Agent
        - 接受语言
        - 引用来源
        """
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.session.headers.update(headers)
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        return random.choice(self.USER_AGENTS)
    
    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        添加随机延迟
        
        参数：
            min_seconds: 最小延迟秒数
            max_seconds: 最大延迟秒数
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _build_search_url(self, keyword: str, page: int = 1) -> str:
        """
        构建搜索URL
        
        参数：
            keyword: 搜索关键词
            page: 页码（从1开始）
        
        返回：
            完整的亚马逊搜索URL
        """
        encoded_keyword = quote_plus(keyword)
        # 计算起始位置（亚马逊使用0-based索引，每页48个产品）
        start_index = (page - 1) * self.ITEMS_PER_PAGE
        return f"{self.AMAZON_BASE_URL}?k={encoded_keyword}&page={page}&s=exact-aware-popularity-rank"
    
    def _extract_asin_from_element(self, element) -> Optional[str]:
        """
        从HTML元素中提取ASIN
        
        参数：
            element: BeautifulSoup元素
        
        返回：
            ASIN字符串，如果未找到则返回None
        """
        # 尝试从data-asin属性获取
        asin = element.get("data-asin")
        if asin:
            return asin
        
        # 尝试从data-component-id获取
        asin = element.get("data-component-id")
        if asin:
            return asin
        
        # 尝试从链接中提取
        link = element.find("a", href=True)
        if link:
            href = link.get("href", "")
            # 匹配 /dp/ASIN 或 /gp/product/ASIN 格式
            match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', href)
            if match:
                return match.group(1)
        
        return None
    
    def _search_page(self, keyword: str, page: int) -> Tuple[Optional[list], bool]:
        """
        搜索指定页面
        
        参数：
            keyword: 搜索关键词
            page: 页码
        
        返回：
            (产品列表, 是否成功)
            产品列表为包含ASIN的字符串列表
        """
        url = self._build_search_url(keyword, page)
        
        # 更新User-Agent
        self.session.headers.update({"User-Agent": self._get_random_user_agent()})
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 检查是否被验证码拦截
            if "captcha" in response.text.lower() or "robot" in response.text.lower():
                print(f"⚠️  第{page}页可能触发反爬验证，请稍后重试")
                return None, False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找产品容器
            # 亚马逊搜索结果通常使用以下选择器
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
                        if asin and len(asin) == 10:  # ASIN通常是10位字符
                            products.append(asin)
                    break
            
            return products, True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求第{page}页时出错: {e}")
            return None, False
    
    def find_product_rank(self, keyword: str, target_asin: str) -> Optional[str]:
        """
        查找产品在搜索结果中的排名
        
        参数：
            keyword: 搜索关键词
            target_asin: 目标产品ASIN（不区分大小写）
        
        返回：
            排名字符串，格式为"页码-位置"（如 "8-198"）
            如果未找到则返回None
        
        示例：
            >>> checker = AmazonRankChecker()
            >>> rank = checker.find_product_rank("deer camera", "B0GPVLJC3B")
            >>> print(rank)  # 输出: "8-198" 或 None
        """
        target_asin = target_asin.upper().strip()
        print(f"🔍 开始搜索: 关键词='{keyword}', ASIN='{target_asin}'")
        
        for page in range(1, self.MAX_PAGES + 1):
            print(f"📄 正在搜索第 {page}/{self.MAX_PAGES} 页...")
            
            products, success = self._search_page(keyword, page)
            
            if not success:
                print(f"⏭️  跳过第{page}页，继续下一页...")
                continue
            
            if products is None:
                print(f"⚠️  第{page}页未获取到产品数据")
                continue
            
            # 在当前页查找目标ASIN
            for position, asin in enumerate(products, start=1):
                if asin.upper() == target_asin:
                    # 计算总排名位置
                    overall_position = (page - 1) * self.ITEMS_PER_PAGE + position
                    result = f"{page}-{overall_position}"
                    print(f"✅ 找到产品！排名: {result}")
                    return result
            
            print(f"   第{page}页未找到，该页共{len(products)}个产品")
            
            # 添加随机延迟，避免触发反爬
            if page < self.MAX_PAGES:
                self._random_delay(2.0, 5.0)
        
        print(f"❌ 在前{self.MAX_PAGES}页中未找到产品 ASIN: {target_asin}")
        return None


def main():
    """
    命令行入口函数
    
    使用方法：
        python amazon_rank_checker.py --keyword "deer camera" --asin "B0GPVLJC3B"
    """
    parser = argparse.ArgumentParser(
        description="查询亚马逊产品搜索排名",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python amazon_rank_checker.py -k "deer camera" -a "B0GPVLJC3B"
  python amazon_rank_checker.py --keyword "wireless headphones" --asin "B08WM3LMJD"
        """
    )
    
    parser.add_argument(
        "-k", "--keyword",
        required=True,
        help="搜索关键词（如: deer camera）"
    )
    
    parser.add_argument(
        "-a", "--asin",
        required=True,
        help="产品ASIN（如: B0GPVLJC3B）"
    )
    
    args = parser.parse_args()
    
    # 创建查询器实例
    checker = AmazonRankChecker()
    
    # 执行查询
    rank = checker.find_product_rank(args.keyword, args.asin)
    
    # 输出结果
    if rank:
        print(f"\n🎉 查询成功！")
        print(f"   关键词: {args.keyword}")
        print(f"   ASIN: {args.asin}")
        print(f"   排名: {rank}")
    else:
        print(f"\n😔 未找到产品")
        print(f"   关键词: {args.keyword}")
        print(f"   ASIN: {args.asin}")
        print(f"   结果: 在前10页中未找到该产品")


# 网页集成示例代码（Flask）
"""
# 以下代码展示如何将查询功能集成到Flask网页应用中

from flask import Flask, request, jsonify
from amazon_rank_checker import AmazonRankChecker

app = Flask(__name__)
checker = AmazonRankChecker()

@app.route('/api/check-rank', methods=['POST'])
def check_rank():
    data = request.get_json()
    keyword = data.get('keyword')
    asin = data.get('asin')
    
    if not keyword or not asin:
        return jsonify({'error': '缺少必要参数: keyword 或 asin'}), 400
    
    rank = checker.find_product_rank(keyword, asin)
    
    return jsonify({
        'keyword': keyword,
        'asin': asin,
        'rank': rank,
        'found': rank is not None
    })

if __name__ == '__main__':
    app.run(debug=True)

# 前端调用示例（JavaScript/fetch）：
fetch('/api/check-rank', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        keyword: 'deer camera',
        asin: 'B0GPVLJC3B'
    })
})
.then(response => response.json())
.then(data => {
    if (data.found) {
        console.log(`排名: ${data.rank}`);  // 输出: "8-198"
    } else {
        console.log('未找到产品');
    }
});
"""


# FastAPI集成示例
"""
# 以下代码展示如何将查询功能集成到FastAPI应用中

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from amazon_rank_checker import AmazonRankChecker

app = FastAPI(title="亚马逊排名查询API")
checker = AmazonRankChecker()

class RankCheckRequest(BaseModel):
    keyword: str
    asin: str

class RankCheckResponse(BaseModel):
    keyword: str
    asin: str
    rank: str | None
    found: bool

@app.post("/api/check-rank", response_model=RankCheckResponse)
async def check_rank(request: RankCheckRequest):
    rank = checker.find_product_rank(request.keyword, request.asin)
    return RankCheckResponse(
        keyword=request.keyword,
        asin=request.asin,
        rank=rank,
        found=rank is not None
    )

# 运行: uvicorn main:app --reload
"""


if __name__ == "__main__":
    main()
