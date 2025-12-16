"""
修复fig6：
1. 确保箭头头部完整显示
2. 添加左侧数据流指示箭头
3. 所有元素在边界内
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 13
plt.rcParams['figure.dpi'] = 300

def create_fixed_architecture():
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(-0.5, 10.5)  # 扩大边界确保箭头完整
    ax.set_ylim(-0.3, 10.3)
    ax.axis('off')
    
    colors = {
        'data': '#E3F2FD', 'feature': '#FFF9C4', 'strategy': '#C8E6C9',
        'execution': '#FFE0B2', 'risk': '#FFCDD2', 'border': '#1565C0'
    }
    
    layers = [
        {'name': 'Data Layer', 'y': 8.5, 'height': 0.95, 'color': colors['data'], 
         'modules': ['Market Data', 'Financial\nStatements', 'News &\nSentiment', 'Macro\nIndicators']},
        {'name': 'Feature Layer', 'y': 6.8, 'height': 0.9, 'color': colors['feature'],
         'modules': ['Technical', 'Fundamental', 'Sentiment', 'Graph']},
        {'name': 'Strategy Layer (FIN-R1)', 'y': 5.0, 'height': 1.05, 'color': colors['strategy'],
         'modules': ['Multimodal\nFusion', 'Factor\nSelection', 'RL Optim']},
        {'name': 'Execution Layer', 'y': 3.2, 'height': 0.8, 'color': colors['execution'],
         'modules': ['Order\nGeneration', 'Smart\nRouting', 'Cost\nAnalysis']},
        {'name': 'Risk Control Layer', 'y': 1.5, 'height': 0.8, 'color': colors['risk'],
         'modules': ['Real-time\nMonitor', 'Dynamic\nStop-loss', 'Position\nMgmt']}
    ]
    
    # 绘制各层
    for layer in layers:
        y_base = layer['y'] - layer['height']/2
        
        # 主框
        box = FancyBboxPatch(
            (0.5, y_base), 9.2, layer['height'],
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
        ax.text(0.75, layer['y'], layer['name'],
                ha='left', va='center', fontsize=13, fontweight='bold',
                color='#1A237E')
        
        # 模块
        n_modules = len(layer['modules'])
        module_width = 1.65
        gap = 0.2
        total_width = n_modules * module_width + (n_modules - 1) * gap
        start_x = 9.7 - total_width
        
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
                    color='#1A237E', multialignment='center')
    
    # ===== 层间箭头（优化箭头头部形状：短杆1/3长度，45度角） =====
    for i in range(len(layers) - 1):
        y1 = layers[i]['y'] - layers[i]['height']/2 - 0.05
        y2 = layers[i+1]['y'] + layers[i+1]['height']/2 + 0.05
        
        # 绘制多个箭头
        for j in range(3):
            x = 2.5 + j * 2.8
            
            # 使用FancyArrowPatch，箭头头部短杆1/3，45度角
            arrow = FancyArrowPatch(
                (x, y1), (x, y2),
                arrowstyle='->,head_width=0.25,head_length=0.15',  # 缩短头部到1/3，45度角
                mutation_scale=20,  # 减小缩放以获得更紧凑的箭头
                color=colors['border'],
                linewidth=2.5,
                alpha=0.7,
                zorder=4,
                shrinkA=0,
                shrinkB=0
            )
            ax.add_patch(arrow)
    
    # ===== 左侧数据流指示箭头（单向向下，优化头部形状） =====
    data_flow_arrow = FancyArrowPatch(
        (0.15, 9.0), (0.15, 1.1),
        arrowstyle='->,head_width=0.3,head_length=0.18',  # 缩短头部到1/3，45度角
        mutation_scale=20,
        color=colors['border'],
        linewidth=3,
        alpha=0.6,
        zorder=5
    )
    ax.add_patch(data_flow_arrow)
    
    # 数据流文字（放在箭头旁边）
    ax.text(-0.15, 5.0, 'Data\nFlow', 
            ha='center', va='center',
            fontsize=12, fontweight='bold', 
            color=colors['border'], rotation=90)
    
    # 标题
    ax.text(5, 9.7, 'FinLoom System Architecture',
            ha='center', va='center', fontsize=17, fontweight='bold',
            color='#1A237E')
    
    plt.tight_layout(pad=0.8)
    plt.savefig('fig6.png', dpi=300, bbox_inches='tight', pad_inches=0.3,
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig6.png with optimized arrow heads!")
    print("\nArrow head improvements:")
    print("  - Arrow head short bars: reduced to 1/3 length")
    print("  - Arrow head angle: 45 degrees (was wider)")
    print("  - head_width: 0.25, head_length: 0.15")
    print("  - mutation_scale: 20 (compact arrows)")
    print("  - Left side: Single downward arrow with same style")
    plt.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Fixing fig6 arrows...")
    print("="*60 + "\n")
    
    create_fixed_architecture()
    
    print("\n" + "="*60)
    print("✓ fig6 fixed!")
    print("="*60 + "\n")

