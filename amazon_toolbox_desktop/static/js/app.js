/**
 * 亚马逊工具箱 - 前端应用
 */

// API 基础URL
const API_BASE = '';

// 当前模式
let currentMode = 'simple';

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initLinkGenerator();
    initRankChecker();
    initRealLinkFetcher();
    checkSystemStatus();
});

// ==================== 导航 ====================

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.dataset.tab;
            
            // 更新导航状态
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // 切换内容
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// ==================== 链接生成器 ====================

function initLinkGenerator() {
    // 模式切换
    const modeBtns = document.querySelectorAll('#link-generator .mode-btn');
    const modePanels = document.querySelectorAll('#link-generator .mode-panel');
    
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const mode = btn.dataset.mode;
            currentMode = mode;
            
            // 更新按钮状态
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 切换面板
            modePanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.dataset.panel === mode) {
                    panel.classList.add('active');
                }
            });
            
            // 隐藏结果
            document.getElementById('link-result').style.display = 'none';
        });
    });
    
    // 生成按钮
    document.getElementById('generate-btn').addEventListener('click', generateLink);
    
    // 复制按钮
    document.getElementById('copy-link-btn').addEventListener('click', () => {
        const link = document.getElementById('result-link').textContent;
        copyToClipboard(link, '链接已复制！');
    });
}

