# 亚马逊链接生成器

生成带追踪参数的亚马逊推广链接的桌面应用。

## 下载安装

### macOS
下载 [亚马逊链接生成器-macOS.dmg](https://github.com/nan/amazon-link-generator/releases/latest)

### Windows
下载 [亚马逊链接生成器-Windows.zip](https://github.com/nan/amazon-link-generator/releases/latest)

## 功能

- **简单模式** - 快速生成基础推广链接
- **搜索模式** - 带关键词和排名参数的链接
- **完整模拟** - 最接近真实亚马逊格式的链接
- **排名查询** - 查询产品在亚马逊搜索结果的排名
- **真实链接获取** - 抓取带 dib 参数的真实亚马逊链接

## 从源码运行

```bash
pip install pywebview requests beautifulsoup4 playwright
playwright install chromium
python amazon_link_generator_desktop.py
```

## 构建

### macOS
```bash
pip install py2app
python setup.py py2app
```

### Windows
```bash
pip install pyinstaller
pyinstaller --clean amazon_link_generator.spec
```

## 自动构建

每次推送到 main 分支，GitHub Actions 会自动构建并发布新版本。

## License

MIT
