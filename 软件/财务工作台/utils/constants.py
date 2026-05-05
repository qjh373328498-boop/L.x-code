"""
财务工作台 - 统一常量配置
"""

# ========== 分页配置 ==========
class Pagination:
    """分页查询配置"""
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    PAGE_SIZE_OPTIONS = [10, 20, 50, 100]


# ========== 缓存配置（秒） ==========
class CacheTTL:
    """缓存过期时间配置"""
    INVOICE_QUERY = 300          # 发票查询 5 分钟
    BANK_RECONCILIATION = 3600    # 银行对账 1 小时
    FINANCIAL_RATIOS = 600        # 财务比率 10 分钟
    INDUSTRY_DATA = 86400         # 行业数据 24 小时
    TEMPLATE_DATA = 86400         # 模板数据 24 小时
    DEFAULT = 300                 # 默认 5 分钟


# ========== 用户角色 ==========
class Roles:
    """用户角色定义"""
    ADMIN = 'admin'
    FINANCE = 'finance'
    INTERN = 'intern'
    GUEST = 'guest'


# ========== 默认账户 ==========
class DefaultAccounts:
    """默认用户账户"""
    ADMIN = {'username': 'admin', 'password': '703102'}
    FINANCE = {'username': 'finance', 'password': 'finance123'}
    INTERN = {'username': 'intern', 'password': 'intern123'}


# ========== 发票类型 ==========
class InvoiceTypes:
    """发票类型定义"""
    SPECIAL = '专用发票'
    NORMAL = '普通发票'
    ELECTRONIC = '电子发票'
    
    OPTIONS = [SPECIAL, NORMAL, ELECTRONIC]


# ========== 认证状态 ==========
class InvoiceStatus:
    """发票认证状态"""
    UNCERTIFIED = '未认证'
    CERTIFIED = '已认证'
    RETURNED = '已退票'
    
    OPTIONS = [UNCERTIFIED, CERTIFIED, RETURNED]


# ========== 财务期间 ==========
class FiscalPeriods:
    """财务期间选项"""
    OPTIONS = ['月度', '季度', '年度']
    MONTHLY = '月度'
    QUARTERLY = '季度'
    YEARLY = '年度'


# ========== 金额容差 ==========
class Tolerance:
    """金额匹配容差"""
    DEFAULT = 0.01
    STRICT = 0.001
    LOOSE = 0.1


# ========== 日期容差（天） ==========
class DateTolerance:
    """日期匹配容差"""
    DEFAULT = 3
    STRICT = 1
    LOOSE = 7


# ========== 数据库配置 ==========
class Database:
    """数据库配置"""
    MAIN_DB = 'data/finance.db'
    HISTORY_DB = 'data/history.db'
    BACKUP_PREFIX = 'finance_backup'


# ========== 行业分类 ==========
class Industries:
    """行业分类"""
    MANUFACTURING = '制造业'
    IT = '信息技术'
    REAL_ESTATE = '房地产'
    CONSTRUCTION = '建筑'
    RETAIL = '批发零售'
    TRANSPORTATION = '交通运输'
    HOSPITALITY = '住宿餐饮'
    LEASING = '租赁商务'
    OTHER = '其他行业'
    
    OPTIONS = [MANUFACTURING, IT, REAL_ESTATE, CONSTRUCTION, 
               RETAIL, TRANSPORTATION, HOSPITALITY, LEASING, OTHER]


# ========== 报表类型 ==========
class ReportTypes:
    """报表类型"""
    BALANCE_SHEET = '资产负债表'
    INCOME_STATEMENT = '利润表'
    CASH_FLOW = '现金流量表'
    
    OPTIONS = [BALANCE_SHEET, INCOME_STATEMENT, CASH_FLOW]


# ========== UI 配置 ==========
class UI:
    """UI 配置"""
    DEFAULT_LAYOUT = 'wide'
    DEFAULT_ICON = '📊'
    SIDEBAR_POSITION = 'left'
