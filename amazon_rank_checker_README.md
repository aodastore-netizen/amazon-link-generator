# Amazon Rank Checker - 亚马逊产品搜索排名查询工具

## 📋 功能介绍

查询指定ASIN在亚马逊搜索结果中的排名位置，支持最多搜索前10页。

## 🚀 使用方法

### 1. 命令行使用

```bash
# 基本用法
python amazon_rank_checker.py --keyword "deer camera" --asin "B0GPVLJC3B"

# 简写形式
python amazon_rank_checker.py -k "deer camera" -a "B0GPVLJC3B"
```

### 2. 作为模块导入

```python
from amazon_rank_checker import AmazonRankChecker

# 创建查询器实例
checker = AmazonRankChecker()

# 查询排名
rank = checker.find_product_rank("deer camera", "B0GPVLJC3B")

if rank:
    print(f"产品排名: {rank}")  # 输出: "8-198"
else:
    print("未找到产品")
```

## 📦 依赖安装

```bash
pip install requests beautifulsoup4
```

## 🔧 输出格式

- **找到产品**: 返回 `"页码-总位置"` 格式，如 `"8-198"`
  - 页码：产品所在的搜索结果页
  - 总位置：从第1页开始计算的累计位置
  
- **未找到产品**: 返回 `None`

## 🌐 网页集成

### Flask 集成示例

```python
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
        return jsonify({'error': '缺少必要参数'}), 400
    
    rank = checker.find_product_rank(keyword, asin)
    
    return jsonify({
        'keyword': keyword,
        'asin': asin,
        'rank': rank,
        'found': rank is not None
    })
```

### FastAPI 集成示例

```python
from fastapi import FastAPI
from pydantic import BaseModel
from amazon_rank_checker import AmazonRankChecker

app = FastAPI()
checker = AmazonRankChecker()

class RankRequest(BaseModel):
    keyword: str
    asin: str

@app.post("/api/check-rank")
async def check_rank(req: RankRequest):
    rank = checker.find_product_rank(req.keyword, req.asin)
    return {
        'keyword': req.keyword,
        'asin': req.asin,
        'rank': rank,
        'found': rank is not None
    }
```

### 前端调用示例

```javascript
// JavaScript/fetch 调用
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
        console.log(`排名: ${data.rank}`);  // "8-198"
    } else {
        console.log('未找到产品');
    }
});
```

## ⚙️ 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_PAGES` | 10 | 最大搜索页数 |
| `ITEMS_PER_PAGE` | 48 | 每页产品数量 |
| 请求延迟 | 2-5秒 | 随机延迟避免反爬 |

## 🛡️ 反爬措施

1. **随机User-Agent**: 每次请求随机选择浏览器UA
2. **请求延迟**: 页面间添加2-5秒随机延迟
3. **请求头模拟**: 完整的浏览器请求头
4. **会话保持**: 使用Session维持连接状态

## ⚠️ 注意事项

1. **亚马逊反爬**: 频繁请求可能触发验证码，建议：
   - 控制查询频率
   - 使用代理IP池
   - 考虑使用亚马逊官方API (Product Advertising API)

2. **页面结构变化**: 亚马逊页面结构可能变化，需要定期更新选择器

3. **地区差异**: 默认查询美国站(amazon.com)，其他站点需修改 `AMAZON_BASE_URL`

## 📁 文件结构

```
.
├── amazon_rank_checker.py    # 主程序文件
├── README.md                  # 使用说明
└── requirements.txt           # 依赖列表（可选）
```

## 📝 示例输出

```
🔍 开始搜索: 关键词='deer camera', ASIN='B0GPVLJC3B'
📄 正在搜索第 1/10 页...
   第1页未找到，该页共48个产品
📄 正在搜索第 2/10 页...
   第2页未找到，该页共48个产品
...
📄 正在搜索第 8/10 页...
✅ 找到产品！排名: 8-198

🎉 查询成功！
   关键词: deer camera
   ASIN: B0GPVLJC3B
   排名: 8-198
```

## 🔗 相关链接

- [亚马逊产品广告API](https://affiliate-program.amazon.com/)
- [BeautifulSoup文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests文档](https://docs.python-requests.org/)
