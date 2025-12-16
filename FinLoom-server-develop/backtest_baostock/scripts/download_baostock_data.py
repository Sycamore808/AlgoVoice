#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download Baostock Data - Main Script
"""
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backtest_baostock.scripts.baostock_downloader import BaostockDownloader


def setup_logging():
    """Setup logging"""
    log_dir = Path("backtest_baostock/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                log_dir / f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function"""
    print("\n" + "="*60)
    print("Baostock数据下载工具")
    print("免费 & 无限制！")
    print("="*60 + "\n")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create downloader
    downloader = BaostockDownloader()
    
    # Check current status
    summary = downloader.get_data_summary()
    print(f"当前数据状态：")
    print(f"  股票文件：{summary.get('daily_stocks', 0)}")
    print(f"  指数文件：{summary.get('indices', 0)}")
    print(f"  总大小：{summary.get('total_size_mb', 0)} MB")
    print()
    
    if summary.get('daily_stocks', 0) >= 3000:
        print("数据已存在！")
        choice = input("是否重新下载？(yes/no): ").lower()
        if choice != 'yes':
            print("跳过下载。")
            downloader.disconnect()
            return
    
    # Download data
    print("\n开始下载...")
    print("Baostock特点：")
    print("  ✓ 完全免费")
    print("  ✓ 无需登录")
    print("  ✓ 无API限制")
    print("  ✓ 可中断续传")
    print()
    
    try:
        success = downloader.download_all_required_data(
            start_date="2000-01-01",
            end_date="2025-12-10"
        )
        
        if success:
            print("\n" + "="*60)
            print("下载完成！")
            print("="*60)
            
            # Show final summary
            final_summary = downloader.get_data_summary()
            print(f"\n最终数据摘要：")
            print(f"  股票文件：{final_summary.get('daily_stocks', 0)}")
            print(f"  指数文件：{final_summary.get('indices', 0)}")
            print(f"  总大小：{final_summary.get('total_size_mb', 0)} MB")
            print()
            print("下一步：运行 run_backtest.bat")
            
        else:
            print("\n" + "="*60)
            print("下载完成，但有部分错误")
            print("="*60)
            print("请查看日志了解详情")
            print("可以重新运行以下载缺失数据")
            
    except KeyboardInterrupt:
        print("\n\n用户中断下载")
        print("进度已保存")
        print("重新运行可继续")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"下载失败：{e}", exc_info=True)
        print(f"\n错误：{e}")
        sys.exit(1)
        
    finally:
        downloader.disconnect()


if __name__ == "__main__":
    main()

