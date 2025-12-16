"""
使用真实数据重新生成：
- fig6: 清爽简洁的系统架构图
- fig17: 真实数据的雷达图（调整归一化方式增强区分度）
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

# ============================================================================
# 图1: 清爽简洁的系统架构图 (fig6.png)
# ============================================================================

def create_clean_architecture():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 简洁配色
    colors = {
        'data': '#E3F2FD',
        'feature': '#FFF9C4',
        'strategy': '#C8E6C9',
        'execution': '#FFE0B2',
        'risk': '#FFCDD2',
        'border': '#1565C0'
    }
    
    # 层次定义
    layers = [
        {'name': 'Data Layer', 'y': 8.5, 'color': colors['data'], 
         'modules': ['Market Data', 'Financial Statements', 'News Sentiment', 'Macro Data']},
        {'name': 'Feature Layer', 'y': 6.8, 'color': colors['feature'],
         'modules': ['Technical', 'Fundamental', 'Sentiment', 'Graph']},
        {'name': 'Strategy Layer (FIN-R1)', 'y': 5.0, 'color': colors['strategy'],
         'modules': ['Multimodal Fusion', 'Factor Selection', 'RL Optimization']},
        {'name': 'Execution Layer', 'y': 3.2, 'color': colors['execution'],
         'modules': ['Order Generation', 'Smart Routing', 'Cost Analysis']},
        {'name': 'Risk Control Layer', 'y': 1.5, 'color': colors['risk'],
         'modules': ['Real-time Monitor', 'Dynamic Stop-loss', 'Position Mgmt']}
    ]
    
    # 绘制各层
    for layer in layers:
        # 主层框
        box = FancyBboxPatch(
            (0.5, layer['y'] - 0.4),
            9, 0.8,
            boxstyle="round,pad=0.05",
            edgecolor=colors['border'],
            facecolor=layer['color'],
            linewidth=2,
            zorder=1
        )
        ax.add_patch(box)
        
        # 层名称
        ax.text(0.8, layer['y'], layer['name'],
                ha='left', va='center', fontsize=11, fontweight='bold',
                color='#1A237E')
        
        # 模块
        n_modules = len(layer['modules'])
        module_width = 1.5
        start_x = 10 - 0.5 - n_modules * module_width - (n_modules - 1) * 0.15
        
        for i, module in enumerate(layer['modules']):
            x = start_x + i * (module_width + 0.15)
            module_box = FancyBboxPatch(
                (x, layer['y'] - 0.25),
                module_width, 0.5,
                boxstyle="round,pad=0.03",
                edgecolor=colors['border'],
                facecolor='white',
                linewidth=1.2,
                zorder=2
            )
            ax.add_patch(module_box)
            
            ax.text(x + module_width/2, layer['y'], module,
                    ha='center', va='center', fontsize=8,
                    color='#1A237E')
    
    # 简洁的层间箭头
    for i in range(len(layers) - 1):
        y1 = layers[i]['y'] - 0.5
        y2 = layers[i+1]['y'] + 0.5
        
        for j in range(3):
            x = 2 + j * 3
            arrow = FancyArrowPatch(
                (x, y1), (x, y2),
                arrowstyle='->,head_width=0.3,head_length=0.2',
                color=colors['border'],
                linewidth=1.5,
                alpha=0.5,
                zorder=0
            )
            ax.add_patch(arrow)
    
    # 标题
    ax.text(5, 9.5, 'AlgoVoice System Architecture',
            ha='center', va='center', fontsize=14, fontweight='bold',
            color='#1A237E')
    
    plt.tight_layout()
    plt.savefig('fig6.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Created clean fig6.png")
    plt.close()

# ============================================================================
# 图2: 基于真实数据的雷达图 (fig17.png)
# ============================================================================

def create_radar_with_real_data():
    # 使用真实数据（从表格）
    strategies = {
        'AlgoVoice': {
            'Annual Return': 20.2,
            'Sharpe Ratio': 0.94,
            'Calmar Ratio': 0.93,
            'Risk Control': 21.7,  # 最大回撤（取绝对值）
            'Volatility': 18.3
        },
        'MA': {
            'Annual Return': 3.8,
            'Sharpe Ratio': 0.04,
            'Calmar Ratio': 0.11,
            'Risk Control': 35.8,
            'Volatility': 22.1
        },
        'RSI': {
            'Annual Return': 9.6,
            'Sharpe Ratio': 0.27,
            'Calmar Ratio': 0.23,
            'Risk Control': 42.3,
            'Volatility': 24.5
        },
        'Bollinger': {
            'Annual Return': 4.6,
            'Sharpe Ratio': 0.07,
            'Calmar Ratio': 0.12,
            'Risk Control': 38.2,
            'Volatility': 21.8
        }
    }
    
    # 归一化函数（增强区分度）
    def normalize_with_contrast(value, max_val, is_negative=False):
        """
        归一化到0-100，并增强区分度
        is_negative: 如果True，值越小越好（如回撤、波动率）
        """
        if is_negative:
            # 对于"越小越好"的指标，反向归一化
            normalized = (1 - value / max_val) * 100
        else:
            # 对于"越大越好"的指标
            normalized = (value / max_val) * 100
        
        # 应用对比度增强（平方根变换，让差异更明显）
        if normalized > 0:
            enhanced = np.sqrt(normalized / 100) * 100
        else:
            enhanced = 0
        
        return min(enhanced, 100)
    
    # 维度和最大值
    categories = ['Annual Return\n(%)', 'Sharpe\nRatio', 'Calmar\nRatio', 
                  'Risk Control\n(Lower DD)', 'Stability\n(Lower Vol)']
    N = len(categories)
    
    # 计算角度
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 配色
    colors_radar = {
        'AlgoVoice': '#5B21B6',
        'MA': '#DC2626',
        'RSI': '#16A34A',
        'Bollinger': '#EA580C'
    }
    
    # 绘制每个策略
    for strategy_name, metrics in strategies.items():
        values = [
            normalize_with_contrast(metrics['Annual Return'], 25, False),
            normalize_with_contrast(metrics['Sharpe Ratio'], 1.0, False),
            normalize_with_contrast(metrics['Calmar Ratio'], 1.0, False),
            normalize_with_contrast(metrics['Risk Control'], 50, True),  # 回撤越小越好
            normalize_with_contrast(metrics['Volatility'], 30, True)     # 波动越小越好
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2.5, 
                label=strategy_name, color=colors_radar[strategy_name],
                markersize=7, markerfacecolor='white', 
                markeredgewidth=2.5, markeredgecolor=colors_radar[strategy_name])
        ax.fill(angles, values, alpha=0.2, color=colors_radar[strategy_name])
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    
    # 设置Y轴
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, color='gray')
    ax.grid(True, linestyle='--', linewidth=0.8, alpha=0.5, color='gray')
    
    # 标题
    ax.set_title('Strategy Performance Radar Chart\n(Normalized Real Data)',
                 fontsize=14, fontweight='bold', pad=30, color='#1A237E')
    
    # 图例
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), 
             fontsize=11, frameon=True, fancybox=True, shadow=True)
    
    # 添加说明
    fig.text(0.5, 0.02, 'Note: All metrics normalized to 0-100 scale with contrast enhancement\n' +
             'Risk Control & Stability: Higher values = Lower drawdown/volatility (better performance)',
             ha='center', fontsize=8, style='italic', color='gray')
    
    plt.tight_layout()
    plt.savefig('fig17.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print("✓ Created fig17.png with real data")
    plt.close()
    
    # 打印真实数据供参考
    print("\n真实数据：")
    for name, metrics in strategies.items():
        print(f"\n{name}:")
        print(f"  年化收益: {metrics['Annual Return']:.1f}%")
        print(f"  夏普比率: {metrics['Sharpe Ratio']:.2f}")
        print(f"  Calmar比率: {metrics['Calmar Ratio']:.2f}")
        print(f"  最大回撤: {metrics['Risk Control']:.1f}%")
        print(f"  年化波动: {metrics['Volatility']:.1f}%")

# ============================================================================
# 主函数
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Regenerating figures with real data...")
    print("="*60 + "\n")
    
    create_clean_architecture()
    create_radar_with_real_data()
    
    print("\n" + "="*60)
    print("✓ Figures regenerated successfully!")
    print("="*60 + "\n")

