#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Baostock Data Adapter
Adapts Baostock data format to match the backtest engine requirements
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaostockDataAdapter:
    """Baostock数据适配器"""
    
    def __init__(self, data_dir: str = "backtest_baostock/baostock_data"):
        """初始化适配器"""
        self.data_dir = Path(data_dir)
        self.daily_dir = self.data_dir / "daily"
        self.index_dir = self.data_dir / "index"
        self.metadata_dir = self.data_dir / "metadata"
        
        self._stock_cache = {}
        self._index_cache = {}
    
    def load_stock_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """
        加载股票数据并转换为标准格式
        
        Baostock fields: date, code, open, high, low, close, volume, amount, turn, pctChg
        Required format: date(index), open, high, low, close, volume, amt, turn, pct_chg, mkt_cap_ard
        """
        # Check cache
        if stock_code in self._stock_cache:
            return self._stock_cache[stock_code]
        
        # 加载文件
        file_path = self.daily_dir / f"{stock_code.replace('.', '_')}.pkl"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_pickle(file_path)
            
            # 转换字段名以匹配回测引擎
            df = df.rename(columns={
                'amount': 'amt',
                'pctChg': 'pct_chg'
            })
            
            # 添加缺失字段（如市值，baostock不直接提供，需要计算或估算）
            # 简化处理：使用成交额/换手率粗略估算市值
            if 'mkt_cap_ard' not in df.columns:
                # 市值 = 成交额 / (换手率/100)
                # 这是粗略估算，实际应该用单独的API获取
                df['mkt_cap_ard'] = np.where(
                    df['turn'] > 0,
                    df['amt'] / (df['turn'] / 100),
                    0
                )
            
            self._stock_cache[stock_code] = df
            return df
            
        except Exception as e:
            logger.error(f"Failed to load {stock_code}: {e}")
            return None
    
    def load_index_data(self, index_code: str) -> Optional[pd.DataFrame]:
        """加载指数数据"""
        if index_code in self._index_cache:
            return self._index_cache[index_code]
        
        file_path = self.index_dir / f"{index_code.replace('.', '_')}.pkl"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_pickle(file_path)
            
            # 转换字段名
            df = df.rename(columns={
                'amount': 'amt',
                'pctChg': 'pct_chg'
            })
            
            self._index_cache[index_code] = df
            return df
            
        except Exception as e:
            logger.error(f"Failed to load index {index_code}: {e}")
            return None
    
    def load_stock_list(self) -> Optional[pd.DataFrame]:
        """加载股票列表"""
        file_path = self.metadata_dir / "stock_list.pkl"
        if not file_path.exists():
            return None
        
        try:
            return pd.read_pickle(file_path)
        except Exception as e:
            logger.error(f"Failed to load stock list: {e}")
            return None
    
    def get_trading_dates(
        self,
        start_date: str,
        end_date: str
    ) -> List[datetime]:
        """
        获取交易日列表
        使用上证指数的日期作为交易日历
        """
        index_df = self.load_index_data('sh.000001')
        if index_df is None:
            return []
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        trading_dates = index_df.index[(index_df.index >= start) & (index_df.index <= end)]
        return trading_dates.tolist()
    
    def get_market_index_return(
        self,
        date: datetime,
        index_code: str = 'sh.000001'
    ) -> float:
        """获取市场指数收益率"""
        index_df = self.load_index_data(index_code)
        if index_df is None:
            return 0.0
        
        try:
            return float(index_df.loc[date, 'pct_chg'])
        except:
            return 0.0
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        与原版保持一致
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        try:
            # 1. 量比（当日成交量/过去5日平均成交量）
            df['volume_ratio'] = df['volume'] / df['volume'].rolling(5).mean()
            
            # 2. 移动均线
            df['ma5'] = df['close'].rolling(5).mean()
            df['ma10'] = df['close'].rolling(10).mean()
            df['ma20'] = df['close'].rolling(20).mean()
            df['ma60'] = df['close'].rolling(60).mean()
            
            # 3. 均线趋势
            df['ma5_uptrend'] = df['ma5'] > df['ma5'].shift(1)
            df['ma60_uptrend'] = df['ma60'] > df['ma60'].shift(1)
            
            # 4. 成交量移动平均
            df['volume_ma5'] = df['volume'].rolling(5).mean()
            df['volume_ma10'] = df['volume'].rolling(10).mean()
            
            # 5. 成交量稳定性
            df['volume_stability'] = (
                df['volume'].rolling(10).std() / 
                df['volume'].rolling(10).mean()
            )
            
            # 6. 当日最高是否创新高
            df['is_new_high'] = df['high'] >= df['high'].rolling(20).max()
            
        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
        
        return df








