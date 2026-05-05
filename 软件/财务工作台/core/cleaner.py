"""
FinCopilot - 数据清洗器
FuzzyWuzzy 实现文本聚类清洗
"""
from fuzzywuzzy import fuzz, process
from typing import List, Dict, Set


def find_similar_names(names: List[str], threshold: int = 80) -> Dict[str, List[str]]:
    """
    查找相似的供应商名称
    
    参数:
        names: 名称列表
        threshold: 相似度阈值（0-100）
    
    返回:
        分组后的相似名称字典
    """
    clusters = {}
    used = set()
    
    for i, name in enumerate(names):
        if name in used:
            continue
        
        # 查找与当前名称相似的所有名称
        similar = []
        for j, other in enumerate(names):
            if i != j and other not in used:
                ratio = fuzz.ratio(name, other)
                if ratio >= threshold:
                    similar.append(other)
                    used.add(other)
        
        if similar:
            used.add(name)
            clusters[name] = similar
    
    return clusters


def standardize_name(name: str, standard_names: List[str]) -> str:
    """
    标准化名称：将别名映射到标准名
    
    参数:
        name: 原始名称
        standard_names: 标准名称列表
    
    返回:
        最匹配的标准名
    """
    if not standard_names:
        return name
    
    # 找到最匹配的标准名
    best_match, score = process.extractOne(name, standard_names)
    
    if score >= 80:
        return best_match
    return name


def extract_keywords(text: str) -> Set[str]:
    """
    提取文本中的关键词
    简化版：按标点和空格分割
    """
    import re
    # 去除标点
    text = re.sub(r'[^\w\s\u4e00-\u9fa5]', ' ', text)
    # 分割
    words = text.split()
    # 过滤短词
    keywords = {w for w in words if len(w) > 1}
    return keywords


def cluster_by_keywords(items: List[Dict[str, str]], keyword_field: str) -> List[Dict]:
    """
    按关键词聚类
    
    参数:
        items: 项目列表
        keyword_field: 用于聚类的字段名
    """
    clusters = {}
    
    for item in items:
        text = item.get(keyword_field, '')
        keywords = extract_keywords(text)
        
        # 用第一个关键词作为聚类键
        if keywords:
            key = list(keywords)[0]
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(item)
    
    # 转换为列表
    result = []
    for key, items in clusters.items():
        result.append({
            'cluster_key': key,
            'count': len(items),
            'items': items
        })
    
    return result
