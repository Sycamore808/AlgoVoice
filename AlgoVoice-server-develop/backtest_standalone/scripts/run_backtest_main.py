#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run Backtest - Standalone Version
Main entry point for running backtest
"""
import sys
import os
from pathlib import Path
import logging
from datetime import datetime
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from main modules
from module_08_execution.backtest.local_data_manager import LocalDataManager
from module_08_execution.backtest.sycamore_backtest_engine import SycamoreBacktestEngine
from module_08_execution.backtest.backtest_visualizer import BacktestVisualizer

def setup_logging():
    """Setup logging"""
    log_dir = Path("backtest_standalone/logs")
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

def main():
    """Main function"""
    print("\n" + "="*80)
    print("Sycamore1024 Strategy Backtest")
    print("25 Years Historical Backtest (2000-2025)")
    print("="*80 + "\n")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Configuration
    START_DATE = "2000-01-01"
    END_DATE = "2025-12-10"
    INITIAL_CAPITAL = 10000000  # 10 million
    
    data_dir = "backtest_standalone/wind_data"
    results_dir = "backtest_standalone/backtest_results"
    
    try:
        # Step 1: Initialize data manager
        print("\n[Step 1/4] Initializing data manager...")
        print("-" * 80)
        
        data_manager = LocalDataManager(data_dir=data_dir)
        
        # Check data
        stock_list = data_manager.load_stock_list()
        if stock_list is None or stock_list.empty:
            print("ERROR: No data found!")
            print(f"Please run download_data.bat first to download data.")
            return
        
        print(f"Data loaded successfully")
        print()
        
        # Step 2: Run backtest
        print("\n[Step 2/4] Running backtest...")
        print("-" * 80)
        print(f"Period: {START_DATE} to {END_DATE}")
        print(f"Initial capital: {INITIAL_CAPITAL:,.0f}")
        print()
        
        engine = SycamoreBacktestEngine(
            initial_capital=INITIAL_CAPITAL,
            data_manager=data_manager
        )
        
        results_df = engine.run_backtest(START_DATE, END_DATE)
        
        if results_df.empty:
            print("ERROR: Backtest produced no results")
            return
        
        # Step 3: Save results
        print("\n[Step 3/4] Saving results...")
        print("-" * 80)
        
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        
        results_df.to_csv(Path(results_dir) / "backtest_results.csv")
        results_df.to_pickle(Path(results_dir) / "backtest_results.pkl")
        
        print(f"Results saved to: {results_dir}")
        print()
        
        # Step 4: Generate visualizations
        print("\n[Step 4/4] Generating charts...")
        print("-" * 80)
        
        visualizer = BacktestVisualizer(output_dir=results_dir)
        chart_paths = visualizer.generate_all_charts(
            results_df,
            engine.trade_records,
            data_manager
        )
        
        # Generate text report
        print("\nGenerating text report...")
        
        total_return = (results_df['portfolio_value'].iloc[-1] / INITIAL_CAPITAL - 1) * 100
        years = (results_df.index[-1] - results_df.index[0]).days / 365
        annual_return = ((1 + total_return/100) ** (1/years) - 1) * 100
        
        daily_returns = results_df['portfolio_value'].pct_change()
        sharpe = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        
        cummax = results_df['portfolio_value'].cummax()
        drawdown = (results_df['portfolio_value'] - cummax) / cummax * 100
        max_drawdown = drawdown.min()
        
        report = f"""
{'='*80}
                    Sycamore1024 Strategy Backtest Report
{'='*80}

Backtest Period: {START_DATE} to {END_DATE}
Trading Days: {len(results_df)}
Years: {years:.1f}

Initial Capital: {INITIAL_CAPITAL:,.0f}
Final Capital: {results_df['portfolio_value'].iloc[-1]:,.0f}

{'='*80}
                        Performance Metrics
{'='*80}
Cumulative Return: {total_return:.2f}%
Annual Return: {annual_return:.2f}%
Sharpe Ratio: {sharpe:.2f}
Max Drawdown: {max_drawdown:.2f}%

{'='*80}
                        Trading Statistics
{'='*80}
Total Trades: {len(engine.trade_records)}
Buy Orders: {len([t for t in engine.trade_records if t['action'] == 'buy'])}
Sell Orders: {len([t for t in engine.trade_records if t['action'] == 'sell'])}
Avg Positions: {results_df['num_stocks'].mean():.1f}
Max Positions: {results_df['num_stocks'].max():.0f}

{'='*80}
                        Generated Files
{'='*80}
"""
        for name, path in chart_paths.items():
            report += f"{name}: {path}\n"
        
        report += f"\n{'='*80}\n"
        report += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*80}\n"
        
        # Save report
        report_path = Path(results_dir) / "backtest_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary
        print(report)
        
        print("\n" + "="*80)
        print("Backtest Complete!")
        print("="*80)
        print(f"\nResults location: {results_dir}")
        print("\nFiles generated:")
        print("  - backtest_results.csv (data)")
        print("  - backtest_report.txt (report)")
        print("  - 4 x PNG charts (visualizations)")
        print()
        
    except KeyboardInterrupt:
        print("\n\nBacktest interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()








