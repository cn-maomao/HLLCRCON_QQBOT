#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List, Optional
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from loguru import logger

from ..crcon_api import CRCONAPIClient, GameState, VipInfo

# 获取配置
from ..config import config

# API配置
CRCON_API_BASE_URL_1 = config.crcon_api_base_url_1
CRCON_API_BASE_URL_2 = config.crcon_api_base_url_2
CRCON_API_TOKEN = config.crcon_api_token

# 注册指令
server_info = on_command("服务器信息", aliases={"服务器状态", "server", "status"}, priority=5)
vip_check = on_command("查询vip", aliases={"vip查询", "checkvip"}, priority=5)
help_cmd = on_command("帮助", aliases={"help", "指令"}, priority=5)


def format_time(seconds: int) -> str:
    """格式化时间显示"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


async def get_api_client(server_num: int = 1) -> CRCONAPIClient:
    """获取API客户端"""
    if server_num == 2:
        base_url = CRCON_API_BASE_URL_2
    else:
        base_url = CRCON_API_BASE_URL_1
    
    return CRCONAPIClient(base_url, CRCON_API_TOKEN)


@server_info.handle()
async def handle_server_info(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理服务器信息查询"""
    try:
        # 解析服务器编号
        server_num = 1
        arg_text = args.extract_plain_text().strip()
        if arg_text and arg_text.isdigit():
            server_num = int(arg_text)
            if server_num not in [1, 2]:
                await server_info.finish("❌ 服务器编号只能是1或2")
        
        async with await get_api_client(server_num) as client:
            # 获取游戏状态
            gamestate = await client.get_gamestate()
            
            # 构建消息
            message = f"🎮 服务器 {server_num} 状态信息\n"
            message += "=" * 30 + "\n"
            message += f"📊 当前比分：\n"
            message += f"  🔵 盟军：{gamestate.allied_score} 分 ({gamestate.allied_players} 人)\n"
            message += f"  🔴 轴心：{gamestate.axis_score} 分 ({gamestate.axis_players} 人)\n"
            message += f"👥 总人数：{gamestate.allied_players + gamestate.axis_players} 人\n"
            message += f"⏰ 剩余时间：{gamestate.remaining_time}\n"
            message += f"🗺️ 当前地图：{gamestate.current_map}\n"
            message += f"➡️ 下一张地图：{gamestate.next_map}"
            
            await server_info.finish(message)
            
    except Exception as e:
        logger.error(f"查询服务器信息失败: {e}")
        await server_info.finish("❌ 查询服务器信息失败，请稍后重试")


@vip_check.handle()
async def handle_vip_check(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理VIP状态查询"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await vip_check.finish("❌ 请输入要查询的玩家名称\n用法：/查询vip 玩家名称 [服务器编号]")
        
        # 解析参数
        parts = arg_text.split()
        player_name = parts[0]
        server_num = 1
        
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await vip_check.finish("❌ 服务器编号只能是1或2")
        
        async with await get_api_client(server_num) as client:
            # 获取VIP列表
            vip_list = await client.get_vip_ids()
            
            # 查找指定玩家
            found_vip = None
            for vip in vip_list:
                if player_name.lower() in vip.name.lower():
                    found_vip = vip
                    break
            
            if found_vip:
                message = f"✅ 玩家 {found_vip.name} 的VIP状态\n"
                message += "=" * 30 + "\n"
                message += f"👤 玩家名称：{found_vip.name}\n"
                message += f"🆔 玩家ID：{found_vip.player_id}\n"
                message += f"💎 VIP状态：有效\n"
                
                if found_vip.expiration:
                    message += f"⏰ 到期时间：{found_vip.expiration}\n"
                else:
                    message += f"⏰ 到期时间：永久\n"
                
                if found_vip.description:
                    message += f"📝 备注：{found_vip.description}"
            else:
                message = f"❌ 未找到玩家 {player_name} 的VIP信息\n"
                message += f"该玩家可能：\n"
                message += f"1. 不是VIP用户\n"
                message += f"2. 玩家名称输入错误\n"
                message += f"3. 不在服务器 {server_num} 中"
            
            await vip_check.finish(message)
            
    except Exception as e:
        logger.error(f"查询VIP状态失败: {e}")
        await vip_check.finish("❌ 查询VIP状态失败，请稍后重试")


@help_cmd.handle()
async def handle_help(bot: Bot, event: Event):
    """处理帮助指令"""
    message = "🤖 CRCON管理机器人 - 玩家功能\n"
    message += "=" * 35 + "\n"
    message += "📊 服务器信息查询：\n"
    message += "  /服务器信息 [服务器编号]\n"
    message += "  /server [1|2]\n"
    message += "  /status [1|2]\n\n"
    message += "💎 VIP状态查询：\n"
    message += "  /查询vip 玩家名称 [服务器编号]\n"
    message += "  /vip查询 玩家名称 [服务器编号]\n"
    message += "  /checkvip 玩家名称 [服务器编号]\n\n"
    message += "📝 说明：\n"
    message += "  • 服务器编号：1或2，默认为1\n"
    message += "  • 玩家名称支持模糊匹配\n"
    message += "  • 所有指令都支持别名\n\n"
    message += "💡 示例：\n"
    message += "  /服务器信息 1\n"
    message += "  /查询vip PlayerName 2"
    
    await help_cmd.finish(message)