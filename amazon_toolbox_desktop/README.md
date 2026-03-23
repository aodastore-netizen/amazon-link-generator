# 亚马逊工具箱 - 桌面版

## 项目结构

```
AmazonToolbox/
├── main.py                 # 主入口（启动桌面应用）
├── app/
│   ├── __init__.py
│   ├── server.py           # Flask后端服务器
│   ├── link_generator.py   # 链接生成逻辑
│   ├── rank_checker.py     # 排名查询逻辑
│   ├── real_link_fetcher.py # 真实链接获取逻辑
│   └── templates/
│       └── index.html      # 主界面
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── requirements.txt
└── README.md
```

## 功能模块

### 1. 链接生成器
- 简单模式：基础ASIN链接
- 搜索模式：带搜索参数的链接
- 完整模拟：最接近真实亚马逊链接
- 自定义模式：完全自定义参数

### 2. 排名查询
- 查询指定ASIN在搜索结果中的排名
- 支持多页搜索（最多10页）
- 显示页码和位置

### 3. 真实链接获取
- 使用Playwright模拟真实浏览器
- 获取带dib参数的真实链接
- 支持可见/无头模式

## 打包命令

```bash
# 安装依赖
pip install -r requirements.txt

# 开发运行
python main.py

# 打包为桌面应用（macOS）
pyinstaller --windowed --onefile --name "亚马逊工具箱" --icon=icon.icns main.py

# 打包为桌面应用（Windows）
pyinstaller --windowed --onefile --name "AmazonToolbox" --icon=icon.ico main.py
```

## 依赖说明

- **Flask**: Web后端框架
- **PyWebView**: 桌面窗口（内嵌浏览器）
- **Playwright**: 浏览器自动化（获取真实链接）
- **BeautifulSoup4**: HTML解析
- **Requests**: HTTP请求
- **PyInstaller**: 打包工具
