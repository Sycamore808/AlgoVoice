#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wind数据下载器 - 下载并本地存储历史数据
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import logging
from typing import Optional, List, Dict
import time

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

class WindDataDownloader:
    """Wind数据下载器，负责下载和本地存储"""
    
    def __init__(self, data_dir: str = "data/backtest_data"):
        """
        初始化数据下载器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据子目录
        self.daily_dir = self.data_dir / "daily"
        self.index_dir = self.data_dir / "index"
        self.industry_dir = self.data_dir / "industry"
        self.metadata_dir = self.data_dir / "metadata"
        
        for dir_path in [self.daily_dir, self.index_dir, self.industry_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.w = None
        self._wind_connected = False
        
    def connect_wind(self) -> bool:
        """连接Wind终端"""
        try:
            from WindPy import w
            self.w = w
            
            # 启动Wind
            result = self.w.start()
            if result.ErrorCode != 0:
                logger.error(f"Wind启动失败: {result.Data}")
                return False
            
            self._wind_connected = True
            logger.info("✅ Wind终端连接成功")
            return True
            
        except ImportError:
            logger.error("❌ WindPy未安装")
            return False
        except Exception as e:
            logger.error(f"❌ Wind连接失败: {e}")
            return False
    
    def download_stock_list(self, trade_date: str = None) -> pd.DataFrame:
        """
        下载股票列表
        
        Args:
            trade_date: 交易日期 YYYYMMDD，默认为最新交易日
            
        Returns:
            股票列表DataFrame
        """
        if not self._wind_connected:
            if not self.connect_wind():
                return pd.DataFrame()
        
        try:
            # 获取A股列表
            logger.info("📥 下载A股列表...")
            result = self.w.wset(
                "sectorconstituent",
                f"date={trade_date or datetime.now().strftime('%Y%m%d')};sectorid=a001010100000000"
            )
            
            if result.ErrorCode != 0:
                logger.error(f"获取股票列表失败: {result.Data}")
                return pd.DataFrame()
            
            df = pd.DataFrame(result.Data, index=result.Fields).T
            logger.info(f"✅ 获取到 {len(df)} 只股票")
            
            # 保存
            save_path = self.metadata_dir / "stock_list.pkl"
            df.to_pickle(save_path)
            
            return df
            
        except Exception as e:
            logger.error(f"下载股票列表失败: {e}")
            return pd.DataFrame()
    
    def download_daily_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        下载单只股票的日线数据
        
        Args:
            stock_code: 股票代码
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            
        Returns:
            日线数据DataFrame
        """
        if not self._wind_connected:
            if not self.connect_wind():
                return None
        
        try:
            # 下载行情数据
            fields = "open,high,low,close,volume,amt,turn,free_turn,pct_chg,mkt_cap_ard"
            result = self.w.wsd(
                stock_code,
                fields,
                start_date,
                end_date,
                "Fill=Previous"
            )
            
            if result.ErrorCode != 0:
                logger.warning(f"获取{stock_code}数据失败: {result.Data}")
                return None
            
            df = pd.DataFrame(result.Data, index=result.Fields, columns=result.Times).T
            df.index.name = 'date'
            df['code'] = stock_code
            
            return df
            
        except Exception as e:
            logger.error(f"下载{stock_code}数据失败: {e}")
            return None
    
    def download_all_stocks_data(
        self,
        start_date: str,
        end_date: str,
        chunk_size: int = 50,
        delay: float = 0.5
    ) -> bool:
        """
        批量下载所有股票数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            chunk_size: 每批下载数量
            delay: 请求间隔（秒）
            
        Returns:
            是否成功
        """
        # 获取股票列表
        stock_list = self.download_stock_list()
        if stock_list.empty:
            logger.error("无法获取股票列表")
            return False
        
        codes = stock_list['wind_code'].tolist() if 'wind_code' in stock_list.columns else []
        total = len(codes)
        
        logger.info(f"📊 开始下载 {total} 只股票的数据")
        logger.info(f"📅 时间范围: {start_date} 至 {end_date}")
        
        success_count = 0
        failed_codes = []
        
        for i in range(0, total, chunk_size):
            chunk = codes[i:i+chunk_size]
            logger.info(f"⏳ 进度: {i+1}/{total} - {i+len(chunk)}/{total}")
            
            for code in chunk:
                try:
                    # 检查是否已存在
                    file_path = self.daily_dir / f"{code.replace('.', '_')}.pkl"
                    if file_path.exists():
                        logger.info(f"⏭️  {code} 数据已存在，跳过")
                        success_count += 1
                        continue
                    
                    # 下载数据
                    df = self.download_daily_data(code, start_date, end_date)
                    if df is not None and not df.empty:
                        # 保存
                        df.to_pickle(file_path)
                        success_count += 1
                        logger.info(f"✅ {code} 下载成功 ({len(df)} 条)")
                    else:
                        failed_codes.append(code)
                        logger.warning(f"⚠️  {code} 下载失败")
                    
                    # 延迟避免API限制
                    time.sleep(delay)
                    
                except Exception as e:
                    failed_codes.append(code)
                    logger.error(f"❌ {code} 处理失败: {e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 下载完成!")
        logger.info(f"📊 成功: {success_count}/{total}")
        logger.info(f"❌ 失败: {len(failed_codes)}/{total}")
        if failed_codes:
            logger.info(f"失败列表: {failed_codes[:10]}...")
        logger.info(f"{'='*60}\n")
        
        return len(failed_codes) == 0
    
    def download_index_data(
        self,
        index_code: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        下载指数数据
        
        Args:
            index_code: 指数代码，如 '000001.SH'（上证指数）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        if not self._wind_connected:
            if not self.connect_wind():
                return None
        
        try:
            logger.info(f"📥 下载指数 {index_code} 数据...")
            
            fields = "open,high,low,close,volume,amt,pct_chg"
            result = self.w.wsd(
                index_code,
                fields,
                start_date,
                end_date,
                ""
            )
            
            if result.ErrorCode != 0:
                logger.error(f"获取指数数据失败: {result.Data}")
                return None
            
            df = pd.DataFrame(result.Data, index=result.Fields, columns=result.Times).T
            df.index.name = 'date'
            df['code'] = index_code
            
            # 保存
            save_path = self.index_dir / f"{index_code.replace('.', '_')}.pkl"
            df.to_pickle(save_path)
            
            logger.info(f"✅ 指数数据下载成功 ({len(df)} 条)")
            return df
            
        except Exception as e:
            logger.error(f"下载指数数据失败: {e}")
            return None
    
    def download_industry_classification(self) -> Optional[pd.DataFrame]:
        """
        下载行业分类数据（申万一级）
        
        Returns:
            行业分类DataFrame
        """
        if not self._wind_connected:
            if not self.connect_wind():
                return None
        
        try:
            logger.info("📥 下载行业分类数据...")
            
            # 获取所有股票的申万一级行业
            stock_list = self.download_stock_list()
            if stock_list.empty:
                return None
            
            codes = stock_list['wind_code'].tolist() if 'wind_code' in stock_list.columns else []
            
            # 批量获取行业
            result = self.w.wss(
                codes,
                "industry_sw",
                f"tradeDate={datetime.now().strftime('%Y%m%d')};industryType=1"
            )
            
            if result.ErrorCode != 0:
                logger.error(f"获取行业分类失败: {result.Data}")
                return None
            
            df = pd.DataFrame({
                'code': result.Codes,
                'industry': result.Data[0] if result.Data else []
            })
            
            # 保存
            save_path = self.industry_dir / "sw_industry_l1.pkl"
            df.to_pickle(save_path)
            
            logger.info(f"✅ 行业分类下载成功 ({len(df)} 只股票)")
            return df
            
        except Exception as e:
            logger.error(f"下载行业分类失败: {e}")
            return None
    
    def download_all_required_data(
        self,
        start_date: str = "2000-01-01",
        end_date: str = "2025-12-10"
    ) -> bool:
        """
        下载所有必需数据（一键下载）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            是否全部成功
        """
        logger.info("\n" + "="*60)
        logger.info("🚀 开始下载回测所需的所有数据")
        logger.info("="*60 + "\n")
        
        success = True
        
        # 1. 下载股票列表
        logger.info("\n【1/4】下载股票列表")
        stock_list = self.download_stock_list()
        if stock_list.empty:
            logger.error("❌ 股票列表下载失败")
            success = False
        
        # 2. 下载所有股票日线数据
        logger.info("\n【2/4】下载所有股票日线数据")
        if not self.download_all_stocks_data(start_date, end_date):
            logger.warning("⚠️  部分股票数据下载失败")
            success = False
        
        # 3. 下载指数数据
        logger.info("\n【3/4】下载指数数据")
        indices = {
            '000001.SH': '上证指数',
            '000300.SH': '沪深300',
            '000905.SH': '中证500'
        }
        for code, name in indices.items():
            df = self.download_index_data(code, start_date, end_date)
            if df is None:
                logger.error(f"❌ {name} 数据下载失败")
                success = False
        
        # 4. 下载行业分类
        logger.info("\n【4/4】下载行业分类")
        industry_df = self.download_industry_classification()
        if industry_df is None:
            logger.error("❌ 行业分类下载失败")
            success = False
        
        logger.info("\n" + "="*60)
        if success:
            logger.info("🎉 所有数据下载完成！")
        else:
            logger.warning("⚠️  部分数据下载失败，但可以继续回测")
        logger.info("="*60 + "\n")
        
        return success
    
    def get_data_summary(self) -> Dict:
        """获取已下载数据的摘要"""
        summary = {
            'daily_stocks': len(list(self.daily_dir.glob('*.pkl'))),
            'indices': len(list(self.index_dir.glob('*.pkl'))),
            'industry_files': len(list(self.industry_dir.glob('*.pkl'))),
            'metadata_files': len(list(self.metadata_dir.glob('*.pkl')))
        }
        
        # 计算数据大小
        total_size = sum(
            f.stat().st_size 
            for f in self.data_dir.rglob('*.pkl')
        ) / (1024 * 1024)  # MB
        
        summary['total_size_mb'] = round(total_size, 2)
        
        return summary


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    downloader = WindDataDownloader()
    
    # 下载所有数据
    downloader.download_all_required_data(
        start_date="2000-01-01",
        end_date="2025-12-10"
    )
    
    # 显示摘要
    summary = downloader.get_data_summary()
    print("\n数据下载摘要:")
    print(f"  股票数据文件: {summary['daily_stocks']}")
    print(f"  指数数据文件: {summary['indices']}")
    print(f"  行业分类文件: {summary['industry_files']}")
    print(f"  元数据文件: {summary['metadata_files']}")
    print(f"  总大小: {summary['total_size_mb']} MB")

