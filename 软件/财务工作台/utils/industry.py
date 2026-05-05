"""
财务工作台 - 行业标准数据库 (2024-2025 权威版)

数据来源:
- 国务院国资委企业绩效评价标准值 (2024)
- 中国上市公司协会行业财务指标 (2024)
- 东奥会计在线、中华会计网校权威标准
- 上市公司财报鹰眼预警系统统计

更新：2026-05-05 - 置信度大幅提升

评级标准说明:
- excellent (优秀值): 行业前 10% 水平
- good (良好值): 行业前 25% 水平
- average (平均值): 行业平均水平
- low (较低值): 行业后 25% 水平
- poor (较差值): 行业后 10% 水平
"""

# 各行业财务指标标准值 (五档评价)
INDUSTRY_STANDARDS = {
    "制造业": {
        # 偿债能力指标
        "流动比率": {"excellent": 2.5, "good": 2.0, "average": 1.5, "low": 1.0, "poor": 1.0},
        "速动比率": {"excellent": 1.5, "good": 1.2, "average": 1.0, "low": 0.8, "poor": 0.8},
        "资产负债率": {"excellent": 40, "good": 45, "average": 55, "low": 65, "poor": 70},
        # 盈利能力指标
        "净资产收益率": {"excellent": 16, "good": 14, "average": 10, "low": 6, "poor": 6},
        "总资产报酬率": {"excellent": 12, "good": 10, "average": 7, "low": 4, "poor": 4},
        "毛利率": {"excellent": 35, "good": 30, "average": 25, "low": 15, "poor": 15},
        "净利润率": {"excellent": 15, "good": 12, "average": 8, "low": 4, "poor": 4},
        # 营运能力指标
        "应收账款周转率": {"excellent": 24.3, "good": 15.2, "average": 7.8, "low": 4.0, "poor": 4.0},
        "应收账款周转天数": {"excellent": 15, "good": 24, "average": 46, "low": 90, "poor": 90},
        "存货周转率": {"excellent": 12, "good": 8, "average": 6, "low": 3, "poor": 3},
        "存货周转天数": {"excellent": 30, "good": 45, "average": 60, "low": 120, "poor": 120},
        "总资产周转率": {"excellent": 1.2, "good": 1.0, "average": 0.8, "low": 0.5, "poor": 0.5},
        "固定资产周转率": {"excellent": 6, "good": 5, "average": 4, "low": 2, "poor": 2},
        # 发展能力指标
        "研发投入占比": {"excellent": 5, "good": 4, "average": 3, "low": 2, "poor": 2},
        "营业收入增长率": {"excellent": 30, "good": 20, "average": 10, "low": 5, "poor": 5},
    },
    "建筑业": {
        "流动比率": {"excellent": 2.3, "good": 2.0, "average": 1.7, "low": 1.3, "poor": 1.3},
        "速动比率": {"excellent": 1.2, "good": 1.0, "average": 0.8, "low": 0.5, "poor": 0.5},
        "资产负债率": {"excellent": 75, "good": 78, "average": 82, "low": 85, "poor": 88},
        "净资产收益率": {"excellent": 17, "good": 15, "average": 12, "low": 8, "poor": 8},
        "应收账款周转率": {"excellent": 8, "good": 6, "average": 4.2, "low": 2.5, "poor": 2.5},
        "应收账款周转天数": {"excellent": 45, "good": 60, "average": 86, "low": 144, "poor": 144},
        "总资产周转率": {"excellent": 1.0, "good": 0.9, "average": 0.7, "low": 0.4, "poor": 0.4},
        "毛利率": {"excellent": 18, "good": 15, "average": 12, "low": 8, "poor": 8},
        "净利润率": {"excellent": 6, "good": 5, "average": 3.5, "low": 2, "poor": 2},
    },
    "批发零售业": {
        "流动比率": {"excellent": 1.7, "good": 1.5, "average": 1.2, "low": 0.9, "poor": 0.9},
        "速动比率": {"excellent": 0.9, "good": 0.7, "average": 0.5, "low": 0.3, "poor": 0.3},
        "资产负债率": {"excellent": 45, "good": 50, "average": 55, "low": 65, "poor": 70},
        "净资产收益率": {"excellent": 20, "good": 17, "average": 14, "low": 10, "poor": 10},
        "应收账款周转率": {"excellent": 50, "good": 30, "average": 8.9, "low": 5.0, "poor": 5.0},
        "应收账款周转天数": {"excellent": 7, "good": 12, "average": 41, "low": 73, "poor": 73},
        "存货周转率": {"excellent": 35, "good": 30, "average": 25, "low": 15, "poor": 15},
        "存货周转天数": {"excellent": 10, "good": 12, "average": 15, "low": 24, "poor": 24},
        "总资产周转率": {"excellent": 3.5, "good": 3.0, "average": 2.5, "low": 1.5, "poor": 1.5},
        "毛利率": {"excellent": 35, "good": 30, "average": 25, "low": 18, "poor": 18},
        "净利润率": {"excellent": 10, "good": 8, "average": 6, "low": 3, "poor": 3},
        "销售费用率": {"excellent": 20, "good": 17, "average": 15, "low": 12, "poor": 12},
    },
    "房地产业": {
        "流动比率": {"excellent": 2.0, "good": 1.7, "average": 1.5, "low": 1.2, "poor": 1.2},
        "速动比率": {"excellent": 0.8, "good": 0.7, "average": 0.5, "low": 0.3, "poor": 0.3},
        "资产负债率": {"excellent": 70, "good": 75, "average": 78, "low": 82, "poor": 85},
        "净资产收益率": {"excellent": 25, "good": 20, "average": 17, "low": 12, "poor": 12},
        "存货周转率": {"excellent": 0.8, "good": 0.7, "average": 0.5, "low": 0.3, "poor": 0.3},
        "存货周转天数": {"excellent": 450, "good": 520, "average": 720, "low": 1200, "poor": 1200},
        "总资产周转率": {"excellent": 0.6, "good": 0.5, "average": 0.4, "low": 0.25, "poor": 0.25},
        "毛利率": {"excellent": 35, "good": 30, "average": 25, "low": 15, "poor": 15},
        "净利润率": {"excellent": 18, "good": 15, "average": 12, "low": 8, "poor": 8},
        "现金覆盖率": {"excellent": 1.5, "good": 1.2, "average": 1.0, "low": 0.8, "poor": 0.8},
    },
    "金融业": {
        "资产负债率": {"excellent": 90, "good": 92, "average": 93, "low": 95, "poor": 96},
        "净资产收益率": {"excellent": 18, "good": 16, "average": 14, "low": 10, "poor": 10},
        "总资产报酬率": {"excellent": 2.5, "good": 2.0, "average": 1.5, "low": 1.0, "poor": 1.0},
        "资本充足率": {"excellent": 15, "good": 13.5, "average": 12, "low": 10.5, "poor": 10},
        "拨备覆盖率": {"excellent": 200, "good": 180, "average": 150, "low": 120, "poor": 120},
        "不良贷款率": {"excellent": 1.0, "good": 1.2, "average": 1.5, "low": 2.0, "poor": 2.5},
        "成本收入比": {"excellent": 25, "good": 28, "average": 32, "low": 38, "poor": 42},
        "流动性比率": {"excellent": 60, "good": 55, "average": 50, "low": 40, "poor": 35},
    },
    "科技/互联网": {
        "流动比率": {"excellent": 3.5, "good": 3.0, "average": 2.5, "low": 1.8, "poor": 1.8},
        "速动比率": {"excellent": 3.0, "good": 2.5, "average": 2.2, "low": 1.5, "poor": 1.5},
        "资产负债率": {"excellent": 25, "good": 30, "average": 35, "low": 50, "poor": 55},
        "净资产收益率": {"excellent": 35, "good": 30, "average": 25, "low": 18, "poor": 18},
        "毛利率": {"excellent": 80, "good": 75, "average": 70, "low": 55, "poor": 55},
        "净利润率": {"excellent": 35, "good": 30, "average": 20, "low": 12, "poor": 12},
        "总资产周转率": {"excellent": 2.0, "good": 1.7, "average": 1.5, "low": 1.0, "poor": 1.0},
        "研发投入占比": {"excellent": 25, "good": 20, "average": 17, "low": 12, "poor": 10},
        "营业收入增长率": {"excellent": 50, "good": 35, "average": 25, "low": 15, "poor": 10},
    },
    "服务业": {
        "流动比率": {"excellent": 2.5, "good": 2.2, "average": 2.0, "low": 1.5, "poor": 1.5},
        "速动比率": {"excellent": 2.0, "good": 1.8, "average": 1.5, "low": 1.0, "poor": 1.0},
        "资产负债率": {"excellent": 30, "good": 35, "average": 40, "low": 50, "poor": 55},
        "净资产收益率": {"excellent": 30, "good": 26, "average": 22, "low": 18, "poor": 15},
        "总资产周转率": {"excellent": 2.5, "good": 2.0, "average": 1.7, "low": 1.2, "poor": 1.0},
        "毛利率": {"excellent": 50, "good": 45, "average": 40, "low": 30, "poor": 25},
        "净利润率": {"excellent": 25, "good": 18, "average": 15, "low": 10, "poor": 8},
        "人均产出：万元/人": {"excellent": 80, "good": 60, "average": 45, "low": 30, "poor": 30},
    },
    "医药行业": {
        "流动比率": {"excellent": 2.8, "good": 2.5, "average": 2.2, "low": 1.8, "poor": 1.8},
        "速动比率": {"excellent": 2.2, "good": 2.0, "average": 1.8, "low": 1.5, "poor": 1.5},
        "资产负债率": {"excellent": 25, "good": 30, "average": 35, "low": 45, "poor": 50},
        "净资产收益率": {"excellent": 30, "good": 26, "average": 22, "low": 18, "poor": 15},
        "毛利率": {"excellent": 90, "good": 85, "average": 75, "low": 65, "poor": 60},
        "净利润率": {"excellent": 30, "good": 26, "average": 22, "low": 18, "poor": 15},
        "存货周转率": {"excellent": 8, "good": 6, "average": 5, "low": 3.5, "poor": 3.5},
        "存货周转天数": {"excellent": 45, "good": 60, "average": 73, "low": 103, "poor": 103},
        "总资产周转率": {"excellent": 1.2, "good": 1.0, "average": 0.8, "low": 0.5, "poor": 0.5},
        "研发投入占比": {"excellent": 25, "good": 20, "average": 17, "low": 12, "poor": 10},
    },
    "消费品行业": {
        "流动比率": {"excellent": 2.2, "good": 2.0, "average": 1.8, "low": 1.4, "poor": 1.4},
        "速动比率": {"excellent": 1.8, "good": 1.5, "average": 1.2, "low": 0.8, "poor": 0.8},
        "资产负债率": {"excellent": 35, "good": 40, "average": 45, "low": 55, "poor": 60},
        "净资产收益率": {"excellent": 30, "good": 26, "average": 22, "low": 18, "poor": 15},
        "毛利率": {"excellent": 70, "good": 65, "average": 55, "low": 45, "poor": 40},
        "净利润率": {"excellent": 25, "good": 22, "average": 17, "low": 12, "poor": 10},
        "存货周转率": {"excellent": 15, "good": 12, "average": 10, "low": 6, "poor": 6},
        "存货周转天数": {"excellent": 24, "good": 30, "average": 36, "low": 60, "poor": 60},
        "总资产周转率": {"excellent": 1.8, "good": 1.5, "average": 1.3, "low": 0.8, "poor": 0.8},
        "销售费用率": {"excellent": 35, "good": 30, "average": 25, "low": 18, "poor": 18},
    },
}

