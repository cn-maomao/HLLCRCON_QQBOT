#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限组管理命令插件
提供权限组的查询、管理和配置功能
"""

from typing import List, Optional
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, Message, GroupMessageEvent
from nonebot.params import CommandArg
from loguru import logger

from ..permission_groups import (
    PermissionLevel, 
    get_permission_group_manager
)
from ..config import is_admin_user

# 注册命令
permission_groups_cmd = on_command("权限组列表", aliases={"权限组", "服务器组列表", "服务器组"}, priority=5)
permission_info_cmd = on_command("权限组详情", aliases={"服务器组详情", "权限详情"}, priority=5)
add_permission_cmd = on_command("添加权限", aliases={"添加管理员", "授权"}, priority=5)
remove_permission_cmd = on_command("移除权限", aliases={"移除管理员", "取消授权"}, priority=5)
my_permission_cmd = on_command("我的权限", aliases={"权限查询", "查看权限"}, priority=5)
reload_permission_cmd = on_command("重载权限配置", aliases={"刷新权限", "重载权限"}, priority=5)


@permission_groups_cmd.handle()
async def handle_permission_groups(bot: Bot, event: Event):
    """处理权限组列表查询"""
    try:
        manager = get_permission_group_manager()
        groups = manager.list_groups()
        
        if not groups:
            await permission_groups_cmd.finish("❌ 未配置任何权限组")
        
        # 创建转发消息节点列表
        forward_messages = []
        
        # 添加标题消息
        title_msg = "🔐 权限组列表"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": title_msg
            }
        })
        
        # 添加每个权限组的信息
        for group_id, group_info in groups.items():
            group_msg = f"📋 {group_info['name']} ({group_id})\n"
            group_msg += f"📝 描述：{group_info['description']}\n"
            group_msg += f"🖥️ 服务器数量：{group_info['servers_count']}\n"
            group_msg += f"👑 主人：{group_info['users_count']['owners']} 人\n"
            group_msg += f"⭐ 超级管理员：{group_info['users_count']['super_admins']} 人\n"
            group_msg += f"🛡️ 普通管理员：{group_info['users_count']['admins']} 人"
            
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": "CRCON机器人",
                    "uin": str(bot.self_id),
                    "content": group_msg
                }
            })
        
        # 添加使用说明
        usage_msg = "💡 使用说明：\n"
        usage_msg += "/权限组详情 [组ID] - 查看详细信息\n"
        usage_msg += "/我的权限 - 查看自己的权限\n"
        usage_msg += "/添加权限 [QQ号] [组ID] [权限级别] - 添加权限（需要管理员权限）\n"
        usage_msg += "/移除权限 [QQ号] [组ID] - 移除权限（需要管理员权限）"
        
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": usage_msg
            }
        })
        
        # 发送转发消息
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=forward_messages)
        
    except Exception as e:
        logger.error(f"查询权限组列表失败: {e}")
        await permission_groups_cmd.finish("❌ 查询权限组列表失败，请稍后重试")


@permission_info_cmd.handle()
async def handle_permission_info(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理权限组详情查询"""
    try:
        args_text = args.extract_plain_text().strip()
        if not args_text:
            await permission_info_cmd.finish("❌ 请指定权限组ID\n使用方法：/权限组详情 [组ID]")
        
        manager = get_permission_group_manager()
        server_group = manager.get_server_group(args_text)
        
        if not server_group:
            await permission_info_cmd.finish(f"❌ 权限组 '{args_text}' 不存在")
        
        # 构建详细信息
        message = f"🔐 权限组详情：{server_group.name}\n"
        message += "=" * 30 + "\n"
        message += f"📝 描述：{server_group.description}\n"
        message += f"🆔 组ID：{args_text}\n\n"
        
        # 服务器信息
        enabled_servers = server_group.get_enabled_servers()
        message += f"🖥️ 绑定服务器 ({len(enabled_servers)} 个)：\n"
        for server in enabled_servers:
            message += f"  • {server['name']} (ID: {server['server_id']})\n"
        
        # 权限用户信息
        message += f"\n👥 权限用户：\n"
        owners = server_group.permissions.get('owners', [])
        super_admins = server_group.permissions.get('super_admins', [])
        admins = server_group.permissions.get('admins', [])
        
        if owners:
            message += f"👑 主人 ({len(owners)} 人)：{', '.join(owners)}\n"
        if super_admins:
            message += f"⭐ 超级管理员 ({len(super_admins)} 人)：{', '.join(super_admins)}\n"
        if admins:
            message += f"🛡️ 普通管理员 ({len(admins)} 人)：{', '.join(admins)}\n"
        
        # 功能权限
        message += f"\n🔧 功能权限：\n"
        features = server_group.features
        feature_names = {
            'allow_kick': '踢人',
            'allow_ban': '封禁',
            'allow_map_change': '换图',
            'allow_player_list': '玩家列表',
            'allow_server_management': '服务器管理'
        }
        
        for feature_key, feature_name in feature_names.items():
            status = "✅" if features.get(feature_key, False) else "❌"
            message += f"  {status} {feature_name}\n"
        
        # 允许的QQ群
        if server_group.allowed_groups:
            message += f"\n💬 允许的QQ群：{', '.join(server_group.allowed_groups)}"
        
        await permission_info_cmd.finish(message)
        
    except Exception as e:
        logger.error(f"查询权限组详情失败: {e}")
        await permission_info_cmd.finish("❌ 查询权限组详情失败，请稍后重试")


