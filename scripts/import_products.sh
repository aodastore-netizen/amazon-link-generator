#!/bin/bash
# 批量导入亚马逊选品数据到飞书多维表格

TOKEN="t-g1043hjjEJGHG2VCDX2RXZPV6NLLAB52AT4MDLKV"
APP_TOKEN="LZtBb66aHaXpHosP31FcezWDnmg"
TABLE_ID="tblOqWppCqrQAq4s"

# 产品数据
products=(
    'Carpet Cleaners (地毯清洁机)|家居|5|5|1|$150-300|高需求+低竞争，客单价高'
    'Household Garbage Disposal Cleaners (垃圾处理器清洁剂)|家居|5|5|0|$15-30|消耗品，复购率高'
    'Luggage Sets (行李箱套装)|家具|5|5|0|$100-250|旅行恢复，需求爆发'
    'Gun Safes (枪支保险箱)|家具|5|5|5|$200-500|美国刚需，高客单'
    'Office Supplies Organizers (办公用品收纳)|家具|5|5|0|$30-80|居家办公趋势'
    'Matcha Sets (抹茶套装)|厨房|5|4|5|$40-100|健康趋势，文化溢价'
    'Commercial Frozen Drink Machines (商用冰沙机)|厨房|5|5|3|$200-500|商用市场，利润高'
    'Free-standing Ice Makers (独立制冰机)|厨房|5|5|2|$150-300|夏季高需求'
    'Chest Expanders (扩胸器)|运动|5|5|5|$15-40|居家健身，成本低'
    'Fashion Tankini Sets (运动泳衣套装)|运动|5|5|5|$30-80|夏季爆款，时尚属性'
    'Pest Controlling Insects (害虫防治昆虫)|园艺|5|4|1|$20-50|有机园艺趋势'
    'Home Pest Lures (家用害虫诱捕器)|园艺|5|2|0|$15-40|环保安全，家庭刚需'
    'Herb Plants (香草植物)|园艺|5|2|1|$10-30|烹饪+园艺双重需求'
    'Swimming Pool Liners (泳池内衬)|园艺|5|5|2|$100-300|季节性高客单'
    'Snow Tubes (雪橇圈)|户外|5|4|5|$20-50|冬季娱乐，季节性爆款'
    'Insect Repelling Wearables (驱虫穿戴设备)|户外|5|4|0|$25-60|户外刚需，创新产品'
    'Fire Extinguishers (灭火器)|户外|5|4|5|$30-100|安全刚需，认证门槛'
    'Household Washing Machine Cleaners (洗衣机清洁剂)|家居|4|2|0|$10-25|家电维护刚需'
    'Household Toilet Cleaners (马桶清洁剂)|家居|4|4|0|$8-20|高频消耗品'
    'Replacement Faucet Mount Water Filters (水龙头滤水器替换装)|厨房|4|0|0|$15-40|消耗品，复购稳定'
    'Weight Vests (负重背心)|运动|5|4|4|$40-100|专业健身市场'
    'Pet Odor Removers (宠物除臭剂)|宠物|4|3|1|$15-35|宠物刚需'
    'Pet Bed Mats (宠物床垫)|宠物|4|2|4|$20-60|宠物舒适用品'
    'Automotive Care Products (汽车护理产品)|汽配|5|5|1|$20-80|车主刚需'
    'Automotive Diesel Additives (柴油添加剂)|汽配|5|4|0|$15-40|商用车市场'
)

# 导入每条记录
for product in "${products[@]}"; do
    IFS='|' read -r name category recommend heat compete price analysis <<< "$product"
    
    curl -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TABLE_ID}/records" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"fields\": {
                \"产品名称\": \"${name}\",
                \"单选\": \"${category}\"
            }
        }" 2>/dev/null | grep -o '"code":[0-9]*' | head -1
    
    echo "导入: ${name}"
    sleep 0.5
done

echo "导入完成！"