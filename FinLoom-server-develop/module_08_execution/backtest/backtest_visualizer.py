"""
回测可视化生成器 - 生成各种分析图表
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)


class BacktestVisualizer:
    """回测可视化器"""
    
    def __init__(self, output_dir: str = "data/backtest_results"):
        """
        初始化可视化器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图风格
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (16, 10)
        plt.rcParams['font.size'] = 10
    
    def generate_monthly_return_heatmap(
        self,
        results_df: pd.DataFrame,
        save_path: Optional[str] = None
    ) -> str:
        """
        生成月度收益热力图
        
        Args:
            results_df: 回测结果DataFrame
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        logger.info("📊 生成月度收益热力图...")
        
        # 计算每日收益率
        results_df = results_df.copy()
        results_df['daily_return'] = results_df['portfolio_value'].pct_change() * 100
        
        # 按年月分组计算收益
        results_df['year'] = results_df.index.year
        results_df['month'] = results_df.index.month
        
        monthly_returns = results_df.groupby(['year', 'month'])['daily_return'].sum().reset_index()
        monthly_returns_pivot = monthly_returns.pivot(index='year', columns='month', values='daily_return')
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})
        
        # 热力图
        sns.heatmap(
            monthly_returns_pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=0,
            cbar_kws={'label': '月度收益率 (%)'},
            ax=ax1,
            linewidths=0.5,
            linecolor='gray'
        )
        
        ax1.set_title('月度收益率热力图', fontsize=16, pad=20)
        ax1.set_xlabel('月份', fontsize=12)
        ax1.set_ylabel('年份', fontsize=12)
        
        # 计算统计信息
        total_return = (results_df['portfolio_value'].iloc[-1] / results_df['portfolio_value'].iloc[0] - 1) * 100
        avg_monthly_return = monthly_returns['daily_return'].mean()
        win_rate = (monthly_returns['daily_return'] > 0).sum() / len(monthly_returns) * 100
        
        # 添加统计信息文本
        stats_text = f"""