@add_permission_cmd.handle()
async def handle_add_permission(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理添加权限命令"""
    try:
        # 检查是否为管理员
        if not is_admin_user(str(event.user_id)):
            await add_permission_cmd.finish("❌ 权限不足，只有管理员可以执行此操作")
        
        args_text = args.extract_plain_text().strip()
        parts = args_text.split()
        
        if len(parts) < 3:
            await add_permission_cmd.finish(
                "❌ 参数不足\n使用方法：/添加权限 [QQ号] [组ID] [权限级别]\n"
                "权限级别：owner(主人)、super_admin(超级管理员)、admin(普通管理员)"
            )
        
        target_user = parts[0]
        group_id = parts[1]
        level_str = parts[2].lower()
        
        # 验证权限级别
        level_map = {
            'owner': PermissionLevel.OWNER,
            'super_admin': PermissionLevel.SUPER_ADMIN,
            'admin': PermissionLevel.ADMIN
        }
        
        if level_str not in level_map:
            await add_permission_cmd.finish(
                "❌ 无效的权限级别\n"
                "可用级别：owner(主人)、super_admin(超级管理员)、admin(普通管理员)"
            )
        
        level = level_map[level_str]
        manager = get_permission_group_manager()
        
        success, message = manager.add_user_to_group(
            target_user, group_id, level, str(event.user_id)
        )
        
        if success:
            await add_permission_cmd.finish(f"✅ {message}")
        else:
            await add_permission_cmd.finish(f"❌ {message}")
        
    except Exception as e:
        logger.error(f"添加权限失败: {e}")
        await add_permission_cmd.finish("❌ 添加权限失败，请稍后重试")


@remove_permission_cmd.handle()
async def handle_remove_permission(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理移除权限命令"""
    try:
        # 检查是否为管理员
        if not is_admin_user(str(event.user_id)):
            await remove_permission_cmd.finish("❌ 权限不足，只有管理员可以执行此操作")
        
        args_text = args.extract_plain_text().strip()
        parts = args_text.split()
        
        if len(parts) < 2:
            await remove_permission_cmd.finish(
                "❌ 参数不足\n使用方法：/移除权限 [QQ号] [组ID]"
            )
        
        target_user = parts[0]
        group_id = parts[1]
        
        manager = get_permission_group_manager()
        
        success, message = manager.remove_user_from_group(
            target_user, group_id, str(event.user_id)
        )
        
        if success:
            await remove_permission_cmd.finish(f"✅ {message}")
        else:
            await remove_permission_cmd.finish(f"❌ {message}")
        
    except Exception as e:
        logger.error(f"移除权限失败: {e}")
        await remove_permission_cmd.finish("❌ 移除权限失败，请稍后重试")


@my_permission_cmd.handle()
async def handle_my_permission(bot: Bot, event: Event):
    """处理查看我的权限命令"""
    try:
        user_id = str(event.user_id)
        manager = get_permission_group_manager()
        
        # 获取用户在所有组中的权限
        user_permissions = {}
        for group_id, server_group in manager.server_groups.items():
            level = server_group.get_user_permission(user_id)
            if level != PermissionLevel.USER:
                user_permissions[group_id] = {
                    'name': server_group.name,
                    'level': level,
                    'features': []
                }
                
                # 检查功能权限
                features = ['allow_kick', 'allow_ban', 'allow_map_change', 'allow_player_list', 'allow_server_management']
                for feature in features:
                    if server_group.has_feature_permission(user_id, feature):
                        user_permissions[group_id]['features'].append(feature)
        
        if not user_permissions:
            await my_permission_cmd.finish("ℹ️ 您在所有权限组中都是普通用户权限")
        
        # 构建权限信息
        message = f"🔐 您的权限信息 (QQ: {user_id})\n"
        message += "=" * 30 + "\n"
        
        level_names = {
            PermissionLevel.OWNER: "👑 主人",
            PermissionLevel.SUPER_ADMIN: "⭐ 超级管理员",
            PermissionLevel.ADMIN: "🛡️ 普通管理员"
        }
        
        feature_names = {
            'allow_kick': '踢人',
            'allow_ban': '封禁',
            'allow_map_change': '换图',
            'allow_player_list': '玩家列表',
            'allow_server_management': '服务器管理'
        }
        
        for group_id, perm_info in user_permissions.items():
            message += f"📋 {perm_info['name']} ({group_id})\n"
            message += f"  权限级别：{level_names[perm_info['level']]}\n"
            
            if perm_info['features']:
                feature_list = [feature_names.get(f, f) for f in perm_info['features']]
                message += f"  可用功能：{', '.join(feature_list)}\n"
            
            message += "\n"
        
        await my_permission_cmd.finish(message.strip())
        
    except Exception as e:
        logger.error(f"查询用户权限失败: {e}")
        await my_permission_cmd.finish("❌ 查询权限信息失败，请稍后重试")


@reload_permission_cmd.handle()
async def handle_reload_permission(bot: Bot, event: Event):
    """处理重载权限配置命令"""
    try:
        # 检查是否为管理员
        if not is_admin_user(str(event.user_id)):
            await reload_permission_cmd.finish("❌ 权限不足，只有管理员可以执行此操作")
        
        manager = get_permission_group_manager()
        manager.reload_config()
        
        groups_count = len(manager.server_groups)
        await reload_permission_cmd.finish(f"✅ 权限配置已重新加载，共加载 {groups_count} 个权限组")
        
    except Exception as e:
        logger.error(f"重载权限配置失败: {e}")
        await reload_permission_cmd.finish("❌ 重载权限配置失败，请稍后重试")