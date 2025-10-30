#!/usr/bin/env python3
"""
测试新的权限组系统
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_permission_groups():
    """测试权限组系统"""
    print("🧪 开始测试权限组系统...")
    
    try:
        # 临时修改配置文件路径以使用测试配置
        import os
        original_config_file = os.environ.get('PERMISSION_GROUPS_CONFIG', 'permission_groups.yaml')
        os.environ['PERMISSION_GROUPS_CONFIG'] = 'permission_groups_test.yaml'
        
        from src.permission_groups import get_permission_group_manager, PermissionLevel
        
        # 使用测试配置文件初始化
        manager = get_permission_group_manager()
        
        # 强制重新加载配置
        manager.reload_config()
        
        print("✅ 权限组管理器初始化成功")
        
        # 测试1: 检查QQ群对应的服务器组
        print("\n📋 测试1: QQ群到服务器组的映射")
        
        group1 = manager.get_group_for_qq_group("123456789")
        if group1:
            print(f"  QQ群 123456789 -> 服务器组: {group1.name}")
        else:
            print("  ❌ QQ群 123456789 没有找到对应的服务器组")
        
        group2 = manager.get_group_for_qq_group("987654321")
        if group2:
            print(f"  QQ群 987654321 -> 服务器组: {group2.name}")
        else:
            print("  ❌ QQ群 987654321 没有找到对应的服务器组")
        
        # 测试2: 服务器别名解析
        print("\n🔗 测试2: 服务器别名解析")
        
        # 测试组1的别名
        resolved1 = manager.resolve_server_alias_for_qq_group("123456789", "主服")
        print(f"  QQ群 123456789, 别名 '主服' -> {resolved1}")
        
        resolved2 = manager.resolve_server_alias_for_qq_group("123456789", "1")
        print(f"  QQ群 123456789, 别名 '1' -> {resolved2}")
        
        # 测试组2的别名
        resolved3 = manager.resolve_server_alias_for_qq_group("987654321", "主服")
        print(f"  QQ群 987654321, 别名 '主服' -> {resolved3}")
        
        resolved4 = manager.resolve_server_alias_for_qq_group("987654321", "A")
        print(f"  QQ群 987654321, 别名 'A' -> {resolved4}")
        
        # 测试3: 权限检查
        print("\n🔐 测试3: 权限检查")
        
        # 测试组1的权限
        has_owner1 = manager.has_permission_in_group("123456789", "1001", PermissionLevel.OWNER)
        print(f"  QQ群 123456789, 用户 1001, OWNER权限: {has_owner1}")
        
        has_admin1 = manager.has_permission_in_group("123456789", "1002", PermissionLevel.ADMIN)
        print(f"  QQ群 123456789, 用户 1002, ADMIN权限: {has_admin1}")
        
        has_player1 = manager.has_permission_in_group("123456789", "1003", PermissionLevel.USER)
        print(f"  QQ群 123456789, 用户 1003, USER权限: {has_player1}")
        
        # 测试组2的权限
        has_owner2 = manager.has_permission_in_group("987654321", "2001", PermissionLevel.OWNER)
        print(f"  QQ群 987654321, 用户 2001, OWNER权限: {has_owner2}")
        
        has_admin2 = manager.has_permission_in_group("987654321", "2002", PermissionLevel.ADMIN)
        print(f"  QQ群 987654321, 用户 2002, ADMIN权限: {has_admin2}")
        
        # 测试4: 功能权限检查
        print("\n⚙️ 测试4: 功能权限检查")
        
        has_feature1 = manager.has_feature_permission_in_group("123456789", "admin_commands")
        print(f"  QQ群 123456789, admin_commands功能: {has_feature1}")
        
        has_feature2 = manager.has_feature_permission_in_group("987654321", "admin_commands")
        print(f"  QQ群 987654321, admin_commands功能: {has_feature2}")
        
        print("\n✅ 权限组系统测试完成")
        
        # 恢复原始配置
        os.environ['PERMISSION_GROUPS_CONFIG'] = original_config_file
        
    except Exception as e:
        print(f"❌ 权限组系统测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_multi_server_manager():
    """测试多服务器管理器"""
    print("\n🖥️ 开始测试多服务器管理器...")
    
    try:
        from src.multi_server_manager import MultiServerManager
        
        # 创建测试配置
        test_config = {
            'servers': {
                'server1': {
                    'name': '测试服务器1',
                    'display_name': '主服',
                    'api_base_url': 'http://localhost:8010/api',
                    'api_token': 'test_token_1',
                    'enabled': True
                },
                'server2': {
                    'name': '测试服务器2', 
                    'display_name': '副服',
                    'api_base_url': 'http://localhost:8011/api',
                    'api_token': 'test_token_2',
                    'enabled': True
                }
            },
            'server_aliases': {
                '1': 'server1',
                '2': 'server2',
                '主': 'server1',
                '副': 'server2'
            }
        }
        
        # 创建临时配置文件
        import yaml
        with open('test_config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, allow_unicode=True)
        
        # 初始化管理器
        manager = MultiServerManager('test_config.yaml')
        
        print("✅ 多服务器管理器初始化成功")
        
        # 测试1: 服务器ID解析（不带QQ群ID）
        print("\n🔍 测试1: 服务器ID解析（全局别名）")
        
        resolved1 = manager.resolve_server_id("1")
        print(f"  别名 '1' -> {resolved1}")
        
        resolved2 = manager.resolve_server_id("主")
        print(f"  别名 '主' -> {resolved2}")
        
        # 测试2: 服务器ID解析（带QQ群ID）
        print("\n🔍 测试2: 服务器ID解析（带QQ群ID）")
        
        resolved3 = manager.resolve_server_id("主服", "123456789")
        print(f"  QQ群 123456789, 别名 '主服' -> {resolved3}")
        
        resolved4 = manager.resolve_server_id("A", "987654321")
        print(f"  QQ群 987654321, 别名 'A' -> {resolved4}")
        
        # 测试3: 获取服务器配置
        print("\n⚙️ 测试3: 获取服务器配置")
        
        config1 = manager.get_server_config("server1")
        if config1:
            print(f"  服务器 server1: {config1.name} ({config1.display_name})")
        
        config2 = manager.get_server_config("主服", "123456789")
        if config2:
            print(f"  QQ群 123456789, 别名 '主服': {config2.name} ({config2.display_name})")
        
        print("\n✅ 多服务器管理器测试完成")
        
        # 清理临时文件
        os.remove('test_config.yaml')
        
    except Exception as e:
        print(f"❌ 多服务器管理器测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_permissions_integration():
    """测试权限系统集成"""
    print("\n🔗 开始测试权限系统集成...")
    
    try:
        from src.permissions import check_permission, is_admin, has_feature_permission
        from src.config import is_admin_user
        
        print("✅ 权限系统模块导入成功")
        
        # 测试1: is_admin_user函数
        print("\n👤 测试1: is_admin_user函数")
        
        # 不带QQ群ID（使用旧系统）
        is_admin1 = is_admin_user("1001")
        print(f"  用户 1001 (无QQ群): {is_admin1}")
        
        # 带QQ群ID（使用新系统）
        is_admin2 = is_admin_user("1001", "123456789")
        print(f"  用户 1001 (QQ群 123456789): {is_admin2}")
        
        is_admin3 = is_admin_user("2001", "987654321")
        print(f"  用户 2001 (QQ群 987654321): {is_admin3}")
        
        # 测试2: is_admin函数
        print("\n🔐 测试2: is_admin函数")
        
        admin_check1 = is_admin("1001")
        print(f"  用户 1001 (无QQ群): {admin_check1}")
        
        admin_check2 = is_admin("1001", "123456789")
        print(f"  用户 1001 (QQ群 123456789): {admin_check2}")
        
        # 测试3: has_feature_permission函数
        print("\n⚙️ 测试3: has_feature_permission函数")
        
        feature_check1 = has_feature_permission("1001", "admin_commands")
        print(f"  用户 1001, admin_commands功能 (无QQ群): {feature_check1}")
        
        feature_check2 = has_feature_permission("1001", "admin_commands", "123456789")
        print(f"  用户 1001, admin_commands功能 (QQ群 123456789): {feature_check2}")
        
        feature_check3 = has_feature_permission("2001", "admin_commands", "987654321")
        print(f"  用户 2001, admin_commands功能 (QQ群 987654321): {feature_check3}")
        
        print("\n✅ 权限系统集成测试完成")
        
    except Exception as e:
        print(f"❌ 权限系统集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试新的独立权限和别名系统\n")
    
    # 运行所有测试
    test_permission_groups()
    test_multi_server_manager()
    test_permissions_integration()
    
    print("\n🎉 所有测试完成！")