策略统计指标:
━━━━━━━━━━━━━━━━━━━━━━
累计收益率: {total_return:.2f}%
月均收益率: {avg_monthly_return:.2f}%
月度胜率: {win_rate:.1f}%
盈利月份: {(monthly_returns['daily_return'] > 0).sum()}
亏损月份: {(monthly_returns['daily_return'] < 0).sum()}
最大月收益: {monthly_returns['daily_return'].max():.2f}%
最大月亏损: {monthly_returns['daily_return'].min():.2f}%
        """
        
        ax2.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        ax2.axis('off')
        
        # 月度收益分布柱状图
        ax2_bar = fig.add_subplot(2, 2, 3)
        monthly_avg = monthly_returns.groupby('month')['daily_return'].mean()
        colors = ['green' if x > 0 else 'red' for x in monthly_avg]
        ax2_bar.bar(monthly_avg.index, monthly_avg.values, color=colors, alpha=0.7)
        ax2_bar.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2_bar.set_xlabel('月份')
        ax2_bar.set_ylabel('平均收益率 (%)')
        ax2_bar.set_title('各月份历史平均收益分布')
        ax2_bar.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        if save_path is None:
            save_path = self.output_dir / "monthly_return_heatmap.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ 月度收益热力图已保存: {save_path}")
        return str(save_path)
    
    def generate_position_trend(
        self,
        results_df: pd.DataFrame,
        trade_records: List[Dict],
        save_path: Optional[str] = None
    ) -> str:
        """
        生成持仓数据趋势图
        
        Args:
            results_df: 回测结果DataFrame
            trade_records: 交易记录
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        logger.info("📊 生成持仓数据趋势图...")
        
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))
        
        # 1. 持仓个数趋势
        ax1 = axes[0]
        results_df['num_stocks'].plot(ax=ax1, color='blue', linewidth=1.5, label='持仓股数')
        results_df['num_stocks'].rolling(20).mean().plot(
            ax=ax1, color='red', linewidth=1, linestyle='--', label='20日均线'
        )
        ax1.set_title('持仓个数趋势', fontsize=14)
        ax1.set_ylabel('股票数量')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 每日换手率与持股数量
        trades_df = pd.DataFrame(trade_records)
        if not trades_df.empty:
            daily_trades = trades_df.groupby('date').size()
            
            ax2 = axes[1]
            ax2_twin = ax2.twinx()
            
            # 左轴：每日持股数量
            results_df['stock_value'].plot(
                ax=ax2, color='purple', linewidth=1, alpha=0.6, label='股票市值'
            )
            ax2.set_ylabel('股票市值 (元)', color='purple')
            ax2.tick_params(axis='y', labelcolor='purple')
            
            # 右轴：每日换手
            daily_trades.plot(ax=ax2_twin, color='orange', linewidth=1.5, label='每日换手次数')
            ax2_twin.set_ylabel('换手次数', color='orange')
            ax2_twin.tick_params(axis='y', labelcolor='orange')
            
            ax2.set_title('每日换手率与持股数量', fontsize=14)
            ax2.grid(True, alpha=0.3)
            
            # 合并图例
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        else:
            ax2 = axes[1]
            ax2.text(0.5, 0.5, '无交易数据', ha='center', va='center', fontsize=14)
            ax2.set_title('每日换手率与持股数量', fontsize=14)
        
        # 3. 持仓占比
        ax3 = axes[2]
        results_df['position_ratio'] = (
            results_df['stock_value'] / results_df['portfolio_value'] * 100
        )
        
        # 填充区域图
        ax3.fill_between(
            results_df.index,
            0,
            results_df['position_ratio'],
            color='orange',
            alpha=0.5,
            label='持仓占比'
        )
        ax3.fill_between(
            results_df.index,
            results_df['position_ratio'],
            100,
            color='lightblue',
            alpha=0.5,
            label='现金占比'
        )
        
        ax3.set_title('持仓占比', fontsize=14)
        ax3.set_ylabel('占比 (%)')
        ax3.set_ylim(0, 100)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 添加统计信息
        stats_text = f"""持仓数据统计:
最高持仓数: {results_df['num_stocks'].max():.0f}
最低持仓数: {results_df['num_stocks'].min():.0f}
平均持仓数: {results_df['num_stocks'].mean():.1f}
持仓占比: {results_df['position_ratio'].iloc[-1]:.1f}%
"""
        
        fig.text(0.98, 0.02, stats_text, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                 verticalalignment='bottom', horizontalalignment='right')
        
        plt.tight_layout()
        
        # 保存
        if save_path is None:
            save_path = self.output_dir / "position_trend.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ 持仓数据趋势图已保存: {save_path}")
        return str(save_path)
    
    def generate_performance_dashboard(
        self,
        results_df: pd.DataFrame,
        save_path: Optional[str] = None
    ) -> str:
        """
        生成绩效指标综合仪表盘
        
        Args:
            results_df: 回测结果DataFrame
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        logger.info("📊 生成绩效指标综合仪表盘...")
        
        # 计算各种绩效指标
        results_df = results_df.copy()
        results_df['daily_return'] = results_df['portfolio_value'].pct_change() * 100
        results_df['cumulative_return'] = (
            (results_df['portfolio_value'] / results_df['portfolio_value'].iloc[0] - 1) * 100
        )
        
        # 计算指标
        total_return = results_df['cumulative_return'].iloc[-1]
        annual_return = (
            (1 + total_return/100) ** (365 / (results_df.index[-1] - results_df.index[0]).days) - 1
        ) * 100
        
        daily_returns = results_df['daily_return'].dropna()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if len(daily_returns) > 0 else 0
        
        # 最大回撤
        cummax = results_df['portfolio_value'].cummax()
        drawdown = (results_df['portfolio_value'] - cummax) / cummax * 100
        max_drawdown = drawdown.min()
        
        # Sortino比率
        downside_returns = daily_returns[daily_returns < 0]
        sortino_ratio = (
            daily_returns.mean() / downside_returns.std() * np.sqrt(252)
            if len(downside_returns) > 0 else 0
        )
        
        # 信息比率（相对市场）
        excess_return = daily_returns - results_df['market_return']
        info_ratio = excess_return.mean() / excess_return.std() * np.sqrt(252) if len(excess_return) > 0 else 0
        
        # Beta
        market_returns = results_df['market_return'].dropna()
        if len(market_returns) > 0 and len(daily_returns) > 0:
            covariance = np.cov(daily_returns, market_returns)[0][1]
            market_variance = np.var(market_returns)
            beta = covariance / market_variance if market_variance != 0 else 0
        else:
            beta = 0
        
        # Alpha
        alpha = annual_return - beta * market_returns.mean() * 252
        
        # 创建仪表盘
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Alpha指标
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_indicator(ax1, alpha, "Alpha", "blue", range_vals=[-5, 30])
        
        # 2. Beta指标
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_indicator(ax2, beta, "Beta", "red", range_vals=[0, 2])
        
        # 3. Sharpe比率
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_indicator(ax3, sharpe_ratio, "Sharpe比率", "green", range_vals=[-1, 3])
        
        # 4. Sortino比率
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_indicator(ax4, sortino_ratio, "Sortino比率", "orange", range_vals=[-1, 4])
        
        # 5. Information Ratio
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_indicator(ax5, info_ratio, "Information Ratio", "purple", range_vals=[-2, 3])
        
        # 6. 最大回撤
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_indicator(ax6, max_drawdown, "最大回撤 (%)", "darkred", range_vals=[-50, 0])
        
        # 7. 累计收益曲线
        ax7 = fig.add_subplot(gs[2, :])
        results_df['cumulative_return'].plot(ax=ax7, color='blue', linewidth=2, label='策略收益')
        
        # 添加市场基准
        market_cumulative = (results_df['market_return'].cumsum())
        market_cumulative.plot(ax=ax7, color='red', linewidth=1.5, linestyle='--', label='市场基准')
        
        ax7.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax7.set_title('累计收益曲线对比', fontsize=14)
        ax7.set_ylabel('累计收益率 (%)')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        ax7.fill_between(results_df.index, 0, results_df['cumulative_return'],
                         where=(results_df['cumulative_return'] >= 0),
                         color='green', alpha=0.1)
        ax7.fill_between(results_df.index, 0, results_df['cumulative_return'],
                         where=(results_df['cumulative_return'] < 0),
                         color='red', alpha=0.1)
        
        # 添加总体统计
        stats_text = f"""
