# 亚马逊链接生成器 - 桌面版

使用 PyWebview 构建的轻量级桌面应用。

## 功能

1. **简单模式** - 生成基础推广链接
2. **搜索模式** - 生成带搜索参数的链接
3. **完整模拟** - 生成最接近真实亚马逊格式的链接
4. **排名查询** - 查询产品在亚马逊搜索结果的排名

## 安装依赖

```bash
pip install pywebview requests beautifulsoup4 playwright
playwright install chromium
```

## 运行

```bash
python amazon_link_generator_desktop.py
```

## 打包成独立应用

### macOS

```bash
pip install py2app
python setup.py py2app
```

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed amazon_link_generator_desktop.py
```

## 注意事项

- 首次运行可能需要安装浏览器依赖
- 排名查询和真实链接功能需要网络连接
- Playwright 功能需要额外安装 Chromium 浏览器
