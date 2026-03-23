# 卖家精灵 API 测试脚本
# API Key: f24cf3e4f6174680b16d35d1807ceb32

import requests
import json

API_KEY = "f24cf3e4f6174680b16d35d1807ceb32"
BASE_URL = "https://api.sellersprite.com"

def test_api():
    """测试 API 连接和可用次数查询"""
    headers = {
        "secret-key": API_KEY,
        "Content-Type": "application/json;charset=utf-8",
        "x-request-id": "test-request-001"
    }
    
    try:
        # 测试 1: 查询可用次数
        print("=== 测试 1: 查询 API 可用次数 ===")
        response = requests.get(f"{BASE_URL}/v1/visits", headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 连接成功!")
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 查询失败: {response.text}")
            
    except Exception as e:
        print(f"错误: {e}")

def test_product_research():
    """测试选产品接口 - 获取选品数据"""
    headers = {
        "secret-key": API_KEY,
        "Content-Type": "application/json;charset=utf-8",
        "x-request-id": "test-request-002"
    }
    
    # 选产品参数 - 获取美国站产品
    payload = {
        "marketplace": "US",  # 美国站
        "month": "202503",    # 2025年3月数据
        "page": 1,
        "size": 8,            # 获取8款产品
        "minPrice": 10,       # 最低价格 $10
        "maxPrice": 100,      # 最高价格 $100
        "minRating": 3.5,     # 最低评分 3.5
        "variation": "N"      # 不含变体
    }
    
    try:
        print("\n=== 测试 2: 选产品接口 ===")
        response = requests.post(
            f"{BASE_URL}/v1/product/research", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "OK":
                items = data.get("data", {}).get("items", [])
                print(f"✅ 选产品接口正常!")
                print(f"获取到 {len(items)} 款产品")
                print(f"总页数: {data.get('data', {}).get('pages')}")
                print(f"总条数: {data.get('data', {}).get('total')}")
                
                if items:
                    print(f"\n=== 产品示例 ===")
                    for i, product in enumerate(items[:3], 1):  # 只显示前3款
                        print(f"\n【产品 {i}】")
                        print(f"  ASIN: {product.get('asin')}")
                        print(f"  标题: {product.get('title', '')[:60]}...")
                        print(f"  品牌: {product.get('brand')}")
                        print(f"  价格: ${product.get('price')}")
                        print(f"  月销量: {product.get('units')}")
                        print(f"  评分: {product.get('rating')} ({product.get('ratings')} 评论)")
                        print(f"  利润率: {product.get('profit')}%")
                        print(f"  类目: {product.get('nodeLabelPath')}")
            else:
                print(f"❌ 接口返回错误: {data.get('message')}")
        else:
            print(f"❌ 接口调用失败: {response.text}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_api()
    test_product_research()
