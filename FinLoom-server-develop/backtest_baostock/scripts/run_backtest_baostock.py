#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run Backtest with Baostock Data
"""
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backtest_baostock.scripts.baostock_data_adapter import BaostockDataAdapter


def setup_logging():
    """Setup logging"""
    log_dir = Path("backtest_baostock/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                log_dir / f'backtest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_sycamore_strategy_backtest(
    data_adapter: BaostockDataAdapter,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000000
):
    """
    运行Sycamore1024策略回测
    使用Baostock数据
    """
    logger = logging.getLogger(__name__)
    
    # 策略参数
    params = {
        'gain_range': [3, 5],
        'volume_ratio_min': 1,
        'turnover_rate_range': [5, 10],
        'market_cap_range': [50, 200],  # 亿元
        'ma_short': 5,
        'ma_long': 60,
        'max_stocks': 10,
        'position_per_stock': 0.1
    }
    
    # 获取交易日
    trading_dates = data_adapter.get_trading_dates(start_date, end_date)
    logger.info(f"Trading days: {len(trading_dates)}")
    
    # 初始化账户
    cash = initial_capital
    portfolio = {}
    daily_records = []
    trade_records = []
    
    # 遍历每个交易日
    for i, date in enumerate(trading_dates):
        if i % 250 == 0:
            logger.info(f"Progress: {i}/{len(trading_dates)} ({i/len(trading_dates)*100:.1f}%)")
        
        try:
            # 这里简化处理：加载所有股票数据会很慢
            # 实际应该预加载或使用数据库
            # 为演示，我们只处理部分数据
            
            # 记录当日状态
            portfolio_value = cash
            for code, shares in portfolio.items():
                # 简化：使用前一日收盘价
                pass
            
            daily_records.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': cash,
                'num_stocks': len(portfolio),
                'market_return': data_adapter.get_market_index_return(date),
                'return': (portfolio_value - initial_capital) / initial_capital * 100
            })
            
        except Exception as e:
            logger.error(f"Error on {date}: {e}")
            continue
    
    # 转换为DataFrame
    import pandas as pd
    results_df = pd.DataFrame(daily_records)
    results_df.set_index('date', inplace=True)
    
    return results_df, trade_records


def main():
    """Main function"""
    print("\n" + "="*80)
    print("Sycamore1024策略回测")
    print("使用Baostock数据（免费无限制！）")
    print("="*80 + "\n")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Configuration
    START_DATE = "2000-01-01"
    END_DATE = "2025-12-10"
    INITIAL_CAPITAL = 10000000
    
    results_dir = Path("backtest_baostock/backtest_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize data adapter
        print("\n[步骤 1/3] 初始化数据适配器...")
        data_adapter = BaostockDataAdapter()
        
        # Check data
        stock_list = data_adapter.load_stock_list()
        if stock_list is None or stock_list.empty:
            print("错误：未找到数据！")
            print("请先运行 download_data.bat 下载数据")
            return
        
        print(f"数据已加载：{len(stock_list)} 只股票")
        
        # Run backtest
        print("\n[步骤 2/3] 运行回测...")
        print("注意：这是简化版本用于测试")
        print("完整版本需要加载所有股票数据")
        
        results_df, trade_records = run_sycamore_strategy_backtest(
            data_adapter,
            START_DATE,
            END_DATE,
            INITIAL_CAPITAL
        )
        
        # Save results
        print("\n[步骤 3/3] 保存结果...")
        results_df.to_csv(results_dir / "backtest_results.csv")
        results_df.to_pickle(results_dir / "backtest_results.pkl")
        
        # Generate report
        total_return = (results_df['portfolio_value'].iloc[-1] / INITIAL_CAPITAL - 1) * 100
        
        report = f"""
{'='*80}
                    Sycamore1024回测报告
                    使用Baostock数据
{'='*80}

回测周期：{START_DATE} 至 {END_DATE}
交易天数：{len(results_df)}

初始资金：{INITIAL_CAPITAL:,.0f}
最终资金：{results_df['portfolio_value'].iloc[-1]:,.0f}

累计收益率：{total_return:.2f}%

{'='*80}
注意：这是简化版本用于测试。
完整版本需要完整实现。
{'='*80}
"""
        
        with open(results_dir / "backtest_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        
        print(f"\n结果已保存到：{results_dir}")
        
    except Exception as e:
        logger.error(f"回测失败：{e}", exc_info=True)
        print(f"\n错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

