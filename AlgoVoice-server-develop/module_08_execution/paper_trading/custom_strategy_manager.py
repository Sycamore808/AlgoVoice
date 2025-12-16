"""
自定义策略管理器
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class CustomStrategyManager:
    """自定义策略管理器"""
    def __init__(self, db_path: str = "data/AlgoVoice.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建策略表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paper_trading_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                description TEXT,
                strategy_type TEXT DEFAULT 'custom',
                parameters TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_time TEXT NOT NULL,
                updated_time TEXT NOT NULL,
                last_run_time TEXT,
                total_runs INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                win_rate REAL DEFAULT 0
            )
        """)
        
        # 创建策略执行记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id TEXT NOT NULL,
                execution_time TEXT NOT NULL,
                status TEXT NOT NULL,
                selected_stocks TEXT,
                profit_loss REAL DEFAULT 0,
                error_message TEXT,
                FOREIGN KEY (strategy_id) REFERENCES paper_trading_strategies(strategy_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_strategy(
        self,
        user_id: str,
        strategy_name: str,
        description: str = "",
        strategy_type: str = "custom",
        parameters: Dict = None
    ) -> str:
        """创建策略"""
        import uuid
        strategy_id = f"strategy_{uuid.uuid4().hex[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO paper_trading_strategies 
            (strategy_id, user_id, strategy_name, description, strategy_type, parameters, created_time, updated_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (strategy_id, user_id, strategy_name, description, strategy_type, 
              json.dumps(parameters or {}), now, now))
        
        conn.commit()
        conn.close()
        
        return strategy_id
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """获取策略"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM paper_trading_strategies WHERE strategy_id = ?", (strategy_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            strategy = dict(row)
            strategy['parameters'] = json.loads(strategy['parameters']) if strategy['parameters'] else {}
            return strategy
        return None
    
    def get_user_strategies(self, user_id: str) -> List[Dict]:
        """获取用户所有策略"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM paper_trading_strategies WHERE user_id = ? ORDER BY created_time DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        strategies = []
        for row in rows:
            strategy = dict(row)
            strategy['parameters'] = json.loads(strategy['parameters']) if strategy['parameters'] else {}
            strategies.append(strategy)
        
        return strategies
    
    def activate_strategy(self, strategy_id: str, is_active: bool = True) -> bool:
        """激活/停用策略"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE paper_trading_strategies 
            SET is_active = ?, updated_time = ?
            WHERE strategy_id = ?
        """, (1 if is_active else 0, datetime.now().isoformat(), strategy_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def record_execution(
        self,
        strategy_id: str,
        status: str,
        selected_stocks: List[str] = None,
        profit_loss: float = 0,
        error_message: str = None
    ):
        """记录策略执行"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO strategy_executions 
            (strategy_id, execution_time, status, selected_stocks, profit_loss, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (strategy_id, now, status, json.dumps(selected_stocks or []), profit_loss, error_message))
        
        # 更新策略统计
        cursor.execute("""
            UPDATE paper_trading_strategies 
            SET last_run_time = ?, total_runs = total_runs + 1, updated_time = ?
            WHERE strategy_id = ?
        """, (now, now, strategy_id))
        
        conn.commit()
        conn.close()
    
    def get_strategy_performance(self, strategy_id: str) -> Dict:
        """获取策略表现"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取执行历史
        cursor.execute("""
            SELECT * FROM strategy_executions 
            WHERE strategy_id = ? 
            ORDER BY execution_time DESC 
            LIMIT 100
        """, (strategy_id,))
        
        executions = [dict(row) for row in cursor.fetchall()]
        
        # 计算统计数据
        total_runs = len(executions)
        successful_runs = len([e for e in executions if e['status'] == 'success'])
        total_profit = sum(e['profit_loss'] for e in executions)
        
        conn.close()
        
        return {
            "strategy_id": strategy_id,
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            "total_profit": total_profit,
            "recent_executions": executions[:10]
        }

