"""
模拟交易账户模块
"""
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal

class Position:
    """持仓"""
    def __init__(self, symbol: str, quantity: int, cost_basis: float):
        self.symbol = symbol
        self.quantity = quantity
        self.cost_basis = cost_basis
        self.average_price = cost_basis / quantity if quantity > 0 else 0
        self.updated_time = datetime.now()
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "cost_basis": self.cost_basis,
            "average_price": self.average_price,
            "updated_time": self.updated_time.isoformat()
        }

class PaperTradingAccount:
    """模拟交易账户"""
    def __init__(self, account_id: str, initial_cash: float = 1000000.0):
        self.account_id = account_id
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[dict] = []
        self.created_time = datetime.now()
        self.updated_time = datetime.now()
    
    @property
    def total_value(self) -> float:
        """总资产价值（现金 + 持仓市值）"""
        return self.cash + sum(pos.cost_basis for pos in self.positions.values())
    
    @property
    def total_pnl(self) -> float:
        """总盈亏"""
        return self.total_value - self.initial_cash
    
    @property
    def return_pct(self) -> float:
        """收益率"""
        return (self.total_pnl / self.initial_cash * 100) if self.initial_cash > 0 else 0
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)
    
    def update_position(self, symbol: str, quantity: int, price: float, is_buy: bool):
        """更新持仓"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            if is_buy:
                # 买入：增加持仓
                new_quantity = pos.quantity + quantity
                new_cost = pos.cost_basis + (quantity * price)
                pos.quantity = new_quantity
                pos.cost_basis = new_cost
                pos.average_price = new_cost / new_quantity if new_quantity > 0 else 0
            else:
                # 卖出：减少持仓
                pos.quantity -= quantity
                pos.cost_basis -= (quantity * pos.average_price)
                if pos.quantity <= 0:
                    del self.positions[symbol]
                    return
            pos.updated_time = datetime.now()
        else:
            if is_buy:
                # 新建持仓
                self.positions[symbol] = Position(symbol, quantity, quantity * price)
    
    def add_trade(self, trade_info: dict):
        """添加交易记录"""
        trade_info["timestamp"] = datetime.now().isoformat()
        self.trade_history.append(trade_info)
        self.updated_time = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            "account_id": self.account_id,
            "initial_cash": self.initial_cash,
            "cash": self.cash,
            "total_value": self.total_value,
            "total_pnl": self.total_pnl,
            "return_pct": self.return_pct,
            "positions": {k: v.to_dict() for k, v in self.positions.items()},
            "trade_count": len(self.trade_history),
            "created_time": self.created_time.isoformat(),
            "updated_time": self.updated_time.isoformat()
        }

