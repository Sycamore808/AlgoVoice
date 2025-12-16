#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试获取股票列表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import baostock as bs
import pandas as pd

print("="*60)
print("测试Baostock获取股票列表")
print("="*60)

# 登录
print("\n[1/3] 登录Baostock...")
lg = bs.login()
if lg.error_code != '0':
    print(f"❌ 登录失败：{lg.error_msg}")
    exit(1)
print("✓ 登录成功")

# 获取股票列表
print("\n[2/3] 获取所有股票列表...")
try:
    rs = bs.query_all_stock()
    
    if rs.error_code != '0':
        print(f"❌ 查询失败：{rs.error_msg}")
        bs.logout()
        exit(1)
    
    # 方法1：使用while循环
    print("   使用 while rs.next() 方式读取...")
    data_list = []
    while rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        print("❌ 未获取到任何数据")
        bs.logout()
        exit(1)
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"✓ 成功获取 {len(df)} 只股票/指数")
    
    # 过滤A股
    if 'type' in df.columns:
        a_shares = df[df['type'] == '1']  # type=1表示股票
        print(f"✓ 其中A股股票：{len(a_shares)} 只")
    
    # 显示前10条
    print("\n前10条数据：")
    print(df.head(10).to_string())
    
    # 显示统计
    print(f"\n数据列：{list(df.columns)}")
    if 'code' in df.columns:
        sh_count = len(df[df['code'].str.startswith('sh.')])
        sz_count = len(df[df['code'].str.startswith('sz.')])
        print(f"上交所(sh)：{sh_count} 只")
        print(f"深交所(sz)：{sz_count} 只")

except Exception as e:
    print(f"❌ 发生错误：{e}")
    import traceback
    traceback.print_exc()
    bs.logout()
    exit(1)

# 登出
print("\n[3/3] 登出...")
bs.logout()
print("✓ 测试完成")

print("\n" + "="*60)
print("结论：如果显示5000+只股票，说明API正常工作！")
print("="*60)