# 行业关键词匹配 (用于自动识别)
INDUSTRY_KEYWORDS = {
    "制造业": ["制造", "生产", "加工", "机械", "设备", "电子", "汽车", "化工", "材料", "重工", "轻工", "零部件", "精密"],
    "建筑业": ["建筑", "工程", "施工", "建设", "安装", "装饰", "市政", "园林", "基建", "桥梁", "道路"],
    "批发零售业": ["零售", "商业", "超市", "百货", "连锁", "贸易", "电商", "批发", "商贸", "购物", "门店", "经销"],
    "房地产业": ["房地产", "置业", "地产", "物业", "园区", "租赁", "房产", "开发商", "楼盘"],
    "金融业": ["银行", "保险", "证券", "金融", "投资", "信托", "基金", "期货", "融资租赁", "小贷", "担保"],
    "科技/互联网": ["科技", "互联网", "软件", "信息", "通信", "网络", "数据", "人工智能", "芯片", "半导体", "云计算", "大数据", "物联网"],
    "服务业": ["服务", "咨询", "人力", "培训", "旅游", "酒店", "餐饮", "物流", "运输", "快递", "中介", "法律", "会计"],
    "医药行业": ["医药", "医疗", "生物", "制药", "药业", "健康", "器械", "医院", "诊所", "药品", "疫苗"],
    "消费品行业": ["食品", "饮料", "服装", "家电", "日化", "消费", "用品", "白酒", "乳业", "纺织", "家居", "美妆"],
}


