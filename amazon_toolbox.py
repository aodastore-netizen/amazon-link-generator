#!/usr/bin/env python3
"""
亚马逊工具箱 - 桌面版启动器
先安装依赖: pip3 install flask flask-cors --user
"""

import os
import sys
import json
import time
import random
import re
import threading
import webbrowser
from urllib.parse import urlparse, parse_qs, quote_plus
from typing import Dict, Any

# 检查依赖
try:
    from flask import Flask, request, jsonify, render_template_string
    from flask_cors import CORS
except ImportError:
    print("请先安装依赖:")
    print("  pip3 install flask flask-cors --user")
    print("  或: brew install flask")
    sys.exit(1)

# HTML模板
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>亚马逊工具箱</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; justify-content: center; }
        .nav-btn { padding: 12px 24px; border: none; background: rgba(255,255,255,0.2); color: white; border-radius: 8px; cursor: pointer; font-size: 14px; }
        .nav-btn:hover, .nav-btn.active { background: white; color: #667eea; }
        .card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        .tab { display: none; }
        .tab.active { display: block; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; font-size: 14px; }
        input, select { width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; }
        .hint { font-size: 12px; color: #999; margin-top: 5px; }
        .btn-primary { width: 100%; padding: 14px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        .btn-primary:disabled { opacity: 0.7; }
        .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; display: none; }
        .result.show { display: block; }
        .result-title { font-weight: 600; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .copy-btn { background: #667eea; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .result-link { background: white; padding: 12px; border-radius: 6px; border: 1px solid #e0e0e0; word-break: break-all; font-family: monospace; font-size: 13px; color: #667eea; margin-bottom: 10px; }
        .params-table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 15px; }
        .params-table th, .params-table td { padding: 8px; text-align: left; border-bottom: 1px solid #e0e0e0; }
        .mode-selector { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .mode-btn { flex: 1; min-width: 100px; padding: 10px; border: 2px solid #e0e0e0; background: white; border-radius: 8px; cursor: pointer; font-size: 13px; }
        .mode-btn.active { border-color: #667eea; background: #f0f4ff; color: #667eea; }
        .mode-panel { display: none; }
        .mode-panel.active { display: block; }
        .warning-box { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 12px; margin-bottom: 20px; font-size: 13px; color: #856404; }
        .rank-display { text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 12px; margin-bottom: 15px; }
        .rank-number { font-size: 56px; font-weight: 700; color: #667eea; }
        .checkbox-label { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .checkbox-label input { width: auto; }
        .toast { position: fixed; top: 20px; right: 20px; background: white; padding: 16px 20px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: none; z-index: 1000; }
        .toast.show { display: flex; align-items: center; gap: 10px; }
        .spinner { border: 2px solid #f3f3f3; border-top: 2px solid #667eea; border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>🛒 亚马逊工具箱</h1><p>链接生成 · 排名查询 · 真实链接获取</p></div>
        <div class="nav">
            <button class="nav-btn active" onclick="showTab('link')">🔗 链接生成器</button>
            <button class="nav-btn" onclick="showTab('rank')">📊 排名查询</button>
            <button class="nav-btn" onclick="showTab('real')">🎯 真实链接</button>
        </div>
        <div class="card tab active" id="tab-link">
            <div class="mode-selector">
                <button class="mode-btn active" onclick="setMode('simple')">简单模式</button>
                <button class="mode-btn" onclick="setMode('search')">搜索模式</button>
                <button class="mode-btn" onclick="setMode('full')">完整模拟</button>
            </div>
            <div class="mode-panel active" id="panel-simple">
                <div class="form-group"><label>ASIN</label><input type="text" id="simple-asin" placeholder="例如: B0GPVLJC3B" maxlength="10"><div class="hint">亚马逊产品唯一标识，10位字符</div></div>
                <div class="form-group"><label>联盟标签 (可选)</label><input type="text" id="simple-tag" value="jackyfan5-20"></div>
            </div>
            <div class="mode-panel" id="panel-search">
                <div class="form-group"><label>搜索关键词</label><input type="text" id="search-keyword" placeholder="例如: deer camera"></div>
                <div class="form-group"><label>目标 ASIN</label><input type="text" id="search-asin" placeholder="例如: B0GPVLJC3B" maxlength="10"></div>
                <div class="form-group"><label>搜索排名</label><input type="text" id="search-rank" value="1-1"></div>
                <div class="form-group"><label>联盟标签 (可选)</label><input type="text" id="search-tag" value="jackyfan5-20"></div>
            </div>
            <div class="mode-panel" id="panel-full">
                <div class="form-group"><label>产品标题</label><input type="text" id="full-title" placeholder="例如: Dargahou Trail Camera"></div>
                <div class="form-group"><label>ASIN</label><input type="text" id="full-asin" placeholder="例如: B0GPVLJC3B" maxlength="10"></div>
                <div class="form-group"><label>搜索关键词</label><input type="text" id="full-keyword" placeholder="例如: deer camera"></div>
                <div class="form-group"><label>搜索排名</label><input type="text" id="full-rank" value="1-1"></div>
                <div class="form-group"><label>联盟标签 (可选)</label><input type="text" id="full-tag" value="jackyfan5-20"></div>
            </div>
            <button class="btn-primary" id="generate-btn" onclick="generateLink()"><span id="generate-text">生成链接</span></button>
            <div class="result" id="link-result">
                <div class="result-title"><span>生成的链接</span><button class="copy-btn" onclick="copyLink()">复制</button></div>
                <div class="result-link" id="result-link"></div>
                <table class="params-table"><thead><tr><th>参数</th><th>值</th><th>说明</th></tr></thead><tbody id="params-tbody"></tbody></table>
            </div>
        </div>
        <div class="card tab" id="tab-rank">
            <div class="form-group"><label>搜索关键词</label><input type="text" id="rank-keyword" placeholder="例如: deer camera"></div>
            <div class="form-group"><label>产品 ASIN</label><input type="text" id="rank-asin" placeholder="例如: B0GPVLJC3B" maxlength="10"></div>
            <div class="form-group"><label>最大搜索页数</label><select id="rank-max-pages"><option value="3">3页</option><option value="5" selected>5页</option><option value="10">10页</option></select></div>
            <button class="btn-primary" id="rank-btn" onclick="checkRank()"><span id="rank-text">查询排名</span></button>
            <div class="result" id="rank-result">
                <div class="rank-display"><div class="rank-number" id="rank-number">-</div><div>排名位置</div></div>
                <div id="rank-details"></div>
            </div>
        </div>
        <div class="card tab" id="tab-real">
            <div class="warning-box">⚠️ 此功能需要安装 playwright: pip3 install playwright --user && playwright install chromium</div>
            <div class="form-group"><label>搜索关键词</label><input type="text" id="real-keyword" placeholder="例如: deer camera"></div>
            <div class="form-group"><label>目标 ASIN</label><input type="text" id="real-asin" placeholder="例如: B0GPVLJC3B" maxlength="10"></div>
            <div class="form-group"><label>最大搜索页数</label><select id="real-max-pages"><option value="3">3页</option><option value="5" selected>5页</option><option value="10">10页</option></select></div>
            <div class="form-group"><label class="checkbox-label"><input type="checkbox" id="real-headless" checked><span>后台模式运行</span></label></div>
            <button class="btn-primary" id="real-btn" onclick="fetchRealLink()"><span id="real-text">获取真实链接</span></button>
            <div class="result" id="real-result">
                <div class="result-title"><span>真实链接（从亚马逊获取）</span><button class="copy-btn" onclick="copyRealLink()">复制</button></div>
                <div class="result-link" id="real-link-text" style="background: #d4edda; border-color: #c3e6cb; color: #155724;"></div>
                <div id="real-info"></div>
            </div>
        </div>
    </div>
    <div class="toast" id="toast"></div>
    <script>
        let currentMode = 'simple', currentLink = '', currentRealLink = '';
        function showTab(tab) { document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active')); document.getElementById('tab-' + tab).classList.add('active'); event.target.classList.add('active'); }
        function setMode(mode) { currentMode = mode; document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active')); document.querySelectorAll('.mode-panel').forEach(p => p.classList.remove('active')); event.target.classList.add('active'); document.getElementById('panel-' + mode).classList.add('active'); document.getElementById('link-result').classList.remove('show'); }
        function showToast(msg, type='info') { const toast = document.getElementById('toast'); const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'; toast.innerHTML = icon + ' ' + msg; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 3000); }
        function setLoading(btnId, textId, loading) { const btn = document.getElementById(btnId), text = document.getElementById(textId); btn.disabled = loading; text.innerHTML = loading ? '<span class="spinner"></span> 处理中...' : '生成链接'; }
        async function generateLink() { let data = { mode: currentMode, asin: '', tag: '' }; if (currentMode === 'simple') { data.asin = document.getElementById('simple-asin').value.trim(); data.tag = document.getElementById('simple-tag').value.trim(); } else if (currentMode === 'search') { data.asin = document.getElementById('search-asin').value.trim(); data.tag = document.getElementById('search-tag').value.trim(); data.keyword = document.getElementById('search-keyword').value.trim(); data.rank = document.getElementById('search-rank').value.trim() || '1-1'; } else if (currentMode === 'full') { data.asin = document.getElementById('full-asin').value.trim(); data.tag = document.getElementById('full-tag').value.trim(); data.title = document.getElementById('full-title').value.trim(); data.keyword = document.getElementById('full-keyword').value.trim(); data.rank = document.getElementById('full-rank').value.trim() || '1-1'; } if (!data.asin) { showToast('请输入 ASIN', 'error'); return; } if (data.asin.length !== 10) { showToast('ASIN 必须是10位字符', 'error'); return; } setLoading('generate-btn', 'generate-text', true); try { const res = await fetch('/api/generate-link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }); const result = await res.json(); if (res.ok) { currentLink = result.link; document.getElementById('result-link').textContent = result.link; document.getElementById('params-tbody').innerHTML = result.params.map(p => `<tr><td><code>${p.name}</code></td><td>${p.value.substring(0,30)}${p.value.length>30?'...':''}</td><td>${p.desc}</td></tr>`).join(''); document.getElementById('link-result').classList.add('show'); showToast('链接生成成功！', 'success'); } else { showToast(result.error || '生成失败', 'error'); } } catch (e) { showToast('网络错误', 'error'); } setLoading('generate-btn', 'generate-text', false); }
        async function checkRank() { const keyword = document.getElementById('rank-keyword').value.trim(), asin = document.getElementById('rank-asin').value.trim(), maxPages = parseInt(document.getElementById('rank-max-pages').value); if (!keyword || !asin) { showToast('请输入关键词和 ASIN', 'error'); return; } if (asin.length !== 10) { showToast('ASIN 必须是10位字符', 'error'); return; } setLoading('rank-btn', 'rank-text', true); try { const res = await fetch('/api/check-rank', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ keyword, asin, max_pages: maxPages }) }); const result = await res.json(); if (res.ok) { if (result.found) { document.getElementById('rank-number').textContent = result.rank; document.getElementById('rank-details').innerHTML = `<p><strong>关键词：</strong>${result.keyword}</p><p><strong>ASIN：</strong>${result.asin}</p><p><strong>页码：</strong>第 ${result.page} 页</p><p><strong>位置：</strong>第 ${result.position} 位</p>`; showToast('查询成功！', 'success'); } else { document.getElementById('rank-number').textContent = '未找到'; document.getElementById('rank-details').innerHTML = `<p style="color: #dc3545;">${result.message}</p>`; showToast(result.message, 'info'); } document.getElementById('rank-result').classList.add('show'); } else { showToast(result.error || '查询失败', 'error'); } } catch (e) { showToast('网络错误', 'error'); } setLoading('rank-btn', 'rank-text', false); }
        async function fetchRealLink() { const keyword = document.getElementById('real-keyword').value.trim(), asin = document.getElementById('real-asin').value.trim(), maxPages = parseInt(document.getElementById('real-max-pages').value), headless = document.getElementById('real-headless').checked; if (!keyword || !asin) { showToast('请输入关键词和 ASIN', 'error'); return; } if (asin.length !== 10) { showToast('ASIN 必须是10位字符', 'error'); return; } setLoading('real-btn', 'real-text', true); try { const res = await fetch('/api/get-real-link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ keyword, asin, max_pages: maxPages, headless }) }); const result = await res.json(); if (res.ok) { if (result.found) { currentRealLink = result.full_link; document.getElementById('real-link-text').textContent = result.full_link; document.getElementById('real-info').innerHTML = `<p><strong>排名：</strong>${result.rank}</p><p><strong>包含 dib 参数：</strong>${result.has_dib ? '✅ 是' : '❌ 否'}</p>`; showToast('真实链接获取成功！', 'success'); } else { document.getElementById('real-link-text').textContent = '未找到产品'; document.getElementById('real-info').innerHTML = `<p style="color: #dc3545;">${result.message}</p>`; showToast(result.message, 'info'); } document.getElementById('real-result').classList.add('show'); } else { showToast(result.error || '获取失败', 'error'); } } catch (e) { showToast('网络错误: ' + e.message, 'error'); } setLoading('real-btn', 'real-text', false); }
        function copyLink() { navigator.clipboard.writeText(currentLink).then(() => showToast('链接已复制！', 'success')); }
        function copyRealLink() { navigator.clipboard.writeText(currentRealLink).then(() => showToast('真实链接已复制！', 'success')); }
    </script>
</body>
</html>'''

# 后端类
class LinkGenerator:
    @staticmethod
    def generate_random_string(length: int) -> str:
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_timestamp() -> str:
        return str(int(time.time()))
    
    @staticmethod
    def url_friendly_title(title: str) -> str:
        return re.sub(r'[^a-zA-Z0-9\s-]', '', title).strip().replace(' ', '-')[:80]
    
    def generate_link(self, mode: str, asin: str, tag: str = '', **kwargs) -> Dict[str, Any]:
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
            params.extend([{'name': 'crid', 'value': crid, 'desc': '搜索请求ID'}, {'name': 'xpid', 'value': xpid, 'desc': '会话追踪ID'}, {'name': 'sr', 'value': rank, 'desc': '搜索排名'}, {'name': 'sprefix', 'value': sprefix, 'desc': '搜索前缀'}, {'name': 'keywords', 'value': keyword, 'desc': '搜索关键词'}, {'name': 'qid', 'value': qid, 'desc': '时间戳'}])
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
            params.extend([{'name': 'crid', 'value': crid, 'desc': '搜索请求ID'}, {'name': 'xpid', 'value': xpid, 'desc': '会话追踪ID'}, {'name': 'sr', 'value': rank, 'desc': '搜索排名'}, {'name': 'sprefix', 'value': sprefix, 'desc': '搜索前缀'}, {'name': 'keywords', 'value': keyword, 'desc': '搜索关键词'}, {'name': 'qid', 'value': qid, 'desc': 'Unix时间戳'}])
        return {'link': link, 'asin': asin, 'tag': tag, 'mode': mode, 'params': params}

# 创建Flask应用
def create_app():
    app = Flask(__name__)
    CORS(app)
    link_gen = LinkGenerator()
    
    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/generate-link', methods=['POST'])
    def api_generate_link():
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400
        mode = data.get('mode', 'simple')
        asin = data.get('asin', '').strip()
        tag = data.get('tag', '').strip()
        if not asin:
            return jsonify({'error': '缺少必要参数: asin'}), 400
        if len(asin) != 10:
            return jsonify({'error': 'ASIN 必须是10位字符'}), 400
        try:
            result = link_gen.generate_link(mode=mode, asin=asin, tag=tag, title=data.get('title', ''), keyword=data.get('keyword', ''), rank=data.get('rank', '1-1'))
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/check-rank', methods=['POST'])
    def api_check_rank():
        return jsonify({'error': '排名查询需要安装 requests 和 beautifulsoup4'}), 503
    
    @app.route('/api/get-real-link', methods=['POST'])
    def api_get_real_link():
        return jsonify({'error': '真实链接获取需要安装 playwright'}), 503
    
    return app

if __name__ == '__main__':
    print("="*60)
    print("🚀 亚马逊工具箱 - 桌面版")
    print("="*60)
    print("\n正在启动...")
    print("访问地址: http://127.0.0.1:5000")
    print("\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    app = create_app()
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://127.0.0.1:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
