#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
链接生成模块
生成各种格式的亚马逊推广链接
"""

import time
import random
import re
from urllib.parse import quote_plus
from typing import Dict, Any, Optional


class LinkGenerator:
    """链接生成器"""
    
    @staticmethod
    def generate_random_string(length: int) -> str:
        """生成随机字符串"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_timestamp() -> str:
        """生成Unix时间戳"""
        return str(int(time.time()))
    
    @staticmethod
    def url_friendly_title(title: str) -> str:
        """将标题转换为URL友好格式"""
        return re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().replace(' ', '-')[:80]
    
    def generate_link(self, mode: str, asin: str, tag: str = '', **kwargs) -> Dict[str, Any]:
        """
        生成链接
        
        参数：
            mode: 模式 ('simple', 'search', 'full', 'custom')
            asin: 产品ASIN
            tag: 联盟标签
            **kwargs: 其他参数
        
        返回：
            包含链接和参数的字典
        """
        # 生成参数
        crid = kwargs.get('crid') or self.generate_random_string(16)
        xpid = kwargs.get('xpid') or (self.generate_random_string(12) + self.generate_random_string(4))
        qid = kwargs.get('qid') or self.generate_timestamp()
        
        params = []
        link = ''
        
        if mode == 'simple':
            link = f"https://www.amazon.com/dp/{asin}"
            if tag:
                link += f"?tag={tag}"
                params.append({'name': 'tag', 'value': tag, 'desc': '联盟追踪标签'})
                
        elif mode == 'search':
            keyword = kwargs.get('keyword', 'product')
            rank = kwargs.get('rank', '1-1')
            encoded_keyword = quote_plus(keyword)
            sprefix = quote_plus(keyword) + '%2Caps%2C145'
            
            link = f"https://www.amazon.com/dp/{asin}/ref=sr_&sr={rank}&xpid={xpid}?crid={crid}&sprefix={sprefix}&keywords={encoded_keyword}&qid={qid}"
            
            if tag:
                link += f"&tag={tag}"
                params.append({'name': 'tag', 'value': tag, 'desc': '联盟追踪标签'})
            
            params.extend([
                {'name': 'crid', 'value': crid, 'desc': '搜索请求ID'},
                {'name': 'xpid', 'value': xpid, 'desc': '会话追踪ID'},
                {'name': 'sr', 'value': rank, 'desc': '搜索排名'},
                {'name': 'sprefix', 'value': sprefix, 'desc': '搜索前缀'},
                {'name': 'keywords', 'value': keyword, 'desc': '搜索关键词'},
                {'name': 'qid', 'value': qid, 'desc': '时间戳'}
            ])
            
        elif mode == 'full':
            title = kwargs.get('title', '')
            keyword = kwargs.get('keyword', 'product')
            rank = kwargs.get('rank', '1-1')
            
            url_title = self.url_friendly_title(title) + '/' if title else ''
            encoded_keyword = quote_plus(keyword)
            sprefix = quote_plus(keyword) + '%2Caps%2C145'
            
            link = f"https://www.amazon.com/{url_title}dp/{asin}/ref=sr_&sr={rank}&xpid={xpid}?crid={crid}&sprefix={sprefix}&keywords={encoded_keyword}&qid={qid}"
            
            if tag:
                link += f"&tag={tag}"
                params.append({'name': 'tag', 'value': tag, 'desc': '联盟追踪标签'})
            
            params.extend([
                {'name': 'crid', 'value': crid, 'desc': '搜索请求ID (16位随机)'},
                {'name': 'xpid', 'value': xpid, 'desc': '会话追踪ID (16位随机)'},
                {'name': 'sr', 'value': rank, 'desc': '搜索排名 (页码-位次)'},
                {'name': 'sprefix', 'value': sprefix, 'desc': '搜索前缀 (关键词+后缀)'},
                {'name': 'keywords', 'value': keyword, 'desc': '搜索关键词'},
                {'name': 'qid', 'value': qid, 'desc': 'Unix时间戳'},
                {'name': 'ref', 'value': 'sr_', 'desc': '来源标识 (Search Results)'}
            ])
            
            if title:
                params.append({'name': 'title', 'value': url_title, 'desc': '产品标题URL格式'})
        
        else:
            raise ValueError(f'不支持的模式: {mode}')
        
        return {
            'link': link,
            'asin': asin,
            'tag': tag,
            'mode': mode,
            'params': params
        }
