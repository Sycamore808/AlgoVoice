#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询用户列表
"""

import sqlite3
from pathlib import Path

db_path = Path("data/users.db")

if not db_path.exists():
    print("❌ 用户数据库不存在")
    print("   数据库会在首次启动时创建")
    exit(1)

print("=" * 70)
print("AlgoVoice 用户列表")
print("=" * 70)
print()

try:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, username, email, display_name, 
                   is_admin, permission_level, created_at, last_login
            FROM users 
            ORDER BY user_id
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("📭 暂无用户")
            print()
            print("💡 提示：系统首次启动时会自动创建默认管理员账号")
            print("   用户名: Sycamore1024")
            print("   密码: AlgoVoicetest")
        else:
            for user in users:
                print(f"用户 ID: {user['user_id']}")
                print(f"用户名: {user['username']}")
                print(f"显示名: {user['display_name']}")
                print(f"邮箱: {user['email'] or '未设置'}")
                print(f"管理员: {'是' if user['is_admin'] else '否'}")
                print(f"权限等级: {user['permission_level']}")
                print(f"创建时间: {user['created_at']}")
                print(f"最后登录: {user['last_login'] or '从未登录'}")
                print("-" * 70)
                print()
            
            print(f"总计: {len(users)} 个用户")
        
        print("=" * 70)
        print()
        print("⚠️  注意：出于安全考虑，密码经过加密存储，无法查看明文")
        print("         如需重置密码，请联系系统管理员")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")
    
input("\n按回车键退出...")











