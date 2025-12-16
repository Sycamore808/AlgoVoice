========================================
  Sycamore1024 Backtest System
  Standalone Tool - Direct Use
========================================

No Installation Needed!
Your WindPy is already installed:
  - F:\Conda
  - F:\SOFTWARE\MATLAB (backup)

========================================
  Quick Start (2 Steps)
========================================

STEP 1: Test Wind Connection
-----------------------------
1. Open Wind Terminal & Login
2. Run: test_wind.bat

Expected: SUCCESS!

STEP 2: Download & Backtest
----------------------------
1. Run: download_data.bat (first time, 2-5 hours)
2. Run: run_backtest.bat (30min-2hr)

Results: backtest_results/

========================================
  Features
========================================

✓ Uses your existing WindPy (F:\Conda)
✓ No virtual environment needed
✓ Simple & direct
✓ Fast execution
✓ Independent data storage
✓ Professional charts & reports

========================================
  File Structure
========================================

backtest_standalone/
├── test_wind.bat           <- Start here
├── download_data.bat       <- Download data
├── run_backtest.bat        <- Run backtest
├── install_packages.bat    <- Optional
│
├── scripts/                <- Python code
│   ├── test_wind.py
│   ├── download_wind_data.py
│   └── run_backtest_main.py
│
├── wind_data/              <- Downloaded data (auto-created)
├── backtest_results/       <- Results (auto-created)
└── logs/                   <- Logs (auto-created)

========================================
  What You Get
========================================

After running backtest:

1. Text Report
   - Cumulative return
   - Annual return
   - Sharpe ratio
   - Max drawdown
   - Trading statistics

2. Four Charts (PNG)
   - Monthly return heatmap
   - Position trend
   - Performance dashboard
   - Industry attribution

3. Data Files (CSV/PKL)
   - Daily portfolio values
   - Trade records
   - Position history

========================================
  Your Advantage
========================================

✓ WindPy already installed
✓ No complex setup
✓ Just 2 steps to start
✓ Time saved: 10-15 minutes

Start now: test_wind.bat

========================================
  Support
========================================

Documentation:
  - README.txt (this file)
  - USAGE.txt (detailed guide)
  - ✅直接开始-无需安装.txt

Paths:
  - WindPy: F:\Conda or F:\SOFTWARE\MATLAB
  - Data: wind_data/
  - Results: backtest_results/
  - Logs: logs/

========================================
