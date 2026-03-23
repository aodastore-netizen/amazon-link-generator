# Helium 10 API 测试脚本
# API Key: 3679ovALcdEPmAb82uleZFtzKNA6guYA

import requests
import json

API_KEY = "3679ovALcdEPmAb82uleZFtzKNA6guYA"

# 尝试多个可能的端点
ENDPOINTS = [
    "https://api.helium10.com/v1",
    "https://api.helium10.com/v2",
    "https://helium10.com/api/v1",
    "https://app.helium10.com/api/v1",
]

def test_endpoint(base_url):
    """测试单个端点"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "X-Api-Key": API_KEY  # 有些API用这种方式
    }
    
    paths = ["/account", "/user", "/auth/verify", "/", "/products"]
    
    for path in paths:
        try:
            url = f"{base_url}{path}"
            print(f"\n尝试: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  状态: {response.status_code}")
            if response.status_code == 200:
                print(f"  成功！响应: {response.text[:200]}")
                return True, base_url, path
            else:
                print(f"  响应: {response.text[:100]}")
        except Exception as e:
            print(f"  错误: {e}")
    return False, None, None

if __name__ == "__main__":
    print("开始测试 Helium 10 API 端点...")
    print(f"API Key: {API_KEY[:10]}...")
    
    for endpoint in ENDPOINTS:
        success, url, path = test_endpoint(endpoint)
        if success:
            print(f"\n✅ 找到可用端点: {url}{path}")
            break
    else:
        print("\n❌ 所有端点都失败")
        print("\n可能需要:")
        print("1. 检查 API Key 是否正确")
        print("2. 确认账户有 API 访问权限")
        print("3. 查看 Helium 10 官方 API 文档获取正确端点")
