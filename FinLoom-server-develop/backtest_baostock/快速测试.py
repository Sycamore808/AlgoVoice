#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速测试股票列表获取"""
import baostock as bs

print("正在测试...")
lg = bs.login()
print(f"1. 登录结果: {lg.error_code} ({lg.error_msg if lg.error_code != '0' else 'OK'})")

if lg.error_code == '0':
    # 必须传入一个交易日期！
    rs = bs.query_all_stock(day='2025-12-10')
    print(f"2. 查询结果: {rs.error_code} ({rs.error_msg if rs.error_code != '0' else 'OK'})")
    
    if rs.error_code == '0':
        count = 0
        while rs.next():
            count += 1
            if count % 1000 == 0:
                print(f"   已读取: {count} 条...")
        
        print(f"3. 总计: {count} 只股票/指数")
        
        if count > 5000:
            print("\n✓ 成功！获取到完整的股票列表！")
        else:
            print(f"\n✗ 失败！仅获取到 {count} 条数据")
    
    bs.logout()

