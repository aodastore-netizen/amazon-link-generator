#!/bin/bash
# 每日选品报告生成脚本
# 每天早上9:00执行

cd /Users/nan/.openclaw/workspace

echo "[$(date)] 开始生成选品日报..."

# 运行爬虫获取数据
python3 scripts/amazon_scraper.py > /tmp/daily_report.json 2>&1

if [ $? -eq 0 ]; then
    echo "[$(date)] 数据获取成功"
    
    # 生成飞书文档
    # TODO: 调用飞书API生成文档
    
    echo "[$(date)] 报告生成完成"
else
    echo "[$(date)] 数据获取失败，请检查日志"
    cat /tmp/daily_report.json
fi
