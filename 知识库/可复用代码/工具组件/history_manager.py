"""
FinCopilot - 历史记录管理
使用 SQLite 保存用户的计算和解析记录
"""
import sqlite3
from datetime import datetime
from typing import Dict, Any, List


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, db_path: str = "data/history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        import os
        
        # 创建数据目录
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                calc_type TEXT NOT NULL,
                params TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 文档解析历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parsing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                filename TEXT NOT NULL,
                amount REAL,
                company TEXT,
                date TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 关联匹配历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matching_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                receipts_count INTEGER,
                invoices_count INTEGER,
                matched_count INTEGER,
                match_rate REAL,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_calculation(self, username: str, calc_type: str, params: Dict, result: Dict) -> int:
        """添加计算记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        import json
        cursor.execute('''
            INSERT INTO calculation_history (username, calc_type, params, result)
            VALUES (?, ?, ?, ?)
        ''', (username, calc_type, json.dumps(params), json.dumps(result)))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def add_parsing(self, username: str, filename: str, result: Dict) -> int:
        """添加文档解析记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO parsing_history 
            (username, filename, amount, company, date, result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            username, filename, 
            result.get('amount', 0),
            result.get('company', ''),
            result.get('date', ''),
            str(result)
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def add_matching(self, username: str, receipts_count: int, invoices_count: int, 
                     matched_count: int, match_rate: float) -> int:
        """添加关联匹配记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO matching_history 
            (username, receipts_count, invoices_count, matched_count, match_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, receipts_count, invoices_count, matched_count, match_rate))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return row_id
    
    def get_calculation_history(self, username: str, limit: int = 50) -> List[Dict]:
        """获取计算历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM calculation_history 
            WHERE username = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (username, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_parsing_history(self, username: str, limit: int = 50) -> List[Dict]:
        """获取文档解析历史"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM parsing_history 
            WHERE username = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (username, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_statistics(self, username: str) -> Dict:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 计算次数
        cursor.execute('SELECT COUNT(*) FROM calculation_history WHERE username = ?', (username,))
        stats['calculation_count'] = cursor.fetchone()[0]
        
        # 解析文件数
        cursor.execute('SELECT COUNT(*) FROM parsing_history WHERE username = ?', (username,))
        stats['parsing_count'] = cursor.fetchone()[0]
        
        # 匹配次数
        cursor.execute('SELECT COUNT(*) FROM matching_history WHERE username = ?', (username,))
        stats['matching_count'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def clear_history(self, username: str, history_type: str = 'all') -> bool:
        """清空历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if history_type == 'calculation':
            cursor.execute('DELETE FROM calculation_history WHERE username = ?', (username,))
        elif history_type == 'parsing':
            cursor.execute('DELETE FROM parsing_history WHERE username = ?', (username,))
        elif history_type == 'matching':
            cursor.execute('DELETE FROM matching_history WHERE username = ?', (username,))
        else:
            cursor.execute('DELETE FROM calculation_history WHERE username = ?', (username,))
            cursor.execute('DELETE FROM parsing_history WHERE username = ?', (username,))
            cursor.execute('DELETE FROM matching_history WHERE username = ?', (username,))
        
        conn.commit()
        conn.close()
        
        return True