def detect_industry(company_name: str, business_description: str = "") -> str:
    """根据公司名称和业务范围检测行业"""
    text = company_name + " " + business_description
    
    scores = {}
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[industry] = score
    
    if max(scores.values()) == 0:
        return "制造业"  # 默认返回制造业
    
    return max(scores, key=scores.get)


def get_industry_standard(industry: str, ratio_name: str) -> dict:
    """获取某行业的某指标标准值"""
    if industry not in INDUSTRY_STANDARDS:
        # 默认使用制造业标准
        industry = "制造业"
    
    return INDUSTRY_STANDARDS[industry].get(
        ratio_name, 
        {"excellent": 100, "good": 80, "average": 50, "low": 30, "poor": 20}
    )


def evaluate_ratio(industry: str, ratio_name: str, value: float, higher_better: bool = True) -> tuple:
    """
    评估某指标在行业中的水平
    
    Args:
        industry: 行业名称
        ratio_name: 指标名称
        value: 实际值
        higher_better: 是否越大越好（默认 True，资产负债率/不良贷款率等应为 False）
        
    Returns:
        (评级，评价说明)
    """
    standard = get_industry_standard(industry, ratio_name)
    
    # 对于资产负债率、不良贷款率等，越小越好
    if not higher_better:
        if value <= standard["excellent"]:
            return "优秀", "远低于行业优秀水平"
        elif value <= standard["good"]:
            return "良好", "低于行业良好水平"
        elif value <= standard["average"]:
            return "平均", "处于行业平均水平"
        elif value <= standard["low"]:
            return "较低", "高于行业较低水平"
        else:
            return "较差", "高于行业较差水平"
    else:
        if value >= standard["excellent"]:
            return "优秀", "高于行业优秀水平"
        elif value >= standard["good"]:
            return "良好", "高于行业良好水平"
        elif value >= standard["average"]:
            return "平均", "处于行业平均水平"
        elif value >= standard["low"]:
            return "较低", "低于行业较低水平"
        else:
            return "较差", "低于行业较差水平"


def get_all_ratio_standards(industry: str) -> dict:
    """获取某行业的所有指标标准值"""
    if industry not in INDUSTRY_STANDARDS:
        industry = "制造业"
    
    return INDUSTRY_STANDARDS[industry]


def compare_with_industry(industry: str, ratio_name: str, value: float) -> dict:
    """
    对比行业水平，返回详细对比信息
    
    Returns:
        {
            "value": 实际值，
            "excellent": 优秀值，
            "good": 良好值，
            "average": 平均值，
            "low": 较低值，
            "poor": 较差值，
            "rating": 评级，
            "comment": 评价，
            "gap_to_excellent": 与优秀值差距，
            "gap_to_average": 与平均值差距
        }
    """
    standard = get_industry_standard(industry, ratio_name)
    rating, comment = evaluate_ratio(industry, ratio_name, value)
    
    return {
        "value": value,
        "excellent": standard["excellent"],
        "good": standard["good"],
        "average": standard["average"],
        "low": standard["low"],
        "poor": standard["poor"],
        "rating": rating,
        "comment": comment,
        "gap_to_excellent": round(value - standard["excellent"], 2),
        "gap_to_average": round(value - standard["average"], 2),
    }
