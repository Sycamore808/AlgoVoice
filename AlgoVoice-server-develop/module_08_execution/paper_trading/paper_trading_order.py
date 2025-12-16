"""
模拟交易订单模块
"""
from enum import Enum
from datetime import datetime
from typing import Optional

class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"  # 待处理
    SUBMITTED = "submitted"  # 已提交
    PARTIAL_FILLED = "partial_filled"  # 部分成交
    FILLED = "filled"  # 已成交
    CANCELLED = "cancelled"  # 已取消
    REJECTED = "rejected"  # 已拒绝

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"  # 限价单

class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"  # 买入
    SELL = "sell"  # 卖出

class Order:
    """订单类"""
    def __init__(
        self,
        order_id: str,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        price: Optional[float] = None,
        strategy_id: Optional[str] = None
    ):
        self.order_id = order_id
        self.symbol = symbol
        self.side = side
        self.quantity = quantity
        self.order_type = order_type
        self.price = price
        self.strategy_id = strategy_id
        
        self.status = OrderStatus.PENDING
        self.filled_quantity = 0
        self.average_price = 0.0
        self.commission = 0.0
        
        self.created_time = datetime.now()
        self.updated_time = datetime.now()
        self.filled_time: Optional[datetime] = None
    
    def to_dict(self):
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": self.quantity,
            "order_type": self.order_type.value,
            "price": self.price,
            "strategy_id": self.strategy_id,
            "status": self.status.value,
            "filled_quantity": self.filled_quantity,
            "average_price": self.average_price,
            "commission": self.commission,
            "created_time": self.created_time.isoformat(),
            "updated_time": self.updated_time.isoformat(),
            "filled_time": self.filled_time.isoformat() if self.filled_time else None
        }

