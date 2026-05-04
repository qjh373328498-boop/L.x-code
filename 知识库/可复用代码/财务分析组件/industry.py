"""
一键财报分析 - 行业标准数据库
"""

# 各行业财务指标标准值
INDUSTRY_STANDARDS = {
    "制造业": {
        "毛利率": {"min": 20, "max": 40, "avg": 30},
        "净利润率": {"min": 5, "max": 15, "avg": 10},
        "存货周转率": {"min": 4, "max": 12, "avg": 8},
        "总资产周转率": {"min": 0.5, "max": 1.2, "avg": 0.8},
        "资产负债率": {"min": 30, "max": 60, "avg": 45},
        "流动比率": {"min": 1.5, "max": 2.5, "avg": 2.0},
        "速动比率": {"min": 1.0, "max": 1.5, "avg": 1.2},
        "固定资产周转率": {"min": 2, "max": 6, "avg": 4},
        "ROE": {"min": 8, "max": 20, "avg": 14},
        "研发投入占比": {"min": 2, "max": 5, "avg": 3.5},
    },
    "科技/互联网": {
        "毛利率": {"min": 60, "max": 80, "avg": 70},
        "净利润率": {"min": 10, "max": 30, "avg": 20},
        "总资产周转率": {"min": 0.8, "max": 2.0, "avg": 1.4},
        "资产负债率": {"min": 20, "max": 50, "avg": 35},
        "流动比率": {"min": 2.0, "max": 4.0, "avg": 3.0},
        "速动比率": {"min": 1.5, "max": 3.0, "avg": 2.2},
        "ROE": {"min": 15, "max": 35, "avg": 25},
        "研发投入占比": {"min": 10, "max": 25, "avg": 17},
    },
    "零售业": {
        "毛利率": {"min": 20, "max": 30, "avg": 25},
        "净利润率": {"min": 3, "max": 10, "avg": 6},
        "存货周转率": {"min": 20, "max": 30, "avg": 25},
        "总资产周转率": {"min": 2.0, "max": 3.0, "avg": 2.5},
        "资产负债率": {"min": 30, "max": 50, "avg": 40},
        "流动比率": {"min": 1.0, "max": 1.5, "avg": 1.2},
        "速动比率": {"min": 0.5, "max": 1.0, "avg": 0.7},
        "ROE": {"min": 10, "max": 20, "avg": 15},
        "销售费用率": {"min": 10, "max": 20, "avg": 15},
    },
    "房地产": {
        "毛利率": {"min": 10, "max": 30, "avg": 20},
        "净利润率": {"min": 5, "max": 15, "avg": 10},
        "存货周转率": {"min": 0.3, "max": 0.8, "avg": 0.5},
        "总资产周转率": {"min": 0.2, "max": 0.6, "avg": 0.4},
        "资产负债率": {"min": 60, "max": 85, "avg": 75},
        "流动比率": {"min": 1.0, "max": 2.0, "avg": 1.5},
        "速动比率": {"min": 0.5, "max": 1.0, "avg": 0.7},
        "ROE": {"min": 10, "max": 25, "avg": 17},
        "拿地权益比": {"min": 60, "max": 80, "avg": 70},
        "土储倍数": {"min": 3, "max": 5, "avg": 4},
    },
    "金融业": {
        "毛利率": {"min": 30, "max": 60, "avg": 45},
        "净利润率": {"min": 15, "max": 35, "avg": 25},
        "资产负债率": {"min": 80, "max": 95, "avg": 90},
        "ROE": {"min": 10, "max": 20, "avg": 15},
        "拨备覆盖率": {"min": 150, "max": 300, "avg": 200},
        "成本收入比": {"min": 25, "max": 40, "avg": 32},
        "资本充足率": {"min": 10, "max": 15, "avg": 12.5},
        "不良贷款率": {"min": 1, "max": 2, "avg": 1.5},
    },
    "服务业": {
        "毛利率": {"min": 30, "max": 50, "avg": 40},
        "净利润率": {"min": 10, "max": 20, "avg": 15},
        "总资产周转率": {"min": 1.0, "max": 2.5, "avg": 1.7},
        "资产负债率": {"min": 20, "max": 50, "avg": 35},
        "流动比率": {"min": 1.5, "max": 2.5, "avg": 2.0},
        "速动比率": {"min": 1.0, "max": 2.0, "avg": 1.5},
        "ROE": {"min": 15, "max": 30, "avg": 22},
        "人均产出": {"min": 20, "max": 50, "avg": 35},  # 万元/人
    },
    "医药行业": {
        "毛利率": {"min": 60, "max": 90, "avg": 75},
        "净利润率": {"min": 15, "max": 30, "avg": 22},
        "存货周转率": {"min": 3, "max": 8, "avg": 5},
        "总资产周转率": {"min": 0.5, "max": 1.2, "avg": 0.8},
        "资产负债率": {"min": 20, "max": 50, "avg": 35},
        "ROE": {"min": 15, "max": 30, "avg": 22},
        "研发费用率": {"min": 10, "max": 25, "avg": 17},
    },
    "消费品": {
        "毛利率": {"min": 40, "max": 70, "avg": 55},
        "净利润率": {"min": 10, "max": 25, "avg": 17},
        "存货周转率": {"min": 5, "max": 15, "avg": 10},
        "总资产周转率": {"min": 0.8, "max": 1.8, "avg": 1.3},
        "资产负债率": {"min": 30, "max": 60, "avg": 45},
        "ROE": {"min": 15, "max": 30, "avg": 22},
        "销售费用率": {"min": 15, "max": 35, "avg": 25},
    },
}

