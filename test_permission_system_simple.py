#!/usr/bin/env python3
"""
简化的权限系统测试脚本
直接测试权限组功能，不依赖复杂的配置加载
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_permission_groups_direct():
    """直接测试权限组系统"""
    print("🔐 开始直接测试权限组系统...")
    
    try:
        # 导入权限相关模块
        from src.permission_groups import ServerGroup, PermissionLevel
        
        # 创建测试数据
        test_group_data = {
            "name": "测试服务器组1",
            "description": "用于测试的服务器组",
            "allowed_groups": ["123456789"],  # 修正字段名
            "game_servers": {
                "server1": {
                    "id": "server1",
                    "name": "测试服务器1",
                    "enabled": True
                },
                "server2": {
                    "id": "server2", 
                    "name": "测试服务器2",
                    "enabled": True
                }
            },
            "server_aliases": {
                "主服": "server1",
                "副服": "server2",
                "1": "server1",
                "2": "server2"
            },
            "permissions": {
                "owners": ["1001"],
                "super_admins": [],
                "admins": ["1002"],
                "users": ["1003"]
            },
            "features": {
                "player_commands": True,
                "admin_commands": True,
                "server_management": True
            }
        }
        
        # 创建服务器组实例
        server_group = ServerGroup("test_group_1", test_group_data)
        print("✅ 服务器组创建成功")
        
        # 测试1: 权限检查
        print("\n👤 测试1: 权限检查")
        
        # 测试用户1001 (OWNER)
        owner_admin_check = server_group.has_permission("1001", PermissionLevel.ADMIN)
        owner_owner_check = server_group.has_permission("1001", PermissionLevel.OWNER)
        print(f"  用户 1001 (OWNER) 管理员权限: {owner_admin_check}")
        print(f"  用户 1001 (OWNER) 所有者权限: {owner_owner_check}")
        
        # 测试用户1002 (ADMIN)
        admin_admin_check = server_group.has_permission("1002", PermissionLevel.ADMIN)
        admin_owner_check = server_group.has_permission("1002", PermissionLevel.OWNER)
        print(f"  用户 1002 (ADMIN) 管理员权限: {admin_admin_check}")
        print(f"  用户 1002 (ADMIN) 所有者权限: {admin_owner_check}")
        
        # 测试用户1003 (USER)
        user_admin_check = server_group.has_permission("1003", PermissionLevel.ADMIN)
        user_user_check = server_group.has_permission("1003", PermissionLevel.USER)
        print(f"  用户 1003 (USER) 管理员权限: {user_admin_check}")
        print(f"  用户 1003 (USER) 用户权限: {user_user_check}")
        
        # 测试2: 功能权限检查
        print("\n⚙️ 测试2: 功能权限检查")
        
        owner_feature = server_group.has_feature_permission("1001", "admin_commands")
        admin_feature = server_group.has_feature_permission("1002", "admin_commands")
        user_feature = server_group.has_feature_permission("1003", "admin_commands")
        
        print(f"  用户 1001 (OWNER) admin_commands功能: {owner_feature}")
        print(f"  用户 1002 (ADMIN) admin_commands功能: {admin_feature}")
        print(f"  用户 1003 (USER) admin_commands功能: {user_feature}")
        
        # 测试3: 服务器别名解析
        print("\n🔍 测试3: 服务器别名解析")
        
        alias1 = server_group.resolve_server_alias("主服")
        alias2 = server_group.resolve_server_alias("1")
        alias3 = server_group.resolve_server_alias("不存在")
        
        print(f"  别名 '主服' -> {alias1}")
        print(f"  别名 '1' -> {alias2}")
        print(f"  别名 '不存在' -> {alias3}")
        
        # 测试4: QQ群检查
        print("\n📱 测试4: QQ群检查")
        
        group_check1 = server_group.is_group_allowed("123456789")
        group_check2 = server_group.is_group_allowed("999999999")
        
        print(f"  QQ群 123456789 允许: {group_check1}")
        print(f"  QQ群 999999999 允许: {group_check2}")
        
        print("\n✅ 权限组系统直接测试完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 权限组系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_functions():
    """测试集成函数"""
    print("\n🔗 开始测试集成函数...")
    
    try:
        # 测试config.py中的权限检查函数
        from src.config import is_admin_user
        from src.permissions import is_admin, has_feature_permission
        
        print("✅ 权限系统模块导入成功")
        
        # 由于没有实际的权限组配置，这些测试可能返回False
        # 但至少可以验证函数调用不会出错
        
        print("\n👤 测试1: is_admin_user函数")
        admin_check1 = is_admin_user("1001")
        admin_check2 = is_admin_user("1001", "123456789")
        print(f"  用户 1001 (无QQ群): {admin_check1}")
        print(f"  用户 1001 (QQ群 123456789): {admin_check2}")
        
        print("\n🔐 测试2: is_admin函数")
        admin_check3 = is_admin("1001")
        admin_check4 = is_admin("1001", "123456789")
        print(f"  用户 1001 (无QQ群): {admin_check3}")
        print(f"  用户 1001 (QQ群 123456789): {admin_check4}")
        
        print("\n⚙️ 测试3: has_feature_permission函数")
        feature_check1 = has_feature_permission("1001", "admin_commands")
        feature_check2 = has_feature_permission("1001", "admin_commands", "123456789")
        print(f"  用户 1001, admin_commands功能 (无QQ群): {feature_check1}")
        print(f"  用户 1001, admin_commands功能 (QQ群 123456789): {feature_check2}")
        
        print("\n✅ 集成函数测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 集成函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎯 开始权限系统测试")
    print("=" * 50)
    
    # 测试1: 直接测试权限组
    success1 = test_permission_groups_direct()
    
    # 测试2: 测试集成函数
    success2 = test_integration_functions()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit(main())