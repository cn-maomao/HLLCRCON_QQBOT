#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Any
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from loguru import logger

from ..config import config, get_all_servers, multi_server_manager, is_admin_user

# 注册命令
server_list_cmd = on_command("服务器列表", aliases={"服务器", "servers", "serverlist"}, priority=5)
server_info_cmd = on_command("服务器详情", aliases={"服务器信息", "serverinfo"}, priority=5)
reload_config_cmd = on_command("重载配置", aliases={"reload", "reloadconfig"}, priority=5)

@server_list_cmd.handle()
async def handle_server_list(bot: Bot, event: Event):
    """处理服务器列表查询"""
    try:
        servers = get_all_servers()
        
        if not servers:
            await server_list_cmd.finish("❌ 没有可用的服务器")
        
        # 创建转发消息
        forward_messages = []
        
        # 添加标题
        title_msg = f"🎮 可用服务器列表 ({len(servers)}个)"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": title_msg
            }
        })
        
        # 添加服务器信息
        for i, server in enumerate(servers, 1):
            server_msg = f"🔸 服务器 {i}\n"
            server_msg += f"📋 ID: {server['id']}\n"
            server_msg += f"🏷️ 名称: {server['name']}\n"
            server_msg += f"🎯 显示名: {server['display_name']}\n"
            server_msg += f"📝 描述: {server['description']}\n"
            server_msg += f"📊 状态: {server.get('status', '正常')}"
            
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": "CRCON机器人",
                    "uin": str(bot.self_id),
                    "content": server_msg
                }
            })
        
        # 添加使用说明
        usage_msg = "💡 使用说明:\n"
        usage_msg += "• 可以使用服务器ID、名称或显示名来指定服务器\n"
        usage_msg += "• 例如: 查服 1 或 查服 AAA\n"
        usage_msg += "• 支持的别名请参考上述列表"
        
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
        logger.error(f"查询服务器列表失败: {e}")
        await server_list_cmd.finish("❌ 查询服务器列表失败，请稍后重试")

@server_info_cmd.handle()
async def handle_server_info(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理服务器详情查询"""
    try:
        # 解析参数
        args_text = args.extract_plain_text().strip()
        if not args_text:
            await server_info_cmd.finish("❌ 请指定服务器ID或名称\n用法: 服务器详情 <服务器ID/名称>")
        
        # 检查是否使用多服务器管理器
        if not multi_server_manager:
            await server_info_cmd.finish("❌ 多服务器管理功能未启用")
        
        # 获取服务器配置
        group_id = str(event.group_id) if hasattr(event, 'group_id') else None
        server_config = multi_server_manager.get_server_config(args_text, group_id)
        if not server_config:
            await server_info_cmd.finish(f"❌ 未找到服务器: {args_text}")
        
        # 构建详细信息
        info_msg = f"🎮 服务器详细信息\n"
        info_msg += "=" * 30 + "\n"
        info_msg += f"🆔 服务器ID: {server_config.server_id}\n"
        info_msg += f"🏷️ 服务器名称: {server_config.name}\n"
        info_msg += f"🎯 显示名称: {server_config.display_name}\n"
        info_msg += f"📝 描述: {server_config.description}\n"
        info_msg += f"🌐 API地址: {server_config.api_base_url}\n"
        info_msg += f"👥 最大玩家数: {server_config.max_players}\n"
        info_msg += f"🌍 地区: {server_config.region}\n"
        info_msg += f"🕐 时区: {server_config.timezone}\n"
        info_msg += f"✅ 启用状态: {'是' if server_config.enabled else '否'}\n"
        info_msg += f"🔧 维护模式: {'是' if server_config.maintenance_mode else '否'}\n"
        
        # 添加自定义参数
        if server_config.custom_params:
            info_msg += "\n🔧 自定义参数:\n"
            for key, value in server_config.custom_params.items():
                info_msg += f"  • {key}: {value}\n"
        
        await server_info_cmd.finish(info_msg)
        
    except Exception as e:
        logger.error(f"查询服务器详情失败: {e}")
        await server_info_cmd.finish("❌ 查询服务器详情失败，请稍后重试")

@reload_config_cmd.handle()
async def handle_reload_config(bot: Bot, event: Event):
    """处理配置重载"""
    try:
        # 检查权限
        user_id = str(event.user_id)
        group_id = str(event.group_id) if hasattr(event, 'group_id') else None
        if not is_admin_user(user_id, group_id):
            await reload_config_cmd.finish("❌ 权限不足，需要管理员权限")
        
        # 检查是否使用多服务器管理器
        if not multi_server_manager:
            await reload_config_cmd.finish("❌ 多服务器管理功能未启用")
        
        # 重载配置
        success = multi_server_manager.reload_config()
        
        if success:
            servers = get_all_servers()
            msg = f"✅ 配置重载成功\n"
            msg += f"📊 当前可用服务器: {len(servers)}个\n"
            msg += f"🕐 重载时间: {multi_server_manager.global_settings.health_check_interval}分钟间隔"
            await reload_config_cmd.finish(msg)
        else:
            await reload_config_cmd.finish("❌ 配置重载失败，请检查配置文件格式")
        
    except Exception as e:
        logger.error(f"重载配置失败: {e}")
        await reload_config_cmd.finish("❌ 重载配置失败，请稍后重试")