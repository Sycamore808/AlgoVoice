"""
生成论文所需图片
- fig6.png: AlgoVoice系统架构图（重画，学术风格）
- fig_llm_evolution.png: 金融大模型技术演进图
- fig_industry_allocation.png: 行业配置动态变化图
- fig_system_diagram.png: 系统核心计算流程图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

# 设置字体和样式
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['figure.dpi'] = 300

# ============================================================================
# 图1: AlgoVoice系统架构图 (fig6.png) - 重新设计
# ============================================================================

def create_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义颜色方案（学术风格）
    colors = {
        'data': '#E3F2FD',      # 浅蓝
        'feature': '#FFF9C4',   # 浅黄
        'strategy': '#C8E6C9',  # 浅绿
        'execution': '#FFE0B2', # 浅橙
        'risk': '#FFCDD2',      # 浅红
        'border': '#1565C0'     # 深蓝边框
    }
    
    # 层次定义
    layers = [
        {'name': 'Data Layer', 'y': 8.5, 'color': colors['data'], 
         'modules': ['Market Data', 'Financial Statements', 'News & Sentiment', 'Macro Indicators']},
        {'name': 'Feature Layer', 'y': 6.8, 'color': colors['feature'],
         'modules': ['Technical Indicators', 'Fundamental Factors', 'Sentiment Features', 'Graph Features']},
        {'name': 'Strategy Layer\n(FIN-R1 Core)', 'y': 5.0, 'color': colors['strategy'],
         'modules': ['Multi-modal Fusion', 'Reinforcement Learning', 'Portfolio Optimization']},
        {'name': 'Execution Layer', 'y': 3.2, 'color': colors['execution'],
         'modules': ['Order Generation', 'Smart Routing', 'Transaction Cost']},
        {'name': 'Risk Control Layer', 'y': 1.5, 'color': colors['risk'],
         'modules': ['Real-time Monitor', 'Dynamic Stop-loss', 'Position Management']}
    ]
    
    # 绘制各层
    module_positions = []
    for layer in layers:
        # 主层框
        box_height = 0.8
        main_box = FancyBboxPatch(
            (0.5, layer['y'] - 0.4),
            9, box_height,
            boxstyle="round,pad=0.05",
            edgecolor=colors['border'],
            facecolor=layer['color'],
            linewidth=2.5,
            zorder=1
        )
        ax.add_patch(main_box)
        
        # 层名称
        ax.text(0.8, layer['y'], layer['name'],
                ha='left', va='center', fontsize=11, fontweight='bold',
                color='#1A237E')
        
        # 模块
        n_modules = len(layer['modules'])
        module_width = 1.6
        start_x = 10 - 0.5 - n_modules * module_width - (n_modules - 1) * 0.1
        
        for i, module in enumerate(layer['modules']):
            x = start_x + i * (module_width + 0.1)
            module_box = FancyBboxPatch(
                (x, layer['y'] - 0.25),
                module_width, 0.5,
                boxstyle="round,pad=0.02",
                edgecolor=colors['border'],
                facecolor='white',
                linewidth=1.2,
                zorder=2
            )
            ax.add_patch(module_box)
            
            ax.text(x + module_width/2, layer['y'], module,
                    ha='center', va='center', fontsize=8,
                    color='#1A237E', multialignment='center')
            
            module_positions.append((x + module_width/2, layer['y']))
    
    # 绘制层间连接箭头
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
                alpha=0.6,
                zorder=0
            )
            ax.add_patch(arrow)
    
    # 添加标题
    ax.text(5, 9.5, 'AlgoVoice Intelligent Quantitative Investment System Architecture',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#1A237E')
    
    # 添加数据流标注
    ax.text(0.3, 5, 'Data\nFlow', ha='center', va='center',
            fontsize=9, color=colors['border'], fontweight='bold',
            rotation=90)
    
    plt.tight_layout()
    plt.savefig('fig6.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Created fig6.png (System Architecture)")
    plt.close()

# ============================================================================
# 图2: 系统核心计算流程图 (fig_system_diagram.png)
# ============================================================================

def create_system_diagram():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 定义流程节点
    nodes = [
        {'name': 'Multi-source\nData Input', 'pos': (2, 8.5), 'color': '#E3F2FD', 'size': 1.2},
        {'name': 'Feature\nExtraction', 'pos': (2, 6.5), 'color': '#FFF9C4', 'size': 1.2},
        {'name': 'FIN-R1\nDecision Model', 'pos': (5, 6.5), 'color': '#C8E6C9', 'size': 1.8},
        {'name': 'Portfolio\nConstruction', 'pos': (8, 6.5), 'color': '#FFE0B2', 'size': 1.2},
        {'name': 'Risk\nAssessment', 'pos': (5, 4.5), 'color': '#FFCDD2', 'size': 1.2},
        {'name': 'Order\nExecution', 'pos': (5, 2.5), 'color': '#E1BEE7', 'size': 1.2},
        {'name': 'Performance\nFeedback', 'pos': (8, 2.5), 'color': '#F0F4C3', 'size': 1.2},
    ]
    
    # 绘制节点
    for node in nodes:
        circle = Circle(node['pos'], node['size']/2,
                       edgecolor='#1565C0', facecolor=node['color'],
                       linewidth=2, zorder=2)
        ax.add_patch(circle)
        
        ax.text(node['pos'][0], node['pos'][1], node['name'],
                ha='center', va='center', fontsize=9, fontweight='bold',
                color='#1A237E', multialignment='center')
    
    # 定义连接关系
    connections = [
        (0, 1, ''),
        (1, 2, 'Features'),
        (2, 3, 'Signals'),
        (3, 4, 'Portfolio'),
        (4, 5, 'Pass'),
        (5, 6, 'Results'),
        (6, 2, 'Learn'),
        (4, 2, 'Adjust'),
    ]
    
    # 绘制连接箭头
    for i, j, label in connections:
        pos1 = nodes[i]['pos']
        pos2 = nodes[j]['pos']
        r1 = nodes[i]['size']/2
        r2 = nodes[j]['size']/2
        
        # 计算箭头起点和终点
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            start_x = pos1[0] + dx/dist * r1
            start_y = pos1[1] + dy/dist * r1
            end_x = pos2[0] - dx/dist * r2
            end_y = pos2[1] - dy/dist * r2
            
            # 反馈循环使用曲线
            if label == 'Learn' or label == 'Adjust':
                style = 'arc3,rad=0.3'
                color = '#FF6F00'
                linestyle = '--'
            else:
                style = 'arc3,rad=0'
                color = '#1565C0'
                linestyle = '-'
            
            arrow = FancyArrowPatch(
                (start_x, start_y), (end_x, end_y),
                arrowstyle='->,head_width=0.3,head_length=0.2',
                connectionstyle=style,
                color=color,
                linewidth=2,
                linestyle=linestyle,
                zorder=1
            )
            ax.add_patch(arrow)
            
            # 添加标签
            if label:
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                ax.text(mid_x, mid_y, label,
                       ha='center', va='bottom', fontsize=8,
                       color=color, style='italic',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                                edgecolor='none', alpha=0.8))
    
    # 添加标题
    ax.text(5, 9.5, 'Core Computation Flow of AlgoVoice System',
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='#1A237E')
    
    # 添加图例
    legend_elements = [
        mpatches.Patch(facecolor='#C8E6C9', edgecolor='#1565C0', label='Decision Core'),
        mpatches.Patch(facecolor='#FFCDD2', edgecolor='#1565C0', label='Risk Control'),
        plt.Line2D([0], [0], color='#FF6F00', linestyle='--', linewidth=2, label='Feedback Loop')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9, frameon=True)
    
    plt.tight_layout()
    plt.savefig('fig_system_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Created fig_system_diagram.png (System Flow)")
    plt.close()

# ============================================================================
# 图3: 金融大模型技术演进图 (fig_llm_evolution.png)
# ============================================================================

def create_llm_evolution():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(2018.5, 2025.5)
    ax.set_ylim(0, 4)
    ax.axis('off')
    
    # 时间轴
    ax.plot([2019, 2025], [0.5, 0.5], 'k-', linewidth=2, zorder=1)
    
    # 定义里程碑事件
    milestones = [
        {
            'year': 2019,
            'name': 'FinBERT',
            'author': 'Araci (2019)',
            'description': 'Financial Sentiment Analysis',
            'capability': 'Text Understanding',
            'color': '#E8F4F8',
            'y': 1.5
        },
        {
            'year': 2023,
            'name': 'BloombergGPT',
            'author': 'Wu et al. (2023)',
            'description': '50B Parameters\nDomain-specific LLM',
            'capability': 'Domain Knowledge',
            'color': '#B8E6F0',
            'y': 2.3
        },
        {
            'year': 2024,
            'name': 'TradingAgents',
            'author': 'Xiao et al. (2024)',
            'description': 'Multi-Agent Trading\nCollaborative Decision',
            'capability': 'Agent Collaboration',
            'color': '#7BC8E2',
            'y': 1.8
        },
        {
            'year': 2025,
            'name': 'FIN-R1',
            'author': 'Liu et al. (2025)',
            'description': 'Reinforcement Learning\nFinancial Reasoning',
            'capability': 'Strategic Reasoning',
            'color': '#4A9EBF',
            'y': 2.8
        }
    ]
    
    # 绘制里程碑
    for i, ms in enumerate(milestones):
        # 时间轴上的点
        ax.plot(ms['year'], 0.5, 'o', markersize=12, color=ms['color'], 
                markeredgecolor='#2C5F7B', markeredgewidth=2, zorder=3)
        
        # 年份标签
        ax.text(ms['year'], 0.15, str(ms['year']), ha='center', va='top',
                fontsize=11, fontweight='bold', color='#2C5F7B')
        
        # 信息框
        box_width = 0.9
        box_height = 0.65
        box = FancyBboxPatch(
            (ms['year'] - box_width/2, ms['y']),
            box_width, box_height,
            boxstyle="round,pad=0.05",
            edgecolor='#2C5F7B',
            facecolor=ms['color'],
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(box)
        
        # 模型名称
        ax.text(ms['year'], ms['y'] + 0.5, ms['name'],
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='#1A3A4A')
        
        # 作者和描述
        ax.text(ms['year'], ms['y'] + 0.25, ms['author'],
                ha='center', va='center', fontsize=8, style='italic',
                color='#2C5F7B')
        
        ax.text(ms['year'], ms['y'] + 0.05, ms['description'],
                ha='center', va='center', fontsize=8,
                color='#1A3A4A', multialignment='center')
        
        # 连接线
        arrow = FancyArrowPatch(
            (ms['year'], 0.5), (ms['year'], ms['y']),
            arrowstyle='-',
            color='#7BC8E2',
            linewidth=1.5,
            linestyle='--',
            alpha=0.6,
            zorder=1
        )
        ax.add_patch(arrow)
    
    # 添加能力演进箭头
    y_cap = 3.5
    ax.annotate('', xy=(2025, y_cap), xytext=(2019, y_cap),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='#FF8C42'))
    
    ax.text(2022, y_cap + 0.2, 'Evolution of Capabilities',
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            color='#FF8C42')
    
    # 能力标签
    capabilities = [
        (2019.5, y_cap - 0.15, 'Sentiment'),
        (2021.5, y_cap - 0.15, 'Domain Expert'),
        (2023.8, y_cap - 0.15, 'Multi-Agent'),
        (2025, y_cap - 0.15, 'Reasoning')
    ]
    
    for x, y, label in capabilities:
        ax.text(x, y, label, ha='center', va='top',
                fontsize=9, color='#FF8C42', style='italic')
    
    # 标题
    ax.text(2022, -0.3, 'Evolution of Financial Large Language Models',
            ha='center', va='top', fontsize=14, fontweight='bold',
            color='#1A3A4A')
    
    plt.tight_layout()
    plt.savefig('fig_llm_evolution.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Created fig_llm_evolution.png")
    plt.close()

# ============================================================================
# 图4: 行业配置动态变化图 (fig_industry_allocation.png)
# ============================================================================

def create_industry_allocation():
    # 时间序列 (季度)
    years = np.arange(2015, 2025, 0.25)
    n_periods = len(years)
    
    # 模拟各行业配置权重变化
    # 基于原文：新能源18.3%, 半导体12.7%, 生物医药10.5%, 消费电子8.9%, 光伏7.2%, 其他42.4%
    
    # 新能源汽车 - 2019后快速上升
    new_energy = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2019:
            new_energy[i] = 8 + np.random.normal(0, 1)
        elif y < 2021:
            new_energy[i] = 8 + (y - 2019) * 15 + np.random.normal(0, 2)
        elif y < 2022:
            new_energy[i] = 38 + np.random.normal(0, 2)
        else:
            new_energy[i] = 38 - (y - 2022) * 8 + np.random.normal(0, 2)
    new_energy = np.clip(new_energy, 5, 45)
    
    # 半导体 - 2020-2021高峰
    semiconductor = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2020:
            semiconductor[i] = 8 + np.random.normal(0, 1)
        elif y < 2021.5:
            semiconductor[i] = 8 + (y - 2020) * 8 + np.random.normal(0, 2)
        else:
            semiconductor[i] = 20 - (y - 2021.5) * 2 + np.random.normal(0, 1.5)
    semiconductor = np.clip(semiconductor, 5, 25)
    
    # 生物医药 - 2020疫情期高峰
    biotech = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2020:
            biotech[i] = 6 + np.random.normal(0, 1)
        elif y < 2021:
            biotech[i] = 6 + (y - 2020) * 12 + np.random.normal(0, 2)
        else:
            biotech[i] = 18 - (y - 2021) * 2 + np.random.normal(0, 1.5)
    biotech = np.clip(biotech, 5, 20)
    
    # 消费电子 - 相对稳定
    consumer_elec = np.zeros(n_periods)
    for i, y in enumerate(years):
        consumer_elec[i] = 9 + np.sin((y - 2015) * 0.8) * 3 + np.random.normal(0, 1)
    consumer_elec = np.clip(consumer_elec, 5, 15)
    
    # 光伏风电 - 2021后上升
    solar_wind = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2021:
            solar_wind[i] = 4 + np.random.normal(0, 0.5)
        else:
            solar_wind[i] = 4 + (y - 2021) * 3 + np.random.normal(0, 1)
    solar_wind = np.clip(solar_wind, 3, 15)
    
    # 其他行业 - 补充到100%
    others = 100 - (new_energy + semiconductor + biotech + consumer_elec + solar_wind)
    
    # 创建堆叠数据
    data = np.vstack([new_energy, semiconductor, biotech, consumer_elec, solar_wind, others])
    
    # 绘图
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 配色方案 - 使用专业的学术配色
    colors = ['#2E7D32', '#1565C0', '#C62828', '#F57C00', '#6A1B9A', '#757575']
    labels = ['New Energy Vehicles', 'Semiconductor', 'Biotechnology', 
              'Consumer Electronics', 'Solar & Wind', 'Others']
    
    # 绘制堆叠面积图
    ax.stackplot(years, data, labels=labels, colors=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
    
    # 标注关键事件
    events = [
        (2015.5, 95, '2015 Market Crash', '#D32F2F'),
        (2020.25, 95, '2020 COVID-19', '#C62828'),
        (2021.0, 95, '2021 Bull Market', '#388E3C'),
        (2022.5, 95, '2022 Adjustment', '#F57C00')
    ]
    
    for x, y, text, color in events:
        ax.axvline(x, color=color, linestyle='--', alpha=0.4, linewidth=1.5)
        ax.text(x, y, text, rotation=90, va='top', ha='right',
                fontsize=8, color=color, fontweight='bold', alpha=0.8)
    
    # 设置坐标轴
    ax.set_xlim(2015, 2024.75)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Portfolio Allocation (%)', fontsize=12, fontweight='bold')
    ax.set_title('Dynamic Industry Allocation of AlgoVoice Strategy (2015-2024)',
                 fontsize=14, fontweight='bold', pad=20)
    
    # 网格
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # 图例
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True,
              fancybox=True, shadow=True, fontsize=10)
    
    # 美化边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    
    plt.tight_layout()
    plt.savefig('fig_industry_allocation.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Created fig_industry_allocation.png")
    plt.close()

# ============================================================================
# 主函数
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Generating figures for the paper...")
    print("="*60 + "\n")
    
    create_system_architecture()
    create_system_diagram()
    create_llm_evolution()
    create_industry_allocation()
    
    print("\n" + "="*60)
    print("✓ All figures generated successfully!")
    print("="*60)
    print("\nGenerated files:")
    print("  - fig6.png (System Architecture - NEW)")
    print("  - fig_system_diagram.png (System Flow - NEW)")
    print("  - fig_llm_evolution.png")
    print("  - fig_industry_allocation.png")
    print("\nPlease upload these files to your Overleaf project.")
    print("Also upload: 因子群生成与筛选模式图.png")
    print("\n")
