#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊真实链接获取工具

功能：通过真实搜索获取带 dib 参数的亚马逊链接
原理：
1. 使用 Selenium/Playwright 模拟真实浏览器
2. 在亚马逊执行真实搜索
3. 提取搜索结果中的链接（包含真实的 crid, xpid, dib 等参数）
4. 替换 ASIN 为目标产品

作者：AI Assistant
日期：2026-03-23
"""

import time
import random
import re
import argparse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Optional, Tuple

# 尝试导入 Playwright，如果没有则提示安装
try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("请先安装 Playwright:")
    print("  pip install playwright")
    print("  playwright install")
    exit(1)


class AmazonRealLinkFetcher:
    """
    亚马逊真实链接获取器
    
    使用 Playwright 模拟真实浏览器行为，获取带 dib 的链接
    """
    
    def __init__(self, headless: bool = True):
        """
        初始化浏览器
        
        参数：
            headless: 是否无头模式（True=不显示浏览器窗口）
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    def start(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # 创建新页面，设置 User-Agent
        context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = context.new_page()
        
        # 注入脚本隐藏 webdriver 标记
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    def stop(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            
    def _random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """随机延迟"""
        time.sleep(random.uniform(min_sec, max_sec))
        
    def search_and_get_link(self, keyword: str, target_asin: str, max_pages: int = 5) -> Optional[dict]:
        """
        搜索并获取真实链接
        
        参数：
            keyword: 搜索关键词
            target_asin: 目标产品 ASIN
            max_pages: 最大搜索页数
            
        返回：
            包含以下字段的字典：
            - full_link: 完整的真实链接
            - base_link: 基础链接（可替换ASIN）
            - params: 提取的参数（crid, xpid, dib等）
            - rank: 排名（页码-位置）
            如果未找到返回 None
        """
        if not self.page:
            raise RuntimeError("浏览器未启动，请先调用 start()")
            
        target_asin = target_asin.upper().strip()
        print(f"🔍 开始搜索: 关键词='{keyword}', ASIN='{target_asin}'")
        
        # 访问亚马逊首页
        print("🌐 正在访问亚马逊...")
        self.page.goto('https://www.amazon.com', wait_until='networkidle')
        self._random_delay(2, 4)
        
        # 输入搜索关键词
        print(f"⌨️  输入关键词: {keyword}")
        search_box = self.page.locator('#twotabsearchtextbox')
        search_box.fill(keyword)
        self._random_delay(0.5, 1.5)
        
        # 点击搜索按钮
        print("🔘 点击搜索...")
        search_button = self.page.locator('#nav-search-submit-button')
        search_button.click()
        self.page.wait_for_load_state('networkidle')
        self._random_delay(3, 5)
        
        # 逐页搜索
        for page_num in range(1, max_pages + 1):
            print(f"📄 正在搜索第 {page_num}/{max_pages} 页...")
            
            # 获取当前页所有产品链接
            product_links = self.page.locator('[data-component-type="s-search-result"] h2 a').all()
            
            for position, link in enumerate(product_links, start=1):
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                # 从链接中提取 ASIN
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if not asin_match:
                    continue
                    
                found_asin = asin_match.group(1)
                
                if found_asin == target_asin:
                    # 找到了！构建完整链接
                    print(f"✅ 找到产品！第{page_num}页第{position}位")
                    
                    # 构建完整 URL
                    full_url = f"https://www.amazon.com{href}" if href.startswith('/') else href
                    
                    # 解析链接参数
                    parsed = urlparse(full_url)
                    params = parse_qs(parsed.query)
                    
                    # 构建基础链接（可替换ASIN的模板）
                    base_link = self._build_base_link(full_url)
                    
                    rank = f"{page_num}-{position}"
                    
                    return {
                        'full_link': full_url,
                        'base_link': base_link,
                        'params': {k: v[0] if len(v) == 1 else v for k, v in params.items()},
                        'rank': rank,
                        'page': page_num,
                        'position': position
                    }
            
            print(f"   第{page_num}页未找到，该页共{len(product_links)}个产品")
            
            # 翻页
            if page_num < max_pages:
                next_button = self.page.locator('a.s-pagination-next')
                if next_button.count() > 0 and next_button.is_visible():
                    print("➡️  翻页...")
                    next_button.click()
                    self.page.wait_for_load_state('networkidle')
                    self._random_delay(3, 5)
                else:
                    print("⚠️  没有下一页了")
                    break
        
        print(f"❌ 在前{max_pages}页中未找到产品")
        return None
        
    def _build_base_link(self, full_url: str) -> str:
        """
        构建基础链接模板
        
        将链接中的 ASIN 替换为占位符，方便后续替换
        """
        # 提取路径中的 ASIN
        asin_match = re.search(r'(/dp/)([A-Z0-9]{10})', full_url)
        if asin_match:
            base = full_url.replace(asin_match.group(2), '{ASIN}')
            return base
        return full_url
        
    def generate_link_for_asin(self, base_link: str, new_asin: str) -> str:
        """
        使用基础链接模板生成新链接
        
        参数：
            base_link: 基础链接模板（包含 {ASIN} 占位符）
            new_asin: 新的 ASIN
            
        返回：
            替换后的完整链接
        """
        return base_link.replace('{ASIN}', new_asin.upper().strip())


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='获取亚马逊真实搜索链接（带 dib 参数）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 显示浏览器窗口（方便调试）
  python amazon_real_link_fetcher.py -k "deer camera" -a "B0GPVLJC3B" --visible
  
  # 无头模式（后台运行）
  python amazon_real_link_fetcher.py -k "pet waterer" -a "B007KL23JS"
  
  # 指定最大搜索页数
  python amazon_real_link_fetcher.py -k "wireless headphones" -a "B08WM3LMJD" --max-pages 10
        """
    )
    
    parser.add_argument('-k', '--keyword', required=True, help='搜索关键词')
    parser.add_argument('-a', '--asin', required=True, help='目标产品 ASIN')
    parser.add_argument('--visible', action='store_true', help='显示浏览器窗口（调试用）')
    parser.add_argument('--max-pages', type=int, default=5, help='最大搜索页数（默认5）')
    
    args = parser.parse_args()
    
    # 创建获取器实例
    fetcher = AmazonRealLinkFetcher(headless=not args.visible)
    
    try:
        print("🚀 启动浏览器...")
        fetcher.start()
        
        # 执行搜索
        result = fetcher.search_and_get_link(args.keyword, args.asin, args.max_pages)
        
        if result:
            print("\n" + "="*60)
            print("🎉 成功获取真实链接！")
            print("="*60)
            print(f"\n📍 排名: {result['rank']}")
            print(f"📄 页码: 第{result['page']}页")
            print(f"🔢 位置: 第{result['position']}位")
            print(f"\n🔗 完整链接:")
            print(f"   {result['full_link']}")
            print(f"\n📋 基础链接模板（可替换ASIN）:")
            print(f"   {result['base_link']}")
            print(f"\n📊 提取的参数:")
            for key, value in result['params'].items():
                display_value = value[:50] + '...' if len(str(value)) > 50 else value
                print(f"   {key}: {display_value}")
            
            # 检查是否有 dib
            if 'dib' in result['params']:
                print(f"\n✅ 链接包含 dib 参数！")
            else:
                print(f"\n⚠️  链接不包含 dib 参数（可能亚马逊已更新）")
                
        else:
            print("\n😔 未找到产品")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔚 关闭浏览器...")
        fetcher.stop()


if __name__ == '__main__':
    main()
