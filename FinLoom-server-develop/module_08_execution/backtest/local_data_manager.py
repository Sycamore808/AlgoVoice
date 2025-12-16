"""
本地数据管理器 - 高效读取和管理下载的数据
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)


class LocalDataManager:
    """本地数据管理器"""
    
    def __init__(self, data_dir: str = "data/backtest_data"):
        """初始化数据管理器"""
        self.data_dir = Path(data_dir)
        self.daily_dir = self.data_dir / "daily"
        self.index_dir = self.data_dir / "index"
        self.industry_dir = self.data_dir / "industry"
        self.metadata_dir = self.data_dir / "metadata"
        
        # 数据缓存
        self._stock_cache = {}
        self._index_cache = {}
        self._industry_cache = None
        self._stock_list_cache = None
        
    def load_stock_data(self, stock_code: str) -> Optional[pd.DataFrame]:
        """
        加载单只股票数据
        
        Args:
            stock_code: 股票代码
            
        Returns:
            股票数据DataFrame
        """
        # 检查缓存
        if stock_code in self._stock_cache:
            return self._stock_cache[stock_code]
        
        # 从文件加载
        file_path = self.daily_dir / f"{stock_code.replace('.', '_')}.pkl"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_pickle(file_path)
            self._stock_cache[stock_code] = df
            return df
        except Exception as e:
            logger.error(f"加载{stock_code}数据失败: {e}")
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
            self._index_cache[index_code] = df
            return df
        except Exception as e:
            logger.error(f"加载指数{index_code}数据失败: {e}")
            return None
    
    def load_industry_classification(self) -> Optional[pd.DataFrame]:
        """加载行业分类"""
        if self._industry_cache is not None:
            return self._industry_cache
        
        file_path = self.industry_dir / "sw_industry_l1.pkl"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_pickle(file_path)
            self._industry_cache = df
            return df
        except Exception as e:
            logger.error(f"加载行业分类失败: {e}")
            return None
    
    def load_stock_list(self) -> Optional[pd.DataFrame]:
        """加载股票列表"""
        if self._stock_list_cache is not None:
            return self._stock_list_cache
        
        file_path = self.metadata_dir / "stock_list.pkl"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_pickle(file_path)
            self._stock_list_cache = df
            return df
        except Exception as e:
            logger.error(f"加载股票列表失败: {e}")
            return None
    
    def get_trading_dates(
        self,
        start_date: str,
        end_date: str
    ) -> List[datetime]:
        """
        获取交易日列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日列表
        """
        # 使用上证指数的日期作为交易日历
        index_df = self.load_index_data('000001.SH')
        if index_df is None:
            return []
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        trading_dates = index_df.index[(index_df.index >= start) & (index_df.index <= end)]
        return trading_dates.tolist()
    
    def get_stock_data_on_date(
        self,
        date: datetime,
        lookback_days: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        获取指定日期所有股票的数据
        
        Args:
            date: 指定日期
            lookback_days: 回看天数（用于计算指标）
            
        Returns:
            {股票代码: 数据DataFrame}
        """
        result = {}
        start_date = date - timedelta(days=lookback_days + 100)  # 多留一些
        
        # 遍历所有股票文件
        for file_path in self.daily_dir.glob('*.pkl'):
            try:
                df = pd.read_pickle(file_path)
                if df is None or df.empty:
                    continue
                
                # 筛选日期范围
                df_filtered = df[(df.index <= date) & (df.index >= start_date)]
                if not df_filtered.empty:
                    code = file_path.stem.replace('_', '.')
                    result[code] = df_filtered
                    
            except Exception as e:
                logger.warning(f"读取{file_path}失败: {e}")
                continue
        
        return result
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            添加指标后的DataFrame
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        try:
            # 1. 涨跌幅（如果没有）
            if 'pct_chg' not in df.columns:
                df['pct_chg'] = df['close'].pct_change() * 100
            
            # 2. 量比（当日成交量/过去5日平均成交量）
            df['volume_ratio'] = df['volume'] / df['volume'].rolling(5).mean()
            
            # 3. 移动均线
            df['ma5'] = df['close'].rolling(5).mean()
            df['ma10'] = df['close'].rolling(10).mean()
            df['ma20'] = df['close'].rolling(20).mean()
            df['ma60'] = df['close'].rolling(60).mean()
            
            # 4. 均线趋势（是否向上）
            df['ma5_uptrend'] = df['ma5'] > df['ma5'].shift(1)
            df['ma60_uptrend'] = df['ma60'] > df['ma60'].shift(1)
            
            # 5. 成交量移动平均
            df['volume_ma5'] = df['volume'].rolling(5).mean()
            df['volume_ma10'] = df['volume'].rolling(10).mean()
            
            # 6. 成交量稳定性（标准差/均值）
            df['volume_stability'] = (
                df['volume'].rolling(10).std() / 
                df['volume'].rolling(10).mean()
            )
            
            # 7. 当日最高是否创新高（20日）
            df['is_new_high'] = df['high'] >= df['high'].rolling(20).max()
            
        except Exception as e:
            logger.error(f"计算指标失败: {e}")
        
        return df
    
    def get_market_index_return(
        self,
        date: datetime,
        index_code: str = '000001.SH'
    ) -> float:
        """
        获取市场指数收益率
        
        Args:
            date: 日期
            index_code: 指数代码
            
        Returns:
            收益率（%）
        """
        index_df = self.load_index_data(index_code)
        if index_df is None:
            return 0.0
        
        try:
            return float(index_df.loc[date, 'pct_chg'])
        except:
            return 0.0
    
    def clear_cache(self):
        """清除缓存"""
        self._stock_cache.clear()
        self._index_cache.clear()
        self._industry_cache = None
        self._stock_list_cache = None
        logger.info("缓存已清除")








