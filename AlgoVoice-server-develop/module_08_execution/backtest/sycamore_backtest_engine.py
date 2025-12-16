"""
Sycamore1024策略回测引擎
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple
import logging
from pathlib import Path

from .local_data_manager import LocalDataManager

logger = logging.getLogger(__name__)


class SycamoreBacktestEngine:
    """Sycamore1024量化选股策略回测引擎"""
    
    def __init__(
        self,
        initial_capital: float = 10000000,  # 1000万初始资金
        data_manager: LocalDataManager = None
    ):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            data_manager: 数据管理器
        """
        self.initial_capital = initial_capital
        self.data_manager = data_manager or LocalDataManager()
        
        # 策略参数
        self.params = {
            'gain_range': [3, 5],  # 涨幅范围 3-5%
            'volume_ratio_min': 1,  # 量比最小值
            'turnover_rate_range': [5, 10],  # 换手率范围
            'market_cap_range': [50, 200],  # 市值范围（亿元）
            'ma_short': 5,  # 短期均线
            'ma_long': 60,  # 长期均线
            'max_stocks': 10,  # 最大持仓股票数
            'position_per_stock': 0.1  # 每只股票仓位
        }
        
        # 回测结果
        self.portfolio = {}  # 当前持仓 {code: shares}
        self.cash = initial_capital
        self.daily_records = []  # 每日记录
        self.trade_records = []  # 交易记录
        
    def screen_stocks(
        self,
        date: datetime,
        all_stocks_data: Dict[str, pd.DataFrame]
    ) -> List[str]:
        """
        执行选股逻辑
        
        Args:
            date: 选股日期
            all_stocks_data: 所有股票数据
            
        Returns:
            选中的股票代码列表
        """
        selected = []
        
        for code, df in all_stocks_data.items():
            try:
                # 确保有足够的历史数据
                if len(df) < 70:  # 需要60日均线数据
                    continue
                
                # 获取最新数据
                latest = df.iloc[-1]
                df_with_indicators = self.data_manager.calculate_indicators(df)
                latest_with_ind = df_with_indicators.iloc[-1]
                
                # 步骤1: 涨幅筛选 3-5%
                pct_chg = latest.get('pct_chg', 0)
                if not (self.params['gain_range'][0] <= pct_chg <= self.params['gain_range'][1]):
                    continue
                
                # 步骤2: 量比>1
                volume_ratio = latest_with_ind.get('volume_ratio', 0)
                if volume_ratio < self.params['volume_ratio_min']:
                    continue
                
                # 步骤3: 换手率 5-10%
                turnover = latest.get('turn', 0) or latest.get('free_turn', 0)
                if not (self.params['turnover_rate_range'][0] <= turnover <= self.params['turnover_rate_range'][1]):
                    continue
                
                # 步骤4: 市值 50-200亿
                mkt_cap = latest.get('mkt_cap_ard', 0) / 100000000  # 转为亿元
                if not (self.params['market_cap_range'][0] <= mkt_cap <= self.params['market_cap_range'][1]):
                    continue
                
                # 步骤5: 成交量稳定（标准差/均值 < 1）
                volume_stability = latest_with_ind.get('volume_stability', 999)
                if volume_stability > 1.0:
                    continue
                
                # 步骤6: 均线向上
                ma5_uptrend = latest_with_ind.get('ma5_uptrend', False)
                ma60_uptrend = latest_with_ind.get('ma60_uptrend', False)
                if not (ma5_uptrend and ma60_uptrend):
                    continue
                
                # 步骤7: 强于大盘（相对强度）
                market_return = self.data_manager.get_market_index_return(date)
                if pct_chg <= market_return:
                    continue
                
                # 步骤8: 尾盘创新高
                is_new_high = latest_with_ind.get('is_new_high', False)
                if not is_new_high:
                    continue
                
                # 步骤9: 不跌破均线
                close = latest.get('close', 0)
                ma5 = latest_with_ind.get('ma5', 0)
                if close < ma5:
                    continue
                
                # 通过所有筛选
                selected.append(code)
                
            except Exception as e:
                logger.warning(f"{code} 筛选失败: {e}")
                continue
        
        # 按市值排序，选择前N只
        if len(selected) > self.params['max_stocks']:
            # 获取市值信息
            stocks_with_cap = []
            for code in selected:
                df = all_stocks_data[code]
                mkt_cap = df.iloc[-1].get('mkt_cap_ard', 0)
                stocks_with_cap.append((code, mkt_cap))
            
            # 按市值排序
            stocks_with_cap.sort(key=lambda x: x[1], reverse=True)
            selected = [code for code, _ in stocks_with_cap[:self.params['max_stocks']]]
        
        return selected
    
    def rebalance_portfolio(
        self,
        date: datetime,
        selected_stocks: List[str],
        all_stocks_data: Dict[str, pd.DataFrame]
    ):
        """
        调整持仓
        
        Args:
            date: 调整日期
            selected_stocks: 选中的股票
            all_stocks_data: 所有股票数据
        """
        # 卖出不在选股列表中的持仓
        to_sell = [code for code in self.portfolio.keys() if code not in selected_stocks]
        for code in to_sell:
            if code in all_stocks_data:
                price = all_stocks_data[code].iloc[-1].get('close', 0)
                shares = self.portfolio[code]
                sell_amount = price * shares * 0.9985  # 扣除手续费
                
                self.cash += sell_amount
                del self.portfolio[code]
                
                self.trade_records.append({
                    'date': date,
                    'code': code,
                    'action': 'sell',
                    'price': price,
                    'shares': shares,
                    'amount': sell_amount
                })
        
        # 买入新股票
        to_buy = [code for code in selected_stocks if code not in self.portfolio]
        if to_buy:
            # 计算每只股票的资金
            total_value = self.get_portfolio_value(date, all_stocks_data)
            cash_per_stock = total_value * self.params['position_per_stock']
            
            for code in to_buy:
                if code not in all_stocks_data:
                    continue
                
                price = all_stocks_data[code].iloc[-1].get('close', 0)
                if price <= 0:
                    continue
                
                # 计算可买股数（100股为单位）
                shares = int(cash_per_stock / price / 100) * 100
                if shares < 100:
                    continue
                
                buy_amount = price * shares * 1.0015  # 加上手续费
                if buy_amount > self.cash:
                    continue
                
                self.cash -= buy_amount
                self.portfolio[code] = shares
                
                self.trade_records.append({
                    'date': date,
                    'code': code,
                    'action': 'buy',
                    'price': price,
                    'shares': shares,
                    'amount': buy_amount
                })
    
    def get_portfolio_value(
        self,
        date: datetime,
        all_stocks_data: Dict[str, pd.DataFrame]
    ) -> float:
        """
        计算投资组合总价值
        
        Args:
            date: 日期
            all_stocks_data: 所有股票数据
            
        Returns:
            总价值
        """
        stock_value = 0
        for code, shares in self.portfolio.items():
            if code in all_stocks_data:
                price = all_stocks_data[code].iloc[-1].get('close', 0)
                stock_value += price * shares
        
        return self.cash + stock_value
    
    def run_backtest(
        self,
        start_date: str = "2000-01-01",
        end_date: str = "2025-12-10"
    ) -> pd.DataFrame:
        """
        运行回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果DataFrame
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 开始回测: {start_date} - {end_date}")
        logger.info(f"💰 初始资金: {self.initial_capital:,.0f}")
        logger.info(f"{'='*60}\n")
        
        # 获取交易日
        trading_dates = self.data_manager.get_trading_dates(start_date, end_date)
        total_days = len(trading_dates)
        
        logger.info(f"📅 交易日总数: {total_days}")
        
        # 重置状态
        self.portfolio = {}
        self.cash = self.initial_capital
        self.daily_records = []
        self.trade_records = []
        
        # 遍历每个交易日
        for i, date in enumerate(trading_dates):
            try:
                # 进度提示
                if i % 250 == 0:  # 每年提示一次
                    logger.info(f"⏳ 进度: {i}/{total_days} ({i/total_days*100:.1f}%) - {date.strftime('%Y-%m-%d')}")
                
                # 仅在每日14:30执行（模拟）- 实际上每个交易日执行一次
                # 获取当日所有股票数据
                all_stocks_data = self.data_manager.get_stock_data_on_date(date, lookback_days=100)
                
                if not all_stocks_data:
                    logger.warning(f"{date} 无可用数据")
                    continue
                
                # 执行选股
                selected_stocks = self.screen_stocks(date, all_stocks_data)
                
                # 调整持仓
                if selected_stocks:
                    self.rebalance_portfolio(date, selected_stocks, all_stocks_data)
                
                # 记录当日状态
                portfolio_value = self.get_portfolio_value(date, all_stocks_data)
                market_return = self.data_manager.get_market_index_return(date)
                
                self.daily_records.append({
                    'date': date,
                    'portfolio_value': portfolio_value,
                    'cash': self.cash,
                    'stock_value': portfolio_value - self.cash,
                    'num_stocks': len(self.portfolio),
                    'selected_count': len(selected_stocks),
                    'market_return': market_return,
                    'return': (portfolio_value - self.initial_capital) / self.initial_capital * 100
                })
                
            except Exception as e:
                logger.error(f"{date} 回测失败: {e}")
                continue
        
        # 转换为DataFrame
        results_df = pd.DataFrame(self.daily_records)
        results_df.set_index('date', inplace=True)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 回测完成!")
        logger.info(f"📊 交易次数: {len(self.trade_records)}")
        if not results_df.empty:
            final_return = results_df['return'].iloc[-1]
            logger.info(f"📈 最终收益率: {final_return:.2f}%")
        logger.info(f"{'='*60}\n")
        
        return results_df


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建回测引擎
    engine = SycamoreBacktestEngine()
    
    # 运行回测（测试少量数据）
    results = engine.run_backtest(
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    print("\n回测结果预览:")
    print(results.head())
    print(results.tail())








