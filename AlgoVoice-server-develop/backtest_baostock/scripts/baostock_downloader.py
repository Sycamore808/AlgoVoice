#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Baostock Data Downloader
Free A-share data source with no API limits
"""
import sys
import os
from pathlib import Path
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import time

logger = logging.getLogger(__name__)


class BaostockDownloader:
    """Baostock数据下载器 - 免费无限制"""
    
    def __init__(self, data_dir: str = "backtest_baostock/baostock_data"):
        """
        初始化下载器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据子目录
        self.daily_dir = self.data_dir / "daily"
        self.index_dir = self.data_dir / "index"
        self.metadata_dir = self.data_dir / "metadata"
        
        for dir_path in [self.daily_dir, self.index_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.bs = None
        self._connected = False
    
    def connect(self) -> bool:
        """连接Baostock"""
        try:
            import baostock as bs
            self.bs = bs
            
            # 登录系统（不需要账号密码）
            lg = self.bs.login()
            if lg.error_code != '0':
                logger.error(f"Baostock login failed: {lg.error_msg}")
                return False
            
            self._connected = True
            logger.info("✓ Baostock连接成功")
            return True
            
        except ImportError:
            logger.error("未安装baostock。请运行：pip install baostock")
            return False
        except Exception as e:
            logger.error(f"Baostock连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self._connected and self.bs:
            try:
                self.bs.logout()
                self._connected = False
            except:
                pass
    
    def download_stock_list(self) -> pd.DataFrame:
        """
        下载股票列表
        
        Returns:
            股票列表DataFrame
        """
        if not self._connected:
            if not self.connect():
                return pd.DataFrame()
        
        try:
            logger.info("正在下载A股股票列表...")
            
            # 获取所有股票列表（必须传入交易日期）
            # 使用最近的交易日
            trade_date = '2025-12-10'
            rs = self.bs.query_all_stock(day=trade_date)
            
            if rs.error_code != '0':
                logger.error(f"查询失败：{rs.error_msg}")
                return pd.DataFrame()
            
            # 使用while循环读取所有数据
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                logger.error("未获取到股票数据")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            logger.info(f"✓ 获取到 {len(df)} 只股票")
            
            # 保存
            save_path = self.metadata_dir / "stock_list.pkl"
            df.to_pickle(save_path)
            
            return df
            
        except Exception as e:
            logger.error(f"下载股票列表失败：{e}")
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
            stock_code: 股票代码 (e.g., 'sh.600000')
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            
        Returns:
            日线数据DataFrame
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            # 下载日线数据
            rs = self.bs.query_history_k_data_plus(
                stock_code,
                "date,code,open,high,low,close,volume,amount,turn,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"  # 后复权
            )
            
            if rs.error_code != '0':
                logger.warning(f"获取{stock_code}失败：{rs.error_msg}")
                return None
            
            # 使用推荐的get_data()方法
            df = rs.get_data()
            
            if df is None or df.empty:
                return None
            
            # 数据类型转换
            df['date'] = pd.to_datetime(df['date'])
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"下载{stock_code}失败：{e}")
            return None
    
    def download_all_stocks_data(
        self,
        start_date: str,
        end_date: str,
        delay: float = 0.1
    ) -> bool:
        """
        批量下载所有股票数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            delay: 请求间隔（秒）
            
        Returns:
            是否成功
        """
        # 获取股票列表
        stock_list = self.download_stock_list()
        if stock_list.empty:
            logger.error("无法获取股票列表")
            return False
        
        codes = stock_list['code'].tolist()
        total = len(codes)
        
        logger.info(f"开始下载 {total} 只股票")
        logger.info(f"日期范围：{start_date} 至 {end_date}")
        
        success_count = 0
        failed_codes = []
        
        for i, code in enumerate(codes, 1):
            try:
                # 检查是否已存在
                file_path = self.daily_dir / f"{code.replace('.', '_')}.pkl"
                if file_path.exists():
                    logger.info(f"[{i}/{total}] {code} - 已存在，跳过")
                    success_count += 1
                    continue
                
                # 下载数据
                df = self.download_daily_data(code, start_date, end_date)
                if df is not None and not df.empty:
                    # 保存
                    df.to_pickle(file_path)
                    success_count += 1
                    logger.info(f"[{i}/{total}] {code} - 成功（{len(df)}条记录）")
                else:
                    failed_codes.append(code)
                    logger.warning(f"[{i}/{total}] {code} - 无数据")
                
                # 延迟（虽然没有限制，但避免请求过快）
                time.sleep(delay)
                
                # 每100只股票显示进度
                if i % 100 == 0:
                    logger.info(f"进度：{i}/{total} ({i/total*100:.1f}%)")
                
            except Exception as e:
                failed_codes.append(code)
                logger.error(f"[{i}/{total}] {code} - 错误：{e}")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"下载完成！")
        logger.info(f"成功：{success_count}/{total}")
        logger.info(f"失败：{len(failed_codes)}/{total}")
        if failed_codes[:10]:
            logger.info(f"失败示例：{failed_codes[:10]}")
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
            index_code: 指数代码 (e.g., 'sh.000001')
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            logger.info(f"正在下载指数 {index_code}...")
            
            rs = self.bs.query_history_k_data_plus(
                index_code,
                "date,code,open,high,low,close,volume,amount,pctChg",
                start_date=start_date,
                end_date=end_date,
                frequency="d"
            )
            
            if rs.error_code != '0':
                logger.error(f"获取指数数据失败：{rs.error_msg}")
                return None
            
            # 使用推荐的get_data()方法
            df = rs.get_data()
            
            if df is None or df.empty:
                return None
            df['date'] = pd.to_datetime(df['date'])
            for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.set_index('date', inplace=True)
            
            # 保存
            save_path = self.index_dir / f"{index_code.replace('.', '_')}.pkl"
            df.to_pickle(save_path)
            
            logger.info(f"✓ 指数 {index_code} 下载完成（{len(df)}条记录）")
            return df
            
        except Exception as e:
            logger.error(f"下载指数失败：{e}")
            return None
    
    def download_all_required_data(
        self,
        start_date: str = "2000-01-01",
        end_date: str = "2025-12-10"
    ) -> bool:
        """
        下载所有必需数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            是否成功
        """
        logger.info("\n" + "="*60)
        logger.info("Baostock数据下载 - 免费无限制！")
        logger.info("="*60 + "\n")
        
        success = True
        
        # 1. 下载股票列表
        logger.info("\n[1/3] 正在下载股票列表...")
        stock_list = self.download_stock_list()
        if stock_list.empty:
            logger.error("下载股票列表失败")
            success = False
        
        # 2. 下载所有股票数据
        logger.info("\n[2/3] 正在下载所有股票数据...")
        if not self.download_all_stocks_data(start_date, end_date):
            logger.warning("部分股票下载失败")
            success = False
        
        # 3. 下载指数数据
        logger.info("\n[3/3] 正在下载指数数据...")
        indices = {
            'sh.000001': '上证指数',
            'sh.000300': '沪深300',
            'sh.000905': '中证500'
        }
        for code, name in indices.items():
            df = self.download_index_data(code, start_date, end_date)
            if df is None:
                logger.error(f"下载{name}失败")
                success = False
        
        logger.info("\n" + "="*60)
        if success:
            logger.info("所有数据下载成功！")
        else:
            logger.warning("下载完成，但有部分错误")
        logger.info("="*60 + "\n")
        
        return success
    
    def get_data_summary(self) -> dict:
        """获取数据摘要"""
        summary = {
            'daily_stocks': len(list(self.daily_dir.glob('*.pkl'))),
            'indices': len(list(self.index_dir.glob('*.pkl'))),
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
    
    downloader = BaostockDownloader()
    
    # 测试连接
    if downloader.connect():
        print("✓ Baostock connected!")
        
        # 下载少量数据测试
        df = downloader.download_daily_data(
            'sh.600000',
            '2024-01-01',
            '2024-12-31'
        )
        
        if df is not None:
            print(f"✓ Test download successful: {len(df)} records")
            print(df.head())
        
        downloader.disconnect()
    else:
        print("✗ Connection failed")

