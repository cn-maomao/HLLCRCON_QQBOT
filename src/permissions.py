#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限管理模块
实现三级权限系统：主人、超级管理员、普通管理员
"""

from typing import List, Set, Optional
from enum import Enum
import json
import os
from pathlib import Path

from nonebot import logger
from nonebot.permission import Permission
from nonebot.adapters import Event
from nonebot.internal.matcher import Matcher

from .config import config


class PermissionLevel(Enum):
    """权限级别枚举"""
    OWNER = "owner"              # 主人
    SUPER_ADMIN = "super_admin"  # 超级管理员
    ADMIN = "admin"              # 普通管理员
    USER = "user"                # 普通用户


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.data_file = Path("data/permissions.json")
        self.data_file.parent.mkdir(exist_ok=True)
        self._load_permissions()
    
    def _load_permissions(self):
        """加载权限数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.owners: Set[str] = set(data.get('owners', []))
                    self.super_admins: Set[str] = set(data.get('super_admins', []))
                    self.admins: Set[str] = set(data.get('admins', []))
            else:
                # 初始化默认权限
                self.owners: Set[str] = set(config.superusers)  # 将现有超级用户设为主人
                self.super_admins: Set[str] = set()
                self.admins: Set[str] = set()
                self._save_permissions()
        except Exception as e:
            logger.error(f"加载权限数据失败: {e}")
            # 使用默认权限
            self.owners: Set[str] = set(config.superusers)
            self.super_admins: Set[str] = set()
            self.admins: Set[str] = set()
    
    def _save_permissions(self):
        """保存权限数据"""
        try:
            data = {
                'owners': list(self.owners),
                'super_admins': list(self.super_admins),
                'admins': list(self.admins)
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存权限数据失败: {e}")
    
    def get_user_permission(self, user_id: str) -> PermissionLevel:
        """获取用户权限级别"""
        if user_id in self.owners:
            return PermissionLevel.OWNER
        elif user_id in self.super_admins:
            return PermissionLevel.SUPER_ADMIN
        elif user_id in self.admins:
            return PermissionLevel.ADMIN
        else:
            return PermissionLevel.USER
    
    def has_permission(self, user_id: str, required_level: PermissionLevel) -> bool:
        """检查用户是否具有指定权限级别"""
        user_level = self.get_user_permission(user_id)
        
        # 权限级别优先级：OWNER > SUPER_ADMIN > ADMIN > USER
        level_priority = {
            PermissionLevel.OWNER: 4,
            PermissionLevel.SUPER_ADMIN: 3,
            PermissionLevel.ADMIN: 2,
            PermissionLevel.USER: 1
        }
        
        return level_priority[user_level] >= level_priority[required_level]
    
    def add_admin(self, user_id: str, operator_id: str) -> tuple[bool, str]:
        """添加普通管理员"""
        # 检查操作者权限
        if not self.has_permission(operator_id, PermissionLevel.SUPER_ADMIN):
            return False, "权限不足，需要超级管理员或主人权限"
        
        # 检查目标用户当前权限
        current_level = self.get_user_permission(user_id)
        if current_level != PermissionLevel.USER:
            return False, f"用户已具有 {current_level.value} 权限"
        
        self.admins.add(user_id)
        self._save_permissions()
        return True, "成功添加普通管理员"
    
    def remove_admin(self, user_id: str, operator_id: str) -> tuple[bool, str]:
        """删除普通管理员"""
        # 检查操作者权限
        if not self.has_permission(operator_id, PermissionLevel.SUPER_ADMIN):
            return False, "权限不足，需要超级管理员或主人权限"
        
        # 检查目标用户是否为普通管理员
        if user_id not in self.admins:
            return False, "用户不是普通管理员"
        
        self.admins.remove(user_id)
        self._save_permissions()
        return True, "成功删除普通管理员"
    
    def add_super_admin(self, user_id: str, operator_id: str) -> tuple[bool, str]:
        """添加超级管理员"""
        # 只有主人可以添加超级管理员
        if not self.has_permission(operator_id, PermissionLevel.OWNER):
            return False, "权限不足，需要主人权限"
        
        # 检查目标用户当前权限
        current_level = self.get_user_permission(user_id)
        if current_level in [PermissionLevel.SUPER_ADMIN, PermissionLevel.OWNER]:
            return False, f"用户已具有 {current_level.value} 权限"
        
        # 如果是普通管理员，先移除
        if user_id in self.admins:
            self.admins.remove(user_id)
        
        self.super_admins.add(user_id)
        self._save_permissions()
        return True, "成功添加超级管理员"
    
    def remove_super_admin(self, user_id: str, operator_id: str) -> tuple[bool, str]:
        """删除超级管理员"""
        # 只有主人可以删除超级管理员
        if not self.has_permission(operator_id, PermissionLevel.OWNER):
            return False, "权限不足，需要主人权限"
        
        # 检查目标用户是否为超级管理员
        if user_id not in self.super_admins:
            return False, "用户不是超级管理员"
        
        self.super_admins.remove(user_id)
        self._save_permissions()
        return True, "成功删除超级管理员"
    
    def list_users_by_level(self, level: PermissionLevel) -> List[str]:
        """获取指定权限级别的用户列表"""
        if level == PermissionLevel.OWNER:
            return list(self.owners)
        elif level == PermissionLevel.SUPER_ADMIN:
            return list(self.super_admins)
        elif level == PermissionLevel.ADMIN:
            return list(self.admins)
        else:
            return []
    
    def get_all_permissions(self) -> dict:
        """获取所有权限信息"""
        return {
            'owners': list(self.owners),
            'super_admins': list(self.super_admins),
            'admins': list(self.admins)
        }


# 全局权限管理器实例
permission_manager = PermissionManager()


# 权限检查函数
def check_permission(level: PermissionLevel):
    """权限检查装饰器工厂"""
    async def _check(event: Event) -> bool:
        user_id = str(event.get_user_id())
        
        # 首先检查全局权限系统
        if permission_manager.has_permission(user_id, level):
            return True
        
        # 如果全局权限不足，再检查群权限系统
        if hasattr(event, 'group_id'):
            group_id = str(event.group_id)
            from .permission_groups import get_permission_group_manager
            manager = get_permission_group_manager()
            server_group = manager.get_group_for_qq_group(group_id)
            if server_group:
                return server_group.has_permission(user_id, level)
        
        return False
    
    return Permission(_check)


def check_permission_for_group(level: PermissionLevel, qq_group_id: str):
    """基于QQ群的权限检查装饰器工厂"""
    async def _check(event: Event) -> bool:
        user_id = str(event.get_user_id())
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.has_permission(user_id, level)
        
        # 回退到旧权限系统
        return permission_manager.has_permission(user_id, level)
    
    return Permission(_check)


# 预定义权限
OWNER = check_permission(PermissionLevel.OWNER)
SUPER_ADMIN = check_permission(PermissionLevel.SUPER_ADMIN)
ADMIN = check_permission(PermissionLevel.ADMIN)

# 兼容性权限（保持向后兼容）
SUPERUSER = ADMIN  # 原来的SUPERUSER权限映射到ADMIN


# 权限检查辅助函数
def is_owner(user_id: str, qq_group_id: Optional[str] = None) -> bool:
    """检查用户是否为主人"""
    if qq_group_id:
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.has_permission(user_id, PermissionLevel.OWNER)
    
    return permission_manager.has_permission(user_id, PermissionLevel.OWNER)


def is_super_admin(user_id: str, qq_group_id: Optional[str] = None) -> bool:
    """检查用户是否为超级管理员或更高权限"""
    if qq_group_id:
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.has_permission(user_id, PermissionLevel.SUPER_ADMIN)
    
    return permission_manager.has_permission(user_id, PermissionLevel.SUPER_ADMIN)


def is_admin(user_id: str, qq_group_id: Optional[str] = None) -> bool:
    """检查用户是否为管理员或更高权限"""
    if qq_group_id:
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.has_permission(user_id, PermissionLevel.ADMIN)
    
    return permission_manager.has_permission(user_id, PermissionLevel.ADMIN)


def has_feature_permission(user_id: str, feature: str, qq_group_id: Optional[str] = None) -> bool:
    """检查用户是否有特定功能权限"""
    if qq_group_id:
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.has_feature_permission(user_id, feature)
    
    # 旧系统默认管理员有所有功能权限
    return is_admin(user_id)


def get_user_permission_level(user_id: str, qq_group_id: Optional[str] = None) -> PermissionLevel:
    """获取用户权限级别"""
    if qq_group_id:
        from .permission_groups import get_permission_group_manager
        manager = get_permission_group_manager()
        server_group = manager.get_group_for_qq_group(qq_group_id)
        if server_group:
            return server_group.get_user_permission(user_id)
    
    return permission_manager.get_user_permission(user_id)


def get_permission_level_name(level: PermissionLevel) -> str:
    """获取权限级别的中文名称"""
    names = {
        PermissionLevel.OWNER: "主人",
        PermissionLevel.SUPER_ADMIN: "超级管理员",
        PermissionLevel.ADMIN: "普通管理员",
        PermissionLevel.USER: "普通用户"
    }
    return names.get(level, "未知")


# 导出
__all__ = [
    "PermissionLevel", "PermissionManager", "permission_manager",
    "OWNER", "SUPER_ADMIN", "ADMIN", "SUPERUSER",
    "is_owner", "is_super_admin", "is_admin",
    "has_feature_permission", "get_user_permission_level",
    "get_permission_level_name", "check_permission", "check_permission_for_group"
]