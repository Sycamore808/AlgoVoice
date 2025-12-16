"""
模拟交易API接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import uuid

from .paper_trading_engine import PaperTradingEngine
from .paper_trading_order import Order, OrderType, OrderSide
from .custom_strategy_manager import CustomStrategyManager

router = APIRouter(prefix="/api/paper-trading", tags=["Paper Trading"])

# 全局实例
engine = PaperTradingEngine()
strategy_manager = CustomStrategyManager()

# ===== 请求模型 =====

class CreateAccountRequest(BaseModel):
    account_id: str
    initial_cash: float = 1000000.0

class SubmitOrderRequest(BaseModel):
    account_id: str
    symbol: str
    side: str  # "buy" or "sell"
    quantity: int
    order_type: str = "market"
    price: Optional[float] = None
    strategy_id: Optional[str] = None

class CreateStrategyRequest(BaseModel):
    user_id: str
    strategy_name: str
    description: str = ""
    strategy_type: str = "custom"
    parameters: Optional[Dict] = None

class ActivateStrategyRequest(BaseModel):
    strategy_id: str
    is_active: bool

# ===== API端点 =====

@router.post("/accounts")
async def create_account(request: CreateAccountRequest):
    """创建模拟交易账户"""
    account = engine.create_account(request.account_id, request.initial_cash)
    return {"success": True, "data": account.to_dict()}

@router.get("/accounts/{account_id}")
async def get_account(account_id: str):
    """获取账户信息"""
    account = engine.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"success": True, "data": account.to_dict()}

@router.post("/orders")
async def submit_order(request: SubmitOrderRequest):
    """提交订单"""
    order_id = f"{request.account_id}_{uuid.uuid4().hex[:8]}"
    
    order = Order(
        order_id=order_id,
        symbol=request.symbol,
        side=OrderSide.BUY if request.side.lower() == "buy" else OrderSide.SELL,
        quantity=request.quantity,
        order_type=OrderType.MARKET if request.order_type.lower() == "market" else OrderType.LIMIT,
        price=request.price,
        strategy_id=request.strategy_id
    )
    
    success = engine.submit_order(request.account_id, order)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to submit order")
    
    # 模拟立即执行（使用提供的价格或默认价格）
    execution_price = request.price if request.price else 10.0  # 简化：使用固定价格
    engine.execute_order(order_id, execution_price)
    
    return {"success": True, "data": order.to_dict()}

@router.get("/orders/{account_id}")
async def get_orders(account_id: str):
    """获取账户订单"""
    orders = engine.get_orders(account_id)
    return {"success": True, "data": [o.to_dict() for o in orders]}

@router.post("/strategies")
async def create_strategy(request: CreateStrategyRequest):
    """创建策略"""
    strategy_id = strategy_manager.create_strategy(
        user_id=request.user_id,
        strategy_name=request.strategy_name,
        description=request.description,
        strategy_type=request.strategy_type,
        parameters=request.parameters
    )
    return {"success": True, "data": {"strategy_id": strategy_id}}

@router.get("/strategies/user/{user_id}")
async def get_user_strategies(user_id: str):
    """获取用户策略列表"""
    strategies = strategy_manager.get_user_strategies(user_id)
    return {"success": True, "data": strategies}

@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """获取策略详情"""
    strategy = strategy_manager.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"success": True, "data": strategy}

@router.post("/strategies/activate")
async def activate_strategy(request: ActivateStrategyRequest):
    """激活/停用策略"""
    success = strategy_manager.activate_strategy(request.strategy_id, request.is_active)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"success": True}

@router.get("/strategies/{strategy_id}/performance")
async def get_strategy_performance(strategy_id: str):
    """获取策略表现"""
    performance = strategy_manager.get_strategy_performance(strategy_id)
    return {"success": True, "data": performance}

