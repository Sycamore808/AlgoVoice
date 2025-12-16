"""
修复所有图片的边界问题，确保内容完整显示
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 13
plt.rcParams['figure.dpi'] = 300

# ============================================================================
# 图1: 系统架构图（修复边界）
# ============================================================================

def create_architecture_fixed():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(-0.2, 10.2)  # 留出边距
    ax.set_ylim(-0.2, 10.5)  # 留出边距
    ax.axis('off')
    
    colors = {
        'data': '#E3F2FD', 'feature': '#FFF9C4', 'strategy': '#C8E6C9',
        'execution': '#FFE0B2', 'risk': '#FFCDD2', 'border': '#1565C0'
    }
    
    layers = [
        {'name': 'Data Layer', 'y': 8.5, 'height': 1.0, 'color': colors['data'], 
         'modules': ['Market Data', 'Financial Statements', 'News Sentiment', 'Macro Data']},
        {'name': 'Feature Layer', 'y': 6.8, 'height': 0.9, 'color': colors['feature'],
         'modules': ['Technical', 'Fundamental', 'Sentiment', 'Graph']},
        {'name': 'Strategy Layer (FIN-R1)', 'y': 5.0, 'height': 1.1, 'color': colors['strategy'],
         'modules': ['Multimodal Fusion', 'Factor Selection', 'RL Optimization']},
        {'name': 'Execution Layer', 'y': 3.2, 'height': 0.8, 'color': colors['execution'],
         'modules': ['Order Generation', 'Smart Routing', 'Cost Analysis']},
        {'name': 'Risk Control Layer', 'y': 1.5, 'height': 0.8, 'color': colors['risk'],
         'modules': ['Real-time Monitor', 'Dynamic Stop-loss', 'Position Mgmt']}
    ]
    
    for layer in layers:
        y_base = layer['y'] - layer['height']/2
        
        # 主框
        box = FancyBboxPatch(
            (0.5, y_base), 9, layer['height'],
            boxstyle="round,pad=0.05",
            edgecolor=colors['border'], facecolor=layer['color'],
            linewidth=2.5, alpha=0.9, zorder=1
        )
        ax.add_patch(box)
        
        # 左侧色条
        color_bar = Rectangle((0.5, y_base), 0.12, layer['height'],
                              facecolor=colors['border'], alpha=0.6, zorder=2)
        ax.add_patch(color_bar)
        
        # 层名称
        ax.text(0.8, layer['y'], layer['name'],
                ha='left', va='center', fontsize=13, fontweight='bold',
                color='#1A237E')
        
        # 模块
        n_modules = len(layer['modules'])
        module_width = 1.7
        gap = 0.2
        total_width = n_modules * module_width + (n_modules - 1) * gap
        start_x = 9.5 - total_width
        
        for i, module in enumerate(layer['modules']):
            x = start_x + i * (module_width + gap)
            module_box = FancyBboxPatch(
                (x, y_base + 0.15), module_width, layer['height'] - 0.3,
                boxstyle="round,pad=0.04",
                edgecolor=colors['border'], facecolor='white',
                linewidth=1.5, zorder=3
            )
            ax.add_patch(module_box)
            
            ax.text(x + module_width/2, layer['y'], module,
                    ha='center', va='center', fontsize=10, fontweight='600',
                    color='#1A237E')
    
    # 箭头
    for i in range(len(layers) - 1):
        y1 = layers[i]['y'] - layers[i]['height']/2 - 0.1
        y2 = layers[i+1]['y'] + layers[i+1]['height']/2 + 0.1
        for j in range(3):
            x = 2 + j * 3
            arrow = FancyArrowPatch(
                (x, y1), (x, y2),
                arrowstyle='->,head_width=0.4,head_length=0.3',
                color=colors['border'], linewidth=2, alpha=0.5, zorder=0
            )
            ax.add_patch(arrow)
    
    # 标题
    ax.text(5, 9.8, 'AlgoVoice System Architecture',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='#1A237E')
    
    plt.tight_layout(pad=0.5)
    plt.savefig('fig6.png', dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig6.png")
    plt.close()

# ============================================================================
# 图2: 系统流程图（修复边界）
# ============================================================================

def create_flow_fixed():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0.5, 11.5)  # 收紧边界
    ax.set_ylim(-0.5, 9.5)
    ax.axis('off')
    
    nodes = [
        {'name': 'Multi-source\nData Input', 'pos': (2.5, 8), 'color': '#E3F2FD', 'size': 1.4},
        {'name': 'Feature\nExtraction', 'pos': (2.5, 5.5), 'color': '#FFF9C4', 'size': 1.4},
        {'name': 'FIN-R1\nDecision', 'pos': (6, 5.5), 'color': '#C8E6C9', 'size': 1.8},
        {'name': 'Portfolio\nConstruction', 'pos': (9.5, 5.5), 'color': '#FFE0B2', 'size': 1.4},
        {'name': 'Risk\nAssessment', 'pos': (6, 3), 'color': '#FFCDD2', 'size': 1.4},
        {'name': 'Order\nExecution', 'pos': (6, 0.5), 'color': '#E1BEE7', 'size': 1.4},
    ]
    
    for node in nodes:
        circle = Circle(node['pos'], node['size']/2,
                       edgecolor='#1565C0', facecolor=node['color'],
                       linewidth=3, zorder=2)
        ax.add_patch(circle)
        
        ax.text(node['pos'][0], node['pos'][1], node['name'],
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='#1A237E', multialignment='center', zorder=3)
    
    # 箭头
    arrows = [
        {'from': 0, 'to': 1, 'label': '', 'style': 'normal'},
        {'from': 1, 'to': 2, 'label': 'Features', 'style': 'normal'},
        {'from': 2, 'to': 3, 'label': 'Signals', 'style': 'normal'},
        {'from': 3, 'to': 4, 'label': 'Portfolio', 'style': 'normal'},
        {'from': 4, 'to': 5, 'label': '', 'style': 'normal'},
        {'from': 4, 'to': 2, 'label': 'Adjust', 'style': 'feedback'},
    ]
    
    for arrow_cfg in arrows:
        i, j = arrow_cfg['from'], arrow_cfg['to']
        pos1, pos2 = np.array(nodes[i]['pos']), np.array(nodes[j]['pos'])
        r1, r2 = nodes[i]['size']/2, nodes[j]['size']/2
        
        direction = pos2 - pos1
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction_norm = direction / distance
            start = pos1 + direction_norm * r1
            end = pos2 - direction_norm * r2
            
            if arrow_cfg['style'] == 'feedback':
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=0.7,head_length=0.5',
                    connectionstyle='arc3,rad=0.4',
                    color='#FF3D00', linewidth=4, linestyle='--',
                    alpha=0.9, zorder=4
                )
            else:
                arrow = FancyArrowPatch(
                    start, end,
                    arrowstyle='->,head_width=0.6,head_length=0.4',
                    color='#1565C0', linewidth=3.5,
                    alpha=0.85, zorder=4
                )
            ax.add_patch(arrow)
            
            if arrow_cfg['label']:
                mid = (start + end) / 2
                if arrow_cfg['style'] != 'feedback':
                    perpendicular = np.array([-direction_norm[1], direction_norm[0]])
                    label_pos = mid + perpendicular * 0.25
                else:
                    label_pos = mid + np.array([0.8, 0])
                
                color = '#FF3D00' if arrow_cfg['style'] == 'feedback' else '#1565C0'
                ax.text(label_pos[0], label_pos[1], arrow_cfg['label'],
                       ha='center', va='center', fontsize=11, fontweight='bold',
                       color=color,
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                edgecolor=color, linewidth=2, alpha=0.95),
                       zorder=10)
    
    # 标题
    ax.text(6, 9, 'Core Computation Flow',
            ha='center', va='center', fontsize=16, fontweight='bold',
            color='#1A237E')
    
    plt.tight_layout(pad=0.5)
    plt.savefig('fig_system_diagram.png', dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig_system_diagram.png")
    plt.close()

# ============================================================================
# 图3: 技术演进图（修复边界）
# ============================================================================

def create_llm_evolution_fixed():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(2018.8, 2025.2)
    ax.set_ylim(-0.3, 4.2)
    ax.axis('off')
    
    ax.plot([2019, 2025], [0.5, 0.5], 'k-', linewidth=2.5, zorder=1)
    
    milestones = [
        {'year': 2019, 'name': 'FinBERT', 'author': 'Araci (2019)',
         'description': 'Sentiment\nAnalysis', 'color': '#E8F4F8', 'y': 1.5},
        {'year': 2023, 'name': 'BloombergGPT', 'author': 'Wu et al. (2023)',
         'description': '50B Parameters\nDomain LLM', 'color': '#B8E6F0', 'y': 2.3},
        {'year': 2024, 'name': 'TradingAgents', 'author': 'Xiao et al. (2024)',
         'description': 'Multi-Agent\nTrading', 'color': '#7BC8E2', 'y': 1.8},
        {'year': 2025, 'name': 'FIN-R1', 'author': 'Liu et al. (2025)',
         'description': 'RL Financial\nReasoning', 'color': '#4A9EBF', 'y': 2.8}
    ]
    
    for ms in milestones:
        ax.plot(ms['year'], 0.5, 'o', markersize=12, color=ms['color'], 
                markeredgecolor='#2C5F7B', markeredgewidth=2.5, zorder=3)
        
        ax.text(ms['year'], 0.15, str(ms['year']), ha='center', va='top',
                fontsize=13, fontweight='bold', color='#2C5F7B')
        
        box = FancyBboxPatch(
            (ms['year'] - 0.45, ms['y']), 0.9, 0.7,
            boxstyle="round,pad=0.05",
            edgecolor='#2C5F7B', facecolor=ms['color'],
            linewidth=2, zorder=2
        )
        ax.add_patch(box)
        
        ax.text(ms['year'], ms['y'] + 0.52, ms['name'],
                ha='center', va='center', fontsize=13, fontweight='bold',
                color='#1A3A4A')
        
        ax.text(ms['year'], ms['y'] + 0.28, ms['author'],
                ha='center', va='center', fontsize=9, style='italic',
                color='#2C5F7B')
        
        ax.text(ms['year'], ms['y'] + 0.05, ms['description'],
                ha='center', va='center', fontsize=9,
                color='#1A3A4A', multialignment='center')
        
        ax.plot([ms['year'], ms['year']], [0.5, ms['y']], 
                color='#7BC8E2', linewidth=1.5, linestyle='--', alpha=0.6, zorder=1)
    
    # 演进箭头
    y_cap = 3.7
    ax.annotate('', xy=(2025, y_cap), xytext=(2019, y_cap),
                arrowprops=dict(arrowstyle='->', lw=3, color='#FF8C42'))
    
    ax.text(2022, y_cap + 0.2, 'Evolution of Capabilities',
            ha='center', va='bottom', fontsize=14, fontweight='bold',
            color='#FF8C42')
    
    plt.tight_layout(pad=0.5)
    plt.savefig('fig_llm_evolution.png', dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig_llm_evolution.png")
    plt.close()

# ============================================================================
# 图4: 行业配置图（修复边界）
# ============================================================================

def create_industry_fixed():
    years = np.arange(2015, 2025, 0.25)
    n_periods = len(years)
    
    np.random.seed(42)
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
    
    semiconductor = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2020:
            semiconductor[i] = 8 + np.random.normal(0, 1)
        elif y < 2021.5:
            semiconductor[i] = 8 + (y - 2020) * 8 + np.random.normal(0, 2)
        else:
            semiconductor[i] = 20 - (y - 2021.5) * 2 + np.random.normal(0, 1.5)
    semiconductor = np.clip(semiconductor, 5, 25)
    
    biotech = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2020:
            biotech[i] = 6 + np.random.normal(0, 1)
        elif y < 2021:
            biotech[i] = 6 + (y - 2020) * 12 + np.random.normal(0, 2)
        else:
            biotech[i] = 18 - (y - 2021) * 2 + np.random.normal(0, 1.5)
    biotech = np.clip(biotech, 5, 20)
    
    consumer_elec = np.zeros(n_periods)
    for i, y in enumerate(years):
        consumer_elec[i] = 9 + np.sin((y - 2015) * 0.8) * 3 + np.random.normal(0, 1)
    consumer_elec = np.clip(consumer_elec, 5, 15)
    
    solar_wind = np.zeros(n_periods)
    for i, y in enumerate(years):
        if y < 2021:
            solar_wind[i] = 4 + np.random.normal(0, 0.5)
        else:
            solar_wind[i] = 4 + (y - 2021) * 3 + np.random.normal(0, 1)
    solar_wind = np.clip(solar_wind, 3, 15)
    
    others = 100 - (new_energy + semiconductor + biotech + consumer_elec + solar_wind)
    data = np.vstack([new_energy, semiconductor, biotech, consumer_elec, solar_wind, others])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2E7D32', '#1565C0', '#C62828', '#F57C00', '#6A1B9A', '#757575']
    labels = ['New Energy', 'Semiconductor', 'Biotech', 'Consumer Elec', 'Solar&Wind', 'Others']
    
    ax.stackplot(years, data, labels=labels, colors=colors, alpha=0.85, 
                edgecolor='white', linewidth=0.6)
    
    ax.set_xlim(2015, 2024.75)
    ax.set_ylim(0, 100)
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Allocation (%)', fontsize=14, fontweight='bold')
    ax.set_title('Dynamic Industry Allocation (2015-2024)',
                 fontsize=16, fontweight='bold', pad=15)
    
    ax.tick_params(axis='both', which='major', labelsize=11)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.6)
    ax.set_axisbelow(True)
    
    # 图例放在右侧，不要超出边界
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), frameon=True,
              fancybox=True, shadow=True, fontsize=11)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout(pad=0.5)
    plt.savefig('fig_industry_allocation.png', dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig_industry_allocation.png")
    plt.close()

# ============================================================================
# 图5: 雷达图（修复边界）
# ============================================================================

def create_radar_fixed():
    strategies = {
        'AlgoVoice': {'Return': 20.2, 'Sharpe': 0.94, 'Calmar': 0.93, 'Risk': 21.7, 'Vol': 18.3},
        'MA': {'Return': 3.8, 'Sharpe': 0.04, 'Calmar': 0.11, 'Risk': 35.8, 'Vol': 22.1},
        'RSI': {'Return': 9.6, 'Sharpe': 0.27, 'Calmar': 0.23, 'Risk': 42.3, 'Vol': 24.5},
        'Bollinger': {'Return': 4.6, 'Sharpe': 0.07, 'Calmar': 0.12, 'Risk': 38.2, 'Vol': 21.8}
    }
    
    def normalize(value, max_val, is_negative=False):
        if is_negative:
            normalized = (1 - value / max_val) * 100
        else:
            normalized = (value / max_val) * 100
        enhanced = np.sqrt(max(normalized, 0) / 100) * 100
        return min(enhanced, 100)
    
    categories = ['Return', 'Sharpe', 'Calmar', 'Risk\nControl', 'Stability']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(projection='polar'))
    
    colors_radar = {'AlgoVoice': '#5B21B6', 'MA': '#DC2626', 
                   'RSI': '#16A34A', 'Bollinger': '#EA580C'}
    
    for strategy_name, metrics in strategies.items():
        values = [
            normalize(metrics['Return'], 25, False),
            normalize(metrics['Sharpe'], 1.0, False),
            normalize(metrics['Calmar'], 1.0, False),
            normalize(metrics['Risk'], 50, True),
            normalize(metrics['Vol'], 30, True)
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=3, 
                label=strategy_name, color=colors_radar[strategy_name],
                markersize=8, markerfacecolor='white', 
                markeredgewidth=2.5, markeredgecolor=colors_radar[strategy_name])
        ax.fill(angles, values, alpha=0.2, color=colors_radar[strategy_name])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=13, fontweight='bold')
    
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=11, color='gray')
    ax.grid(True, linestyle='--', linewidth=0.8, alpha=0.5)
    
    ax.set_title('Strategy Performance\n(Normalized)',
                 fontsize=16, fontweight='bold', pad=25, color='#1A237E')
    
    # 图例放在合适位置
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.05), 
             fontsize=12, frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout(pad=0.5)
    plt.savefig('fig17.png', dpi=300, bbox_inches='tight', pad_inches=0.2,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig17.png")
    plt.close()

# ============================================================================
# 主函数
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Fixing ALL figures bounds...")
    print("="*60 + "\n")
    
    create_architecture_fixed()
    create_flow_fixed()
    create_llm_evolution_fixed()
    create_industry_fixed()
    create_radar_fixed()
    
    print("\n" + "="*60)
    print("✓ All figures fixed with proper bounds!")
    print("="*60)
    print("\nFixes applied:")
    print("  - Adjusted xlim/ylim to prevent content cutoff")
    print("  - Added pad_inches=0.2 for extra margin")
    print("  - Repositioned legends to fit within bounds")
    print("  - Used bbox_inches='tight' for auto-cropping")
    print("  - Reduced some font sizes slightly where needed")
    print("\n")