绩效统计摘要:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
累计收益率: {total_return:.2f}%
年化收益率: {annual_return:.2f}%
夏普比率: {sharpe_ratio:.2f}
索提诺比率: {sortino_ratio:.2f}
信息比率: {info_ratio:.2f}
Alpha: {alpha:.2f}%
Beta: {beta:.2f}
最大回撤: {max_drawdown:.2f}%
胜率: {(daily_returns > 0).sum() / len(daily_returns) * 100:.1f}%
        """
        
        fig.text(0.98, 0.97, stats_text, fontsize=10,
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                 verticalalignment='top', horizontalalignment='right')
        
        plt.suptitle('绩效指标综合仪表盘', fontsize=18, y=0.98)
        
        # 保存
        if save_path is None:
            save_path = self.output_dir / "performance_dashboard.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ 绩效指标综合仪表盘已保存: {save_path}")
        return str(save_path)
    
    def _plot_indicator(
        self,
        ax,
        value: float,
        title: str,
        color: str,
        range_vals: List[float]
    ):
        """绘制单个指标"""
        # 简化的指标显示
        ax.text(0.5, 0.6, f"{value:.2f}", ha='center', va='center',
                fontsize=32, fontweight='bold', color=color)
        ax.text(0.5, 0.3, title, ha='center', va='center',
                fontsize=14, fontweight='bold')
        
        # 添加背景色（根据值的好坏）
        if "Alpha" in title or "Sharpe" in title or "Sortino" in title or "Information" in title:
            bg_color = 'lightgreen' if value > 0 else 'lightcoral'
        elif "最大回撤" in title:
            bg_color = 'lightgreen' if value > -20 else 'lightcoral'
        elif "Beta" in title:
            bg_color = 'lightblue'
        else:
            bg_color = 'white'
        
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def generate_industry_attribution(
        self,
        trade_records: List[Dict],
        data_manager,
        save_path: Optional[str] = None
    ) -> str:
        """
        生成行业归因分析
        
        Args:
            trade_records: 交易记录
            data_manager: 数据管理器
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        logger.info("📊 生成行业归因分析...")
        
        # 获取行业分类
        industry_df = data_manager.load_industry_classification()
        if industry_df is None or industry_df.empty:
            logger.warning("无行业分类数据，生成模拟数据")
            # 创建模拟数据
            fig, ax = plt.subplots(figsize=(16, 10))
            ax.text(0.5, 0.5, '行业分类数据未加载\n请确保已下载行业分类信息',
                    ha='center', va='center', fontsize=20)
            ax.axis('off')
        else:
            # 统计各行业的交易
            trades_df = pd.DataFrame(trade_records)
            if not trades_df.empty:
                # 合并行业信息
                trades_df = trades_df.merge(
                    industry_df,
                    left_on='code',
                    right_on='code',
                    how='left'
                )
                
                # 按行业统计
                buy_trades = trades_df[trades_df['action'] == 'buy']
                sell_trades = trades_df[trades_df['action'] == 'sell']
                
                industry_buy = buy_trades.groupby('industry')['amount'].sum().sort_values(ascending=False)
                industry_sell = sell_trades.groupby('industry')['amount'].sum().sort_values(ascending=False)
                industry_count = buy_trades.groupby('industry').size().sort_values(ascending=False)
                
                # 创建图表
                fig, axes = plt.subplots(2, 2, figsize=(18, 12))
                
                # 1. 主动买入行业分布
                ax1 = axes[0, 0]
                top_buy = industry_buy.head(15)
                colors_buy = plt.cm.Greens(np.linspace(0.4, 0.9, len(top_buy)))
                top_buy.plot(kind='barh', ax=ax1, color=colors_buy)
                ax1.set_title('主动买入 - 行业资金分布', fontsize=14)
                ax1.set_xlabel('买入金额 (元)')
                
                # 2. 主动卖出行业分布
                ax2 = axes[0, 1]
                top_sell = industry_sell.head(15)
                colors_sell = plt.cm.Reds(np.linspace(0.4, 0.9, len(top_sell)))
                top_sell.plot(kind='barh', ax=ax2, color=colors_sell)
                ax2.set_title('主动卖出 - 行业资金分布', fontsize=14)
                ax2.set_xlabel('卖出金额 (元)')
                
                # 3. 交易频次行业分布
                ax3 = axes[1, 0]
                top_count = industry_count.head(15)
                colors_count = plt.cm.Blues(np.linspace(0.4, 0.9, len(top_count)))
                top_count.plot(kind='barh', ax=ax3, color=colors_count)
                ax3.set_title('交易频次 - 行业分布', fontsize=14)
                ax3.set_xlabel('交易次数')
                
                # 4. 净买入排名
                ax4 = axes[1, 1]
                industry_net = (industry_buy - industry_sell).sort_values(ascending=False).head(15)
                colors_net = ['green' if x > 0 else 'red' for x in industry_net]
                industry_net.plot(kind='barh', ax=ax4, color=colors_net, alpha=0.7)
                ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
                ax4.set_title('净买入 - 行业资金分布', fontsize=14)
                ax4.set_xlabel('净买入金额 (元)')
                
                plt.suptitle('行业归因分析数据摘要', fontsize=16)
            else:
                fig, ax = plt.subplots(figsize=(16, 10))
                ax.text(0.5, 0.5, '无交易记录', ha='center', va='center', fontsize=20)
                ax.axis('off')
        
        plt.tight_layout()
        
        # 保存
        if save_path is None:
            save_path = self.output_dir / "industry_attribution.png"
        else:
            save_path = Path(save_path)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ 行业归因分析已保存: {save_path}")
        return str(save_path)
    
    def generate_all_charts(
        self,
        results_df: pd.DataFrame,
        trade_records: List[Dict],
        data_manager
    ) -> Dict[str, str]:
        """
        生成所有图表
        
        Args:
            results_df: 回测结果DataFrame
            trade_records: 交易记录
            data_manager: 数据管理器
            
        Returns:
            图表路径字典
        """
        logger.info("\n" + "="*60)
        logger.info("🎨 开始生成所有可视化图表")
        logger.info("="*60 + "\n")
        
        chart_paths = {}
        
        # 1. 月度收益热力图
        chart_paths['monthly_heatmap'] = self.generate_monthly_return_heatmap(results_df)
        
        # 2. 持仓数据趋势图
        chart_paths['position_trend'] = self.generate_position_trend(results_df, trade_records)
        
        # 3. 绩效指标综合仪表盘
        chart_paths['performance_dashboard'] = self.generate_performance_dashboard(results_df)
        
        # 4. 行业归因分析
        chart_paths['industry_attribution'] = self.generate_industry_attribution(
            trade_records, data_manager
        )
        
        logger.info("\n" + "="*60)
        logger.info("✅ 所有图表生成完成！")
        for name, path in chart_paths.items():
            logger.info(f"  {name}: {path}")
        logger.info("="*60 + "\n")
        
        return chart_paths


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建测试数据
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='D')
    test_df = pd.DataFrame({
        'portfolio_value': np.cumsum(np.random.randn(len(dates)) * 10000) + 10000000,
        'cash': 5000000,
        'stock_value': 5000000,
        'num_stocks': np.random.randint(5, 15, len(dates)),
        'market_return': np.random.randn(len(dates)) * 0.5,
        'return': np.cumsum(np.random.randn(len(dates)) * 0.5)
    }, index=dates)
    
    visualizer = BacktestVisualizer()
    visualizer.generate_monthly_return_heatmap(test_df)
    visualizer.generate_position_trend(test_df, [])
    visualizer.generate_performance_dashboard(test_df)
    
    print("测试图表生成完成！")








