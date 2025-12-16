"""
模拟交易引擎
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .paper_trading_account import PaperTradingAccount
from .paper_trading_order import Order, OrderStatus, OrderSide

class PaperTradingEngine:
    """模拟交易引擎"""
    def __init__(self):
        self.accounts: Dict[str, PaperTradingAccount] = {}
        self.orders: Dict[str, Order] = {}
    
    def create_account(self, account_id: str, initial_cash: float = 1000000.0) -> PaperTradingAccount:
        """创建账户"""
        if account_id in self.accounts:
            return self.accounts[account_id]
        
        account = PaperTradingAccount(account_id, initial_cash)
        self.accounts[account_id] = account
        return account
    
    def get_account(self, account_id: str) -> Optional[PaperTradingAccount]:
        """获取账户"""
        return self.accounts.get(account_id)
    
    def submit_order(self, account_id: str, order: Order) -> bool:
        """提交订单"""
        account = self.get_account(account_id)
        if not account:
            order.status = OrderStatus.REJECTED
            return False
        
        # 检查资金
        if order.side == OrderSide.BUY:
            required_cash = order.quantity * (order.price or 0)
            if account.cash < required_cash:
                order.status = OrderStatus.REJECTED
                return False
        
        order.status = OrderStatus.SUBMITTED
        self.orders[order.order_id] = order
        return True
    
    def execute_order(self, order_id: str, execution_price: float) -> bool:
        """执行订单"""
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.SUBMITTED:
            return False
        
        account = self.get_account(order.order_id.split("_")[0])  # 简化：从order_id提取account_id
        if not account:
            return False
        
        # 计算手续费（万分之三）
        commission = order.quantity * execution_price * 0.0003
        
        if order.side == OrderSide.BUY:
            # 买入
            total_cost = order.quantity * execution_price + commission
            account.cash -= total_cost
            account.update_position(order.symbol, order.quantity, execution_price, True)
        else:
            # 卖出
            total_proceeds = order.quantity * execution_price - commission
            account.cash += total_proceeds
            account.update_position(order.symbol, order.quantity, execution_price, False)
        
        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.average_price = execution_price
        order.commission = commission
        order.filled_time = datetime.now()
        order.updated_time = datetime.now()
        
        # 记录交易
        account.add_trade({
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "price": execution_price,
            "commission": commission
        })
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        order = self.orders.get(order_id)
        if not order or order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_time = datetime.now()
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.orders.get(order_id)
    
    def get_orders(self, account_id: str) -> List[Order]:
        """获取账户所有订单"""
        return [o for o in self.orders.values() if o.order_id.startswith(account_id)]

