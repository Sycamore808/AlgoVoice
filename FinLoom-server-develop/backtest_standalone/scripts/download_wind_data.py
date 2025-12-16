#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download Wind Data - Standalone Version
Downloads all required data and saves locally
"""
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from main module
from module_08_execution.backtest.wind_data_downloader import WindDataDownloader

def setup_logging():
    """Setup logging"""
    log_dir = Path("backtest_standalone/logs")
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
    print("Wind Data Download Tool")
    print("="*60 + "\n")
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create downloader with standalone data directory
    data_dir = "backtest_standalone/wind_data"
    downloader = WindDataDownloader(data_dir=data_dir)
    
    # Check current status
    summary = downloader.get_data_summary()
    print(f"Current data status:")
    print(f"  Stock files: {summary.get('daily_stocks', 0)}")
    print(f"  Index files: {summary.get('indices', 0)}")
    print(f"  Industry files: {summary.get('industry_files', 0)}")
    print(f"  Total size: {summary.get('total_size_mb', 0)} MB")
    print()
    
    if summary.get('daily_stocks', 0) >= 3000:
        print("Data already exists!")
        choice = input("Re-download? (yes/no): ").lower()
        if choice != 'yes':
            print("Skipping download.")
            return
    
    # Download data
    print("\nStarting download...")
    print("This may take 2-5 hours.")
    print("You can interrupt and resume later.")
    print()
    
    try:
        success = downloader.download_all_required_data(
            start_date="2000-01-01",
            end_date="2025-12-10"
        )
        
        if success:
            print("\n" + "="*60)
            print("Download Complete!")
            print("="*60)
            
            # Show final summary
            final_summary = downloader.get_data_summary()
            print(f"\nFinal data summary:")
            print(f"  Stock files: {final_summary.get('daily_stocks', 0)}")
            print(f"  Index files: {final_summary.get('indices', 0)}")
            print(f"  Industry files: {final_summary.get('industry_files', 0)}")
            print(f"  Total size: {final_summary.get('total_size_mb', 0)} MB")
            print()
            print("Next step: Run run_backtest.bat")
            
        else:
            print("\n" + "="*60)
            print("Download completed with some errors")
            print("="*60)
            print("Check logs for details")
            print("You can re-run to download missing data")
            
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        print("Progress has been saved")
        print("Re-run to continue")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()








