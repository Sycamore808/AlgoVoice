"""
修复系统流程图，让箭头更清晰明显
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 13
plt.rcParams['figure.dpi'] = 300

def create_clear_flow_with_arrows():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 节点定义
    nodes = [
        {'name': 'Multi-source\nData Input', 'pos': (3, 8), 'color': '#E3F2FD', 'size': 1.6},
        {'name': 'Feature\nExtraction', 'pos': (3, 5.5), 'color': '#FFF9C4', 'size': 1.6},
        {'name': 'FIN-R1\nDecision\nModel', 'pos': (7, 5.5), 'color': '#C8E6C9', 'size': 2.2},
        {'name': 'Portfolio\nConstruction', 'pos': (11, 5.5), 'color': '#FFE0B2', 'size': 1.6},
        {'name': 'Risk\nAssessment', 'pos': (7, 2.8), 'color': '#FFCDD2', 'size': 1.6},
        {'name': 'Order\nExecution', 'pos': (7, 0.5), 'color': '#E1BEE7', 'size': 1.6},
    ]
    
    # 绘制节点
    for node in nodes:
        # 阴影
        shadow = Circle((node['pos'][0] + 0.1, node['pos'][1] - 0.1), node['size']/2,
                       edgecolor='none', facecolor='gray',
                       alpha=0.3, zorder=1)
        ax.add_patch(shadow)
        
        # 节点
        circle = Circle(node['pos'], node['size']/2,
                       edgecolor='#1565C0', facecolor=node['color'],
                       linewidth=3.5, zorder=2)
        ax.add_patch(circle)
        
        # 文字
        ax.text(node['pos'][0], node['pos'][1], node['name'],
                ha='center', va='center', fontsize=13, fontweight='bold',
                color='#1A237E', multialignment='center', zorder=3)
    
    # 连接定义（更详细的箭头配置）
    arrows = [
        # (起点, 终点, 标签, 样式)
        {'from': 0, 'to': 1, 'label': '', 'style': 'normal'},
        {'from': 1, 'to': 2, 'label': 'Features', 'style': 'normal'},
        {'from': 2, 'to': 3, 'label': 'Signals', 'style': 'normal'},
        {'from': 3, 'to': 4, 'label': 'Portfolio', 'style': 'normal'},
        {'from': 4, 'to': 5, 'label': 'Validated', 'style': 'normal'},
        {'from': 4, 'to': 2, 'label': 'Adjust', 'style': 'feedback'},
    ]
    
    # 绘制箭头
    for arrow_cfg in arrows:
        i = arrow_cfg['from']
        j = arrow_cfg['to']
        label = arrow_cfg['label']
        style = arrow_cfg['style']
        
        pos1 = np.array(nodes[i]['pos'])
        pos2 = np.array(nodes[j]['pos'])
        r1 = nodes[i]['size']/2
        r2 = nodes[j]['size']/2
        
        # 计算方向向量
        direction = pos2 - pos1
        distance = np.linalg.norm(direction)
        
        if distance > 0:
            direction_norm = direction / distance
            
            # 起点和终点（考虑圆的半径）
            start = pos1 + direction_norm * r1
            end = pos2 - direction_norm * r2
            
            # 根据样式设置箭头属性
            if style == 'feedback':
                # 反馈回路：红色、虚线、大箭头、弧形
                arrow_style = '->,head_width=0.8,head_length=0.6'
                connection_style = 'arc3,rad=0.45'
                color = '#FF3D00'
                linewidth = 4.5
                linestyle = '--'
                alpha = 0.9
                zorder = 5
            else:
                # 正常流程：蓝色、实线、大箭头
                arrow_style = '->,head_width=0.7,head_length=0.5'
                connection_style = 'arc3,rad=0'
                color = '#1565C0'
                linewidth = 4.5
                linestyle = '-'
                alpha = 0.85
                zorder = 4
            
            # 绘制箭头
            arrow = FancyArrowPatch(
                start, end,
                arrowstyle=arrow_style,
                connectionstyle=connection_style,
                color=color,
                linewidth=linewidth,
                linestyle=linestyle,
                alpha=alpha,
                zorder=zorder,
                mutation_scale=1.5  # 让箭头更大
            )
            ax.add_patch(arrow)
            
            # 绘制标签
            if label:
                # 计算标签位置
                if style == 'feedback':
                    # 反馈回路标签放在弧线外侧
                    mid = (start + end) / 2
                    offset = np.array([1.2, 0])  # 向右偏移
                    label_pos = mid + offset
                    label_color = '#FF3D00'
                else:
                    # 正常标签放在箭头中间
                    mid = (start + end) / 2
                    # 垂直方向稍微偏移，避免压在箭头上
                    perpendicular = np.array([-direction_norm[1], direction_norm[0]])
                    label_pos = mid + perpendicular * 0.3
                    label_color = '#1565C0'
                
                # 绘制标签背景框
                bbox_props = dict(
                    boxstyle='round,pad=0.5',
                    facecolor='white',
                    edgecolor=label_color,
                    linewidth=2.5,
                    alpha=0.95
                )
                
                ax.text(label_pos[0], label_pos[1], label,
                       ha='center', va='center',
                       fontsize=12, fontweight='bold',
                       color=label_color,
                       bbox=bbox_props,
                       zorder=10)
    
    # 添加箭头图例（说明）
    legend_y = 9.3
    
    # 正向流程箭头示例
    ax.plot([0.5, 2], [legend_y, legend_y], 
            color='#1565C0', linewidth=4.5, linestyle='-',
            marker='>', markersize=15, markerfacecolor='#1565C0',
            markeredgecolor='#1565C0', solid_capstyle='butt')
    ax.text(2.3, legend_y, 'Forward Flow', 
            ha='left', va='center', fontsize=12, fontweight='bold',
            color='#1565C0')
    
    # 反馈回路箭头示例
    ax.plot([5, 6.5], [legend_y, legend_y], 
            color='#FF3D00', linewidth=4.5, linestyle='--',
            marker='>', markersize=15, markerfacecolor='#FF3D00',
            markeredgecolor='#FF3D00', solid_capstyle='butt')
    ax.text(6.8, legend_y, 'Feedback Loop', 
            ha='left', va='center', fontsize=12, fontweight='bold',
            color='#FF3D00')
    
    # 标题
    ax.text(7, 9.7, 'AlgoVoice System - Core Computation Flow',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color='#1A237E',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#E8F5E9',
                     edgecolor='#1565C0', linewidth=2.5, alpha=0.8))
    
    # 底部说明
    ax.text(7, 0.1, 'All arrows show clear data flow direction with enhanced visibility',
            ha='center', va='center', fontsize=10, style='italic',
            color='gray')
    
    plt.tight_layout()
    plt.savefig('fig_system_diagram.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print("✓ Fixed fig_system_diagram.png - Arrows are now clear!")
    plt.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Fixing system flow diagram...")
    print("="*60 + "\n")
    
    create_clear_flow_with_arrows()
    
    print("\n" + "="*60)
    print("✓ Flow diagram fixed with clear arrows!")
    print("="*60)
    print("\nImprovements:")
    print("  - Arrow width: 4.5pt (was 3pt)")
    print("  - Arrow heads: 0.7-0.8 wide (was 0.5)")
    print("  - Feedback loop: Red color, thicker dashed line")
    print("  - Labels: Larger font with clear backgrounds")
    print("  - Legend: Added arrow style explanation")
    print("\n")

