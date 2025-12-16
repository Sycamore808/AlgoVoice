"""
初始化Sycamore1024用户和策略
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from module_08_execution.paper_trading.custom_strategy_manager import CustomStrategyManager
from module_08_execution.paper_trading.paper_trading_engine import PaperTradingEngine

def main():
    """初始化Sycamore1024策略"""
    print("Initializing Sycamore1024 strategy...")
    
    # 创建策略管理器
    strategy_manager = CustomStrategyManager()
    
    # 检查是否已存在
    existing_strategies = strategy_manager.get_user_strategies("Sycamore1024")
    
    if existing_strategies:
        print(f"Found {len(existing_strategies)} existing strategy/strategies for Sycamore1024")
        for strategy in existing_strategies:
            print(f"  - {strategy['strategy_name']} (ID: {strategy['strategy_id']})")
        return
    
    # 创建Sycamore1024的量化选股策略
    strategy_id = strategy_manager.create_strategy(
        user_id="Sycamore1024",
        strategy_name="量化选股策略V1",
        description="每日14:30执行的10步量化选股策略：涨幅3-5%，量比>1，换手率5-10%，市值50-200亿，成交量稳定，均线向上，强于大盘，尾盘创新高",
        strategy_type="quantitative_selection",
        parameters={
            "execution_time": "14:30",
            "gain_range": [3, 5],  # 涨幅范围 3%-5%
            "volume_ratio_min": 1,  # 量比最小值
            "turnover_rate_range": [5, 10],  # 换手率范围 5%-10%
            "market_cap_range": [50, 200],  # 市值范围 50-200亿
            "check_volume_stability": True,  # 检查成交量稳定性
            "check_ma_uptrend": True,  # 检查均线向上
            "check_relative_strength": True,  # 检查相对强度
            "check_eod_high": True,  # 检查尾盘创新高
            "ma_short": 5,  # 短期均线天数
            "ma_long": 60,  # 长期均线天数
        }
    )
    
    print(f"✓ Created strategy: {strategy_id}")
    
    # 创建模拟交易账户
    engine = PaperTradingEngine()
    account = engine.create_account("Sycamore1024", initial_cash=1000000.0)
    print(f"✓ Created paper trading account with {account.initial_cash:,.2f} CNY")
    
    print("\nInitialization complete!")
    print(f"User: Sycamore1024")
    print(f"Strategy ID: {strategy_id}")
    print(f"Account: {account.account_id}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

