#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""详细测试 - 查看具体读取到什么数据"""
import baostock as bs
import pandas as pd

print("="*60)
print("详细测试Baostock API")
print("="*60)

# 登录
lg = bs.login()
print(f"\n1. 登录: {lg.error_code} - {lg.error_msg if lg.error_code != '0' else 'OK'}")

if lg.error_code != '0':
    print("登录失败，退出")
    exit(1)

# 获取股票列表
print("\n2. 查询股票列表...")
rs = bs.query_all_stock(day='2025-12-10')
print(f"   查询结果: {rs.error_code} - {rs.error_msg if rs.error_code != '0' else 'OK'}")

if rs.error_code != '0':
    print("查询失败，退出")
    bs.logout()
    exit(1)

# 查看字段
print(f"\n3. 返回字段: {rs.fields}")

# 读取前10条数据看看
print("\n4. 读取前10条数据:")
data_list = []
count = 0
while rs.next() and count < 10:
    row = rs.get_row_data()
    data_list.append(row)
    print(f"   [{count+1}] {row}")
    count += 1

# 继续读取剩余数据（不打印）
print("\n5. 继续读取剩余数据...")
while rs.next():
    data_list.append(rs.get_row_data())
    count += 1
    if count % 1000 == 0:
        print(f"   进度: {count} 条")

print(f"\n6. 总计: {count} 条")

# 转换为DataFrame分析
if data_list:
    df = pd.DataFrame(data_list, columns=rs.fields)
    print(f"\n7. 数据分析:")
    print(f"   数据形状: {df.shape}")
    print(f"   列名: {list(df.columns)}")
    
    if 'code' in df.columns:
        print(f"\n   前5条代码:")
        print(df['code'].head(5).tolist())
        print(f"\n   后5条代码:")
        print(df['code'].tail(5).tolist())
        
        # 统计
        sh_count = df['code'].str.startswith('sh.').sum()
        sz_count = df['code'].str.startswith('sz.').sum()
        print(f"\n   上交所(sh): {sh_count}")
        print(f"   深交所(sz): {sz_count}")

bs.logout()
print("\n" + "="*60)
print("测试完成")
print("="*60)