# 行业关键词匹配
INDUSTRY_KEYWORDS = {
    "制造业": ["制造", "生产", "加工", "机械", "设备", "电子", "汽车", "化工", "材料", "重工", "轻工"],
    "科技/互联网": ["科技", "互联网", "软件", "信息", "通信", "网络", "数据", "人工智能", "芯片", "半导体"],
    "零售业": ["零售", "商业", "超市", "百货", "连锁", "贸易", "电商"],
    "房地产": ["房地产", "置业", "地产", "物业", "园区", "租赁", "房产"],
    "金融业": ["银行", "保险", "证券", "金融", "投资", "信托", "基金", "期货"],
    "服务业": ["服务", "咨询", "人力", "培训", "旅游", "酒店", "餐饮", "物流", "运输"],
    "医药行业": ["医药", "医疗", "生物", "制药", "药业", "健康", "器械"],
    "消费品": ["食品", "饮料", "服装", "家电", "日化", "消费", "用品", "白酒", "乳业"],
}


def detect_industry(company_name: str, business_description: str = "") -> str:
    """根据公司名称和业务范围检测行业"""
    text = company_name + " " + business_description
    
    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[industry] = score
    
    if max(scores.values()) == 0:
        return "未分類"
    
    return max(scores, key=scores.get)


def get_industry_standard(industry: str, ratio_name: str) -> dict:
    """获取某行业的某指标标准值"""
    if industry not in INDUSTRY_STANDARDS:
        return {"min": 0, "max": 100, "avg": 50}
    
    return INDUSTRY_STANDARDS[industry].get(
        ratio_name, 
        {"min": 0, "max": 100, "avg": 50}
    )


def evaluate_ratio(industry: str, ratio_name: str, value: float) -> tuple:
    """评估某指标在行业中的水平"""
    standard = get_industry_standard(industry, ratio_name)
    
    if value >= standard["max"]:
        return "优秀", "高于行业优秀水平"
    elif value >= standard["avg"]:
        return "良好", "高于行业平均水平"
    elif value >= standard["min"]:
        return "一般", "处于行业合理区间"
    else:
        return "较差", "低于行业最低标准"