async function generateLink() {
    const btn = document.getElementById('generate-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    // 获取输入值
    let data = {
        mode: currentMode,
        asin: '',
        tag: ''
    };
    
    if (currentMode === 'simple') {
        data.asin = document.getElementById('simple-asin').value.trim();
        data.tag = document.getElementById('simple-tag').value.trim();
    } else if (currentMode === 'search') {
        data.asin = document.getElementById('search-asin').value.trim();
        data.tag = document.getElementById('search-tag').value.trim();
        data.keyword = document.getElementById('search-keyword').value.trim();
        data.rank = document.getElementById('search-rank').value.trim() || '1-1';
    } else if (currentMode === 'full') {
        data.asin = document.getElementById('full-asin').value.trim();
        data.tag = document.getElementById('full-tag').value.trim();
        data.title = document.getElementById('full-title').value.trim();
        data.keyword = document.getElementById('full-keyword').value.trim();
        data.rank = document.getElementById('full-rank').value.trim() || '1-1';
    } else if (currentMode === 'custom') {
        data.asin = document.getElementById('custom-asin').value.trim();
        data.tag = document.getElementById('custom-tag').value.trim();
        data.title = document.getElementById('custom-title').value.trim();
        data.keyword = document.getElementById('custom-keywords').value.trim();
        data.crid = document.getElementById('custom-crid').value.trim();
    }
    
    // 验证
    if (!data.asin) {
        showToast('请输入 ASIN', 'error');
        return;
    }
    
    if (data.asin.length !== 10) {
        showToast('ASIN 必须是10位字符', 'error');
        return;
    }
    
    // 显示加载状态
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-flex';
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 显示结果
            document.getElementById('result-link').textContent = result.link;
            
            // 填充参数表格
            const tbody = document.getElementById('params-tbody');
            tbody.innerHTML = result.params.map(p => `
                <tr>
                    <td><code>${p.name}</code></td>
                    <td>${p.value.length > 30 ? p.value.substring(0, 30) + '...' : p.value}</td>
                    <td>${p.desc}</td>
                </tr>
            `).join('');
            
            document.getElementById('link-result').style.display = 'block';
            showToast('链接生成成功！', 'success');
        } else {
            showToast(result.error || '生成失败', 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ==================== 排名查询 ====================

function initRankChecker() {
    document.getElementById('check-rank-btn').addEventListener('click', checkRank);
}

async function checkRank() {
    const btn = document.getElementById('check-rank-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    const keyword = document.getElementById('rank-keyword').value.trim();
    const asin = document.getElementById('rank-asin').value.trim();
    const maxPages = parseInt(document.getElementById('rank-max-pages').value);
    
    if (!keyword || !asin) {
        showToast('请输入关键词和 ASIN', 'error');
        return;
    }
    
    if (asin.length !== 10) {
        showToast('ASIN 必须是10位字符', 'error');
        return;
    }
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-flex';
    
    try {
        const response = await fetch(`${API_BASE}/api/check-rank`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                keyword: keyword,
                asin: asin,
                max_pages: maxPages
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const resultDiv = document.getElementById('rank-result');
            const rankNumber = document.getElementById('rank-number');
            const rankDetails = document.getElementById('rank-details');
            
            if (result.found) {
                rankNumber.textContent = result.rank;
                rankDetails.innerHTML = `
                    <p><strong>关键词：</strong>${result.keyword}</p>
                    <p><strong>ASIN：</strong>${result.asin}</p>
                    <p><strong>页码：</strong>第 ${result.page} 页</p>
                    <p><strong>位置：</strong>第 ${result.position} 位</p>
                    <p><strong>总排名：</strong>第 ${result.overall_position} 位</p>
                `;
                showToast('查询成功！', 'success');
            } else {
                rankNumber.textContent = '未找到';
                rankDetails.innerHTML = `
                    <p><strong>关键词：</strong>${result.keyword}</p>
                    <p><strong>ASIN：</strong>${result.asin}</p>
                    <p style="color: #dc3545;">${result.message}</p>
                `;
                showToast(result.message, 'info');
            }
            
            resultDiv.style.display = 'block';
        } else {
            showToast(result.error || '查询失败', 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ==================== 真实链接获取 ====================

function initRealLinkFetcher() {
    document.getElementById('fetch-real-link-btn').addEventListener('click', fetchRealLink);
    
    document.getElementById('copy-real-link-btn').addEventListener('click', () => {
        const link = document.getElementById('real-link-text').textContent;
        copyToClipboard(link, '真实链接已复制！');
    });
}

async function fetchRealLink() {
    const btn = document.getElementById('fetch-real-link-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    const keyword = document.getElementById('real-keyword').value.trim();
    const asin = document.getElementById('real-asin').value.trim();
    const maxPages = parseInt(document.getElementById('real-max-pages').value);
    const headless = document.getElementById('real-headless').checked;
    
    if (!keyword || !asin) {
        showToast('请输入关键词和 ASIN', 'error');
        return;
    }
    
    if (asin.length !== 10) {
        showToast('ASIN 必须是10位字符', 'error');
        return;
    }
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline-flex';
    
    try {
        const response = await fetch(`${API_BASE}/api/get-real-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                keyword: keyword,
                asin: asin,
                max_pages: maxPages,
                headless: headless
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            const resultDiv = document.getElementById('real-link-result');
            
            if (result.found) {
                document.getElementById('real-link-text').textContent = result.full_link;
                
                // 链接信息
                const linkInfo = document.getElementById('link-info');
                linkInfo.innerHTML = `
                    <p><strong>排名：</strong>${result.rank}（第${result.page}页第${result.position}位）</p>
                    <p><strong>包含 dib 参数：</strong>${result.has_dib ? '✅ 是' : '❌ 否'}</p>
                `;
                
                // 参数表格
                const tbody = document.getElementById('real-params-tbody');
                tbody.innerHTML = Object.entries(result.params).map(([key, value]) => `
                    <tr>
                        <td><code>${key}</code></td>
                        <td>${typeof value === 'string' && value.length > 50 ? value.substring(0, 50) + '...' : value}</td>
                    </tr>
                `).join('');
                
                showToast('真实链接获取成功！', 'success');
            } else {
                document.getElementById('real-link-text').textContent = '未找到产品';
                document.getElementById('link-info').innerHTML = `
                    <p style="color: #dc3545;">${result.message}</p>
                `;
                document.getElementById('real-params-tbody').innerHTML = '';
                showToast(result.message, 'info');
            }
            
            resultDiv.style.display = 'block';
        } else {
            showToast(result.error || '获取失败', 'error');
        }
    } catch (error) {
        showToast('网络错误: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
}

// ==================== 工具函数 ====================

async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const result = await response.json();
        
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (result.status === 'running') {
            statusText.textContent = '系统正常';
            statusDot.style.background = 'var(--success-color)';
        } else {
            statusText.textContent = '系统异常';
            statusDot.style.background = 'var(--danger-color)';
        }
    } catch (error) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        statusText.textContent = '连接失败';
        statusDot.style.background = 'var(--danger-color)';
    }
}

function copyToClipboard(text, successMessage) {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMessage, 'success');
    }).catch(() => {
        // 降级方案
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast(successMessage, 'success');
    });
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `
        <span>${icon}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}
