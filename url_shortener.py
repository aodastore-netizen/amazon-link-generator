#!/usr/bin/env python3
"""
短链服务 - Simple URL Shortener
使用 Flask + SQLite
"""

from flask import Flask, redirect, request, jsonify, render_template_string
import sqlite3
import string
import random
import os
from datetime import datetime

app = Flask(__name__)

# 数据库文件
DB_FILE = 'shortlinks.db'

# 短码长度
SHORT_CODE_LENGTH = 6

# 短码字符集（去除容易混淆的字符）
CHARSET = string.ascii_letters + string.digits
CHARSET = CHARSET.replace('l', '').replace('I', '').replace('1', '').replace('O', '').replace('0', '')


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0,
            last_accessed TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def generate_short_code():
    """生成短码"""
    return ''.join(random.choices(CHARSET, k=SHORT_CODE_LENGTH))


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# HTML 模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>短链服务</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        input[type="url"], input[type="text"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #f0f4ff;
            border-radius: 10px;
            display: none;
        }
        .result.show { display: block; }
        .short-url {
            font-size: 18px;
            color: #667eea;
            word-break: break-all;
            margin: 10px 0;
        }
        .stats {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th { color: #666; font-weight: 600; }
        .copy-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 短链服务</h1>
        
        <div class="form-group">
            <label>长链接</label>
            <input type="url" id="longUrl" placeholder="https://example.com/very/long/url..." required>
        </div>
        
        <div class="form-group">
            <label>自定义短码（可选）</label>
            <input type="text" id="customCode" placeholder="例如: abc123">
        </div>
        
        <button onclick="createShortLink()">生成短链</button>
        
        <div class="result" id="result">
            <div>短链接：</div>
            <div class="short-url" id="shortUrl"></div>
            <button class="copy-btn" onclick="copyToClipboard()">复制</button>
        </div>
        
        <div class="stats">
            <h3>最近生成的短链</h3>
            <table>
                <thead>
                    <tr>
                        <th>短码</th>
                        <th>点击</th>
                        <th>创建时间</th>
                    </tr>
                </thead>
                <tbody id="statsBody">
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        async function createShortLink() {
            const longUrl = document.getElementById('longUrl').value;
            const customCode = document.getElementById('customCode').value;
            
            if (!longUrl) {
                alert('请输入长链接');
                return;
            }
            
            const response = await fetch('/api/shorten', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: longUrl, custom_code: customCode })
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('shortUrl').textContent = data.short_url;
                document.getElementById('result').classList.add('show');
                loadStats();
            } else {
                alert('错误: ' + data.error);
            }
        }
        
        function copyToClipboard() {
            const text = document.getElementById('shortUrl').textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert('已复制到剪贴板');
            });
        }
        
        async function loadStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            const tbody = document.getElementById('statsBody');
            tbody.innerHTML = '';
            
            data.links.forEach(link => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><a href="/${link.short_code}" target="_blank">${link.short_code}</a></td>
                    <td>${link.clicks}</td>
                    <td>${link.created_at}</td>
                `;
            });
        }
        
        // 页面加载时获取统计
        loadStats();
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """首页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/<short_code>')
def redirect_to_url(short_code):
    """短链跳转"""
    conn = get_db_connection()
    link = conn.execute(
        'SELECT * FROM links WHERE short_code = ?',
        (short_code,)
    ).fetchone()
    
    if link:
        # 更新点击数
        conn.execute(
            'UPDATE links SET clicks = clicks + 1, last_accessed = ? WHERE id = ?',
            (datetime.now(), link['id'])
        )
        conn.commit()
        conn.close()
        return redirect(link['long_url'])
    
    conn.close()
    return jsonify({'error': 'Short link not found'}), 404


@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """创建短链 API"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    long_url = data['url']
    custom_code = data.get('custom_code', '').strip()
    
    # 验证 URL
    if not long_url.startswith(('http://', 'https://')):
        return jsonify({'success': False, 'error': 'Invalid URL'}), 400
    
    conn = get_db_connection()
    
    # 使用自定义短码或生成新短码
    if custom_code:
        # 检查自定义短码是否已存在
        existing = conn.execute(
            'SELECT * FROM links WHERE short_code = ?',
            (custom_code,)
        ).fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'error': 'Custom code already exists'}), 400
        
        short_code = custom_code
    else:
        # 生成唯一短码
        while True:
            short_code = generate_short_code()
            existing = conn.execute(
                'SELECT * FROM links WHERE short_code = ?',
                (short_code,)
            ).fetchone()
            if not existing:
                break
    
    # 保存到数据库
    try:
        conn.execute(
            'INSERT INTO links (short_code, long_url) VALUES (?, ?)',
            (short_code, long_url)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    conn.close()
    
    # 构建短链接
    base_url = request.host_url.rstrip('/')
    short_url = f"{base_url}/{short_code}"
    
    return jsonify({
        'success': True,
        'short_code': short_code,
        'short_url': short_url,
        'long_url': long_url
    })


@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    conn = get_db_connection()
    links = conn.execute(
        'SELECT short_code, clicks, created_at FROM links ORDER BY created_at DESC LIMIT 10'
    ).fetchall()
    conn.close()
    
    return jsonify({
        'links': [dict(link) for link in links]
    })


if __name__ == '__main__':
    init_db()
    print("短链服务启动中...")
    print("访问: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
