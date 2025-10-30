#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限组管理模块
支持多个服务器组的独立权限配置
"""

from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import yaml
import json
from datetime import datetime
from enum import Enum

from nonebot import logger
from .config import config


class PermissionLevel(Enum):
    """权限级别枚举"""
    OWNER = "owner"
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"


class ServerGroup:
    """服务器组类"""
    
    def __init__(self, group_id: str, group_data: Dict[str, Any]):
        self.group_id = group_id
        self.name = group_data.get('name', group_id)
        self.description = group_data.get('description', '')
        self.game_servers = group_data.get('game_servers', [])
        self.permissions = group_data.get('permissions', {})
        self.allowed_groups = set(group_data.get('allowed_groups', []))
        self.features = group_data.get('features', {})
    
    def get_user_permission(self, user_id: str) -> PermissionLevel:
        """获取用户在此服务器组的权限级别"""
        if user_id in self.permissions.get('owners', []):
            return PermissionLevel.OWNER
        elif user_id in self.permissions.get('super_admins', []):
            return PermissionLevel.SUPER_ADMIN
        elif user_id in self.permissions.get('admins', []):
            return PermissionLevel.ADMIN
        else:
            return PermissionLevel.USER
    
    def has_permission(self, user_id: str, required_level: PermissionLevel) -> bool:
        """检查用户是否有指定权限"""
        user_level = self.get_user_permission(user_id)
        level_hierarchy = {
            PermissionLevel.USER: 0,
            PermissionLevel.ADMIN: 1,
            PermissionLevel.SUPER_ADMIN: 2,
            PermissionLevel.OWNER: 3
        }
        return level_hierarchy[user_level] >= level_hierarchy[required_level]
    
    def has_feature_permission(self, user_id: str, feature: str) -> bool:
        """检查用户是否有特定功能权限"""
        # 主人和超级管理员默认拥有所有功能权限
        user_level = self.get_user_permission(user_id)
        if user_level in [PermissionLevel.OWNER, PermissionLevel.SUPER_ADMIN]:
            return self.features.get(feature, True)
        elif user_level == PermissionLevel.ADMIN:
            return self.features.get(feature, False)
        else:
            # 普通用户只能使用查询功能
            return feature in ['allow_player_list'] and self.features.get(feature, True)
    
    def is_group_allowed(self, group_id: str) -> bool:
        """检查QQ群是否被允许使用此服务器组"""
        return group_id in self.allowed_groups
    
    def get_enabled_servers(self) -> List[Dict[str, Any]]:
        """获取启用的游戏服务器列表"""
        return [server for server in self.game_servers if server.get('enabled', True)]


class PermissionGroupManager:
    """权限组管理器"""
    
    def __init__(self):
        # 使用新的统一配置文件
        from .utils.config_loader import get_config
        self.config_loader = get_config()
        
        # 保留缓存和日志文件路径
        self.cache_file = Path("data/permission_groups_cache.json")
        self.log_file = Path("logs/permissions.log")
        
        # 确保目录存在
        self.cache_file.parent.mkdir(exist_ok=True)
        self.log_file.parent.mkdir(exist_ok=True)
        
        self.server_groups: Dict[str, ServerGroup] = {}
        self.global_settings: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载权限组配置"""
        try:
            # 从统一配置文件加载权限组配置
            permission_groups_data = self.config_loader.get_permission_groups()
            global_settings_data = self.config_loader.get_global_settings()
            
            # 加载服务器组
            self.server_groups = {}
            for group_id, group_data in permission_groups_data.items():
                self.server_groups[group_id] = ServerGroup(group_id, group_data)
            
            # 加载全局设置
            self.global_settings = {
                'default_group': global_settings_data.get('default_server_group', 'group_a'),
                'enable_cross_group_permissions': global_settings_data.get('enable_cross_group_permissions', True),
                'permission_cache_time': global_settings_data.get('permission_cache_time', 300),
                'log_permission_operations': global_settings_data.get('log_permission_operations', True)
            }
            
            logger.info(f"已加载 {len(self.server_groups)} 个服务器组配置")
            
        except Exception as e:
            logger.error(f"加载权限组配置失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        self.server_groups = {}
        self.global_settings = {
            'default_group': 'group_a',
            'enable_cross_group_permissions': True,
            'permission_cache_time': 300,
            'log_permission_operations': True
        }
    
    def reload_config(self):
        """重新加载配置"""
        self.config_loader.reload()
        self._load_config()
        self._log_operation("CONFIG_RELOAD", "system", "配置文件已重新加载")
    
    def get_server_group(self, group_id: str) -> Optional[ServerGroup]:
        """获取服务器组"""
        return self.server_groups.get(group_id)
    
    def get_default_group(self) -> Optional[ServerGroup]:
        """获取默认服务器组"""
        default_group_id = self.global_settings.get('default_group')
        if default_group_id:
            return self.get_server_group(default_group_id)
        # 如果没有配置默认组，返回第一个组
        if self.server_groups:
            return list(self.server_groups.values())[0]
        return None
    
    def get_group_for_qq_group(self, qq_group_id: str) -> Optional[ServerGroup]:
        """根据QQ群ID获取对应的服务器组"""
        for server_group in self.server_groups.values():
            if server_group.is_group_allowed(qq_group_id):
                return server_group
        return self.get_default_group()
    
    def get_user_permission_in_group(self, user_id: str, group_id: str) -> PermissionLevel:
        """获取用户在指定服务器组的权限"""
        server_group = self.get_server_group(group_id)
        if server_group:
            return server_group.get_user_permission(user_id)
        return PermissionLevel.USER
    
    def has_permission_in_group(self, user_id: str, group_id: str, required_level: PermissionLevel) -> bool:
        """检查用户在指定服务器组是否有权限"""
        server_group = self.get_server_group(group_id)
        if server_group:
            # 检查跨组权限
            if self.global_settings.get('enable_cross_group_permissions', True):
                # 检查用户是否在任何组中都是主人
                for sg in self.server_groups.values():
                    if sg.get_user_permission(user_id) == PermissionLevel.OWNER:
                        return True
            return server_group.has_permission(user_id, required_level)
        return False
    
    def has_feature_permission_in_group(self, user_id: str, group_id: str, feature: str) -> bool:
        """检查用户在指定服务器组是否有功能权限"""
        server_group = self.get_server_group(group_id)
        if server_group:
            return server_group.has_feature_permission(user_id, feature)
        return False
    
    def add_user_to_group(self, user_id: str, group_id: str, level: PermissionLevel, operator_id: str) -> tuple[bool, str]:
        """添加用户到服务器组"""
        server_group = self.get_server_group(group_id)
        if not server_group:
            return False, f"服务器组 {group_id} 不存在"
        
        # 检查操作者权限
        if not self.has_permission_in_group(operator_id, group_id, PermissionLevel.SUPER_ADMIN):
            return False, "权限不足，需要超级管理员权限"
        
        # 不能添加比自己权限高的用户
        operator_level = server_group.get_user_permission(operator_id)
        if level.value in ['owner', 'super_admin'] and operator_level != PermissionLevel.OWNER:
            return False, "只有主人可以添加主人和超级管理员"
        
        # 添加用户
        level_key = f"{level.value}s"
        if level_key not in server_group.permissions:
            server_group.permissions[level_key] = []
        
        if user_id not in server_group.permissions[level_key]:
            server_group.permissions[level_key].append(user_id)
            self._save_config()
            self._log_operation("ADD_USER", operator_id, f"添加用户 {user_id} 到组 {group_id}，权限级别: {level.value}")
            return True, f"成功添加用户到 {server_group.name}"
        else:
            return False, "用户已存在于该权限级别"
    
    def remove_user_from_group(self, user_id: str, group_id: str, operator_id: str) -> tuple[bool, str]:
        """从服务器组移除用户"""
        server_group = self.get_server_group(group_id)
        if not server_group:
            return False, f"服务器组 {group_id} 不存在"
        
        # 检查操作者权限
        if not self.has_permission_in_group(operator_id, group_id, PermissionLevel.SUPER_ADMIN):
            return False, "权限不足，需要超级管理员权限"
        
        # 不能移除比自己权限高的用户
        operator_level = server_group.get_user_permission(operator_id)
        target_level = server_group.get_user_permission(user_id)
        
        if target_level in [PermissionLevel.OWNER, PermissionLevel.SUPER_ADMIN] and operator_level != PermissionLevel.OWNER:
            return False, "只有主人可以移除主人和超级管理员"
        
        # 移除用户
        removed = False
        for level_key in ['owners', 'super_admins', 'admins']:
            if user_id in server_group.permissions.get(level_key, []):
                server_group.permissions[level_key].remove(user_id)
                removed = True
                break
        
        if removed:
            self._save_config()
            self._log_operation("REMOVE_USER", operator_id, f"从组 {group_id} 移除用户 {user_id}")
            return True, f"成功从 {server_group.name} 移除用户"
        else:
            return False, "用户不在任何权限级别中"
    
    def list_groups(self) -> Dict[str, Dict[str, Any]]:
        """列出所有服务器组"""
        result = {}
        for group_id, server_group in self.server_groups.items():
            result[group_id] = {
                'name': server_group.name,
                'description': server_group.description,
                'servers_count': len(server_group.get_enabled_servers()),
                'users_count': {
                    'owners': len(server_group.permissions.get('owners', [])),
                    'super_admins': len(server_group.permissions.get('super_admins', [])),
                    'admins': len(server_group.permissions.get('admins', []))
                }
            }
        return result
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            data = {
                'server_groups': {},
                'global_settings': self.global_settings
            }
            
            for group_id, server_group in self.server_groups.items():
                data['server_groups'][group_id] = {
                    'name': server_group.name,
                    'description': server_group.description,
                    'game_servers': server_group.game_servers,
                    'permissions': server_group.permissions,
                    'allowed_groups': list(server_group.allowed_groups),
                    'features': server_group.features
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info("权限组配置已保存")
        except Exception as e:
            logger.error(f"保存权限组配置失败: {e}")
    
    def _log_operation(self, operation: str, operator_id: str, description: str):
        """记录权限操作日志"""
        if not self.global_settings.get('log_permission_operations', True):
            return
        
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'operator_id': operator_id,
                'description': description
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"记录权限操作日志失败: {e}")


# 全局权限组管理器实例
permission_group_manager = PermissionGroupManager()


def get_permission_group_manager() -> PermissionGroupManager:
    """获取权限组管理器实例"""
    return permission_group_manager


__all__ = [
    'PermissionLevel', 'ServerGroup', 'PermissionGroupManager',
    'permission_group_manager', 'get_permission_group_manager'
]