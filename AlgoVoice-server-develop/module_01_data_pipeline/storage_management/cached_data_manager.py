"""
缓存数据管理器
优先从本地数据库读取数据，只在必要时才从AKshare获取
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

from common.logging_system import setup_logger
from module_01_data_pipeline.data_acquisition.akshare_collector import AkshareDataCollector
from module_01_data_pipeline.storage_management.database_manager import DatabaseManager

logger = setup_logger("cached_data_manager")


class CachedDataManager:
    """缓存数据管理器 - 优先使用本地数据"""
    
    def __init__(self, db_path: str = "data/AlgoVoice.db", update_threshold_days: int = 1):
        """
        初始化缓存数据管理器
        
        Args:
            db_path: 数据库路径
            update_threshold_days: 数据更新阈值（天）
        """
        self.db_manager = DatabaseManager(db_path)
        self.collector = AkshareDataCollector(rate_limit=0.3)
        self.update_threshold_days = update_threshold_days
        
        logger.info("✅ 缓存数据管理器已启动 - 优先使用本地数据")
    
    def get_stock_history(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        获取股票历史数据（优先从本地读取）
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD 或 YYYYMMDD)
            end_date: 结束日期 (YYYY-MM-DD 或 YYYYMMDD)
            force_update: 是否强制从网络更新
            
        Returns:
            历史数据DataFrame
        """
        try:
            # 标准化日期格式
            start_date_std = self._standardize_date(start_date)
            end_date_std = self._standardize_date(end_date)
            
            if not force_update:
                # 1. 先尝试从本地数据库读取
                local_data = self.db_manager.get_stock_prices(
                    symbol=symbol,
                    start_date=start_date_std,
                    end_date=end_date_std
                )
                
                if not local_data.empty:
                    # 检查数据是否需要更新
                    need_update = self._check_need_update(local_data, end_date_std)
                    
                    if not need_update:
                        logger.info(f"✅ 从本地数据库读取 {symbol} 数据 ({len(local_data)} 条)")
                        return local_data
                    else:
                        logger.info(f"⚠️ 本地数据需要更新，从网络获取最新数据...")
            
            # 2. 从网络获取数据
            logger.info(f"🌐 从AKshare获取 {symbol} 数据...")
            
            # 转换为AKshare格式 (YYYYMMDD)
            start_date_ak = start_date_std.replace("-", "")
            end_date_ak = end_date_std.replace("-", "")
            
            df = self.collector.fetch_stock_history(
                symbol=symbol,
                start_date=start_date_ak,
                end_date=end_date_ak,
                period="daily",
                adjust="qfq"
            )
            
            if not df.empty:
                # 标准化列名
                df = self._standardize_columns(df)
                
                # 保存到本地数据库
                self.db_manager.save_stock_prices(symbol, df)
                logger.info(f"✅ 已更新本地数据库 {symbol} ({len(df)} 条)")
                
                return df
            else:
                logger.warning(f"⚠️ 未获取到 {symbol} 的数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取 {symbol} 历史数据失败: {e}")
            
            # 如果网络获取失败，尝试返回本地数据（即使可能过期）
            try:
                local_data = self.db_manager.get_stock_prices(
                    symbol=symbol,
                    start_date=start_date_std,
                    end_date=end_date_std
                )
                if not local_data.empty:
                    logger.warning(f"⚠️ 返回本地缓存数据 {symbol} (可能不是最新)")
                    return local_data
            except:
                pass
            
            return pd.DataFrame()
    
    def get_stock_list(self, force_update: bool = False) -> pd.DataFrame:
        """
        获取股票列表（优先从本地读取）
        
        Args:
            force_update: 是否强制从网络更新
            
        Returns:
            股票列表DataFrame
        """
        try:
            if not force_update:
                # TODO: 从数据库读取股票列表
                # 目前直接从网络获取
                pass
            
            # 从AKshare获取
            logger.info("🌐 从AKshare获取股票列表...")
            stock_list = self.collector.fetch_stock_list("A股")
            
            if not stock_list.empty:
                logger.info(f"✅ 获取到 {len(stock_list)} 只股票")
                
                # 保存到数据库
                for _, row in stock_list.iterrows():
                    try:
                        symbol = row.get('代码', row.get('symbol', ''))
                        name = row.get('名称', row.get('name', ''))
                        
                        if symbol and name:
                            self.db_manager.save_stock_info(
                                symbol=str(symbol),
                                name=str(name),
                                sector=row.get('行业', None)
                            )
                    except:
                        continue
            
            return stock_list
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_macro_data(
        self,
        indicator_type: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        获取宏观数据（优先从本地读取）
        
        Args:
            indicator_type: 指标类型 (GDP, CPI, PMI等)
            force_update: 是否强制从网络更新
            
        Returns:
            宏观数据DataFrame
        """
        try:
            if not force_update:
                # 从本地数据库读取
                local_data = self.db_manager.get_macro_data(indicator_type=indicator_type)
                
                if not local_data.empty:
                    # 检查数据是否需要更新（宏观数据更新频率较低）
                    last_date = local_data['date'].max()
                    days_old = (datetime.now() - pd.to_datetime(last_date)).days
                    
                    if days_old < 30:  # 30天内的数据认为是新的
                        logger.info(f"✅ 从本地数据库读取 {indicator_type} 数据 ({len(local_data)} 条)")
                        return local_data
            
            # 从网络获取
            logger.info(f"🌐 从AKshare获取 {indicator_type} 数据...")
            from module_01_data_pipeline.data_acquisition.alternative_data_collector import ChineseAlternativeDataCollector
            
            alt_collector = ChineseAlternativeDataCollector(rate_limit=0.5)
            macro_data = alt_collector.fetch_macro_economic_data(indicator_type)
            
            if macro_data and indicator_type in macro_data:
                df = macro_data[indicator_type]
                if not df.empty:
                    # 保存到数据库
                    self.db_manager.save_macro_data(indicator_type, df)
                    logger.info(f"✅ 已更新本地数据库 {indicator_type} ({len(df)} 条)")
                    return df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取 {indicator_type} 宏观数据失败: {e}")
            
            # 返回本地数据（即使可能过期）
            try:
                local_data = self.db_manager.get_macro_data(indicator_type=indicator_type)
                if not local_data.empty:
                    logger.warning(f"⚠️ 返回本地缓存数据 {indicator_type}")
                    return local_data
            except:
                pass
            
            return pd.DataFrame()
    
    def get_sector_data(
        self,
        date: Optional[str] = None,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        获取板块数据（优先从本地读取）
        
        Args:
            date: 日期 (YYYY-MM-DD)，None表示最新
            force_update: 是否强制从网络更新
            
        Returns:
            板块数据DataFrame
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            if not force_update:
                # 从本地数据库读取
                local_data = self.db_manager.get_sector_data(date=date)
                
                if not local_data.empty:
                    logger.info(f"✅ 从本地数据库读取板块数据 ({len(local_data)} 个板块)")
                    return local_data
            
            # 从网络获取
            logger.info("🌐 从AKshare获取板块数据...")
            from module_01_data_pipeline.data_acquisition.alternative_data_collector import ChineseAlternativeDataCollector
            
            alt_collector = ChineseAlternativeDataCollector(rate_limit=0.5)
            sector_df = alt_collector.fetch_sector_performance()
            
            if not sector_df.empty:
                # 保存到数据库
                self.db_manager.save_sector_data(sector_df, date=date)
                logger.info(f"✅ 已更新本地数据库板块数据 ({len(sector_df)} 个板块)")
                return sector_df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取板块数据失败: {e}")
            
            # 返回本地数据
            try:
                local_data = self.db_manager.get_sector_data(date=date)
                if not local_data.empty:
                    logger.warning(f"⚠️ 返回本地缓存板块数据")
                    return local_data
            except:
                pass
            
            return pd.DataFrame()
    
    def update_latest_data(self, symbols: List[str] = None):
        """
        更新最新数据（每日增量更新）
        
        Args:
            symbols: 要更新的股票代码列表，None表示更新所有
        """
        logger.info("开始更新最新数据...")
        
        try:
            # 如果没有指定股票，从数据库获取所有股票
            if symbols is None:
                symbols = self.db_manager.get_symbols_list()
                if not symbols:
                    logger.warning("数据库中没有股票数据，请先运行初始化脚本")
                    return
            
            today = datetime.now().strftime("%Y%m%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
            
            updated_count = 0
            for symbol in symbols:
                try:
                    # 获取最近2天的数据（确保获取到最新）
                    df = self.collector.fetch_stock_history(
                        symbol=symbol,
                        start_date=yesterday,
                        end_date=today,
                        period="daily",
                        adjust="qfq"
                    )
                    
                    if not df.empty:
                        df = self._standardize_columns(df)
                        self.db_manager.save_stock_prices(symbol, df)
                        updated_count += 1
                        
                        if updated_count % 10 == 0:
                            logger.info(f"已更新 {updated_count}/{len(symbols)} 只股票")
                    
                except Exception as e:
                    logger.error(f"更新 {symbol} 失败: {e}")
                    continue
            
            logger.info(f"✅ 完成更新，共更新 {updated_count} 只股票")
            
        except Exception as e:
            logger.error(f"更新最新数据失败: {e}")
    
    def _check_need_update(self, df: pd.DataFrame, end_date: str) -> bool:
        """
        检查数据是否需要更新
        
        Args:
            df: 本地数据
            end_date: 请求的结束日期
            
        Returns:
            是否需要更新
        """
        if df.empty:
            return True
        
        # 获取本地数据的最后日期
        last_date = df.index.max()
        
        # 转换为datetime
        if isinstance(last_date, str):
            last_date = pd.to_datetime(last_date)
        
        end_date_dt = pd.to_datetime(end_date)
        
        # 计算天数差
        days_diff = (end_date_dt - last_date).days
        
        # 如果数据超过阈值天数，需要更新
        return days_diff > self.update_threshold_days
    
    def _standardize_date(self, date_str: str) -> str:
        """
        标准化日期格式为 YYYY-MM-DD
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD 或 YYYYMMDD)
            
        Returns:
            标准化的日期字符串 (YYYY-MM-DD)
        """
        # 去除可能的连字符
        date_str = date_str.replace("-", "")
        
        # 转换为 YYYY-MM-DD 格式
        if len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        return date_str
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化DataFrame列名"""
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'pct_change',
            '涨跌额': 'change',
            '换手率': 'turnover_rate',
        }
        
        df = df.copy()
        df.rename(columns=column_mapping, inplace=True)
        
        return df
    
    def get_statistics(self) -> Dict:
        """获取缓存统计信息"""
        return self.db_manager.get_database_stats()


# 全局实例（单例模式）
_global_cached_manager = None


def get_cached_data_manager(db_path: str = "data/AlgoVoice.db") -> CachedDataManager:
    """
    获取全局缓存数据管理器实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        缓存数据管理器实例
    """
    global _global_cached_manager
    if _global_cached_manager is None:
        _global_cached_manager = CachedDataManager(db_path)
    return _global_cached_manager






