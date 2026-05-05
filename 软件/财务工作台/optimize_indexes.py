"""
数据库索引优化工具
为常用查询字段创建索引，大幅提升查询性能
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "finance.db"

def create_indexes():
    """创建推荐索引"""
    
    indexes = [
        # 发票表索引
        "CREATE INDEX IF NOT EXISTS idx_invoice_code ON invoice(code)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_number ON invoice(number)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoice(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_supplier ON invoice(supplier)",
        "CREATE INDEX IF NOT EXISTS idx_invoice_buyer ON invoice(buyer)",
        
        # 财务指标表索引
        "CREATE INDEX IF NOT EXISTS idx_metrics_period ON financial_metrics(period DESC)",
        "CREATE INDEX IF NOT EXISTS idx_metrics_category ON financial_metrics(category)",
        
        # 银行交易表索引（如果存在）
        "CREATE INDEX IF NOT EXISTS idx_bank_date ON bank_transaction(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_bank_amount ON bank_transaction(amount)",
        
        # 凭证表索引（如果存在）
        "CREATE INDEX IF NOT EXISTS idx_voucher_date ON voucher(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_voucher_type ON voucher(type)",
    ]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    created = []
    skipped = []
    errors = []
    
    for sql in indexes:
        try:
            # 检查表是否存在
            table_name = sql.split("ON")[1].split("(")[0].strip()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone():
                cursor.execute(sql)
                created.append(sql)
            else:
                skipped.append(f"表 {table_name} 不存在")
        except Exception as e:
            errors.append(f"{sql} - {str(e)}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ 成功创建 {len(created)} 个索引")
    if skipped:
        print(f"⚠️ 跳过 {len(skipped)} 个索引（表不存在）")
    if errors:
        print(f"❌ 错误 {len(errors)} 个")
    
    return created, skipped, errors

if __name__ == "__main__":
    print("开始优化数据库索引...")
    created, skipped, errors = create_indexes()
    print("\n创建的索引:")
    for idx in created:
        print(f"  ✓ {idx}")
