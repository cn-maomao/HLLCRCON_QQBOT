#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List, Tuple, Optional
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot.permission import SUPERUSER
from loguru import logger

from ..crcon_api import CRCONAPIClient, Player

# 获取配置
from ..config import config

# API配置
CRCON_API_BASE_URL_1 = config.crcon_api_base_url_1
CRCON_API_BASE_URL_2 = config.crcon_api_base_url_2
CRCON_API_TOKEN = config.crcon_api_token

# 管理员指令（需要超级用户权限）
player_list = on_command("玩家列表", aliases={"players", "在线玩家"}, priority=5, permission=SUPERUSER)
admin_kill = on_command("击杀", aliases={"kill", "管理员击杀"}, priority=5, permission=SUPERUSER)
kick_player = on_command("踢出", aliases={"kick"}, priority=5, permission=SUPERUSER)
ban_player = on_command("封禁", aliases={"ban"}, priority=5, permission=SUPERUSER)
switch_now = on_command("立即调边", aliases={"switch", "调边"}, priority=5, permission=SUPERUSER)
switch_death = on_command("死后调边", aliases={"switchdeath"}, priority=5, permission=SUPERUSER)
change_map = on_command("换图", aliases={"changemap", "切换地图"}, priority=5, permission=SUPERUSER)
set_idle_time = on_command("设置闲置时间", aliases={"setidle"}, priority=5, permission=SUPERUSER)
admin_help = on_command("管理帮助", aliases={"adminhelp"}, priority=5, permission=SUPERUSER)

# 常用地图列表
COMMON_MAPS = [
    "carentan_warfare", "foy_warfare", "hill400_warfare", "hurtgenforest_warfare",
    "kursk_warfare", "omahabeach_warfare", "purpleheartlane_warfare", 
    "sainte-mere-eglise_warfare", "stalingrad_warfare", "stmariedumont_warfare",
    "utahbeach_warfare", "driel_warfare", "elalamein_warfare", "kharkov_warfare",
    "mortain_warfare", "remagen_warfare"
]


async def get_api_client(server_num: int = 1) -> CRCONAPIClient:
    """获取API客户端"""
    if server_num == 2:
        base_url = CRCON_API_BASE_URL_2
    else:
        base_url = CRCON_API_BASE_URL_1
    
    return CRCONAPIClient(base_url, CRCON_API_TOKEN)


def parse_range(range_str: str) -> List[int]:
    """解析序号范围，如 1-5 或 1,3,5-7"""
    indices = []
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(part))
    
    return sorted(list(set(indices)))


def format_player_list(players: List[Player]) -> str:
    """格式化玩家列表显示"""
    if not players:
        return "❌ 当前没有在线玩家"
    
    message = f"👥 在线玩家列表 (共 {len(players)} 人)\n"
    message += "=" * 40 + "\n"
    
    allied_players = [p for p in players if p.team == "Allies"]
    axis_players = [p for p in players if p.team == "Axis"]
    
    message += f"🔵 盟军 ({len(allied_players)} 人):\n"
    for i, player in enumerate(allied_players, 1):
        message += f"  {i:2d}. {player.name} (K:{player.kills} D:{player.deaths})\n"
    
    message += f"\n🔴 轴心 ({len(axis_players)} 人):\n"
    for i, player in enumerate(axis_players, len(allied_players) + 1):
        message += f"  {i:2d}. {player.name} (K:{player.kills} D:{player.deaths})\n"
    
    message += f"\n💡 使用序号进行批量操作，如：/击杀 1-5 表示击杀序号1-5的玩家"
    
    return message


@player_list.handle()
async def handle_player_list(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理玩家列表查询"""
    try:
        # 解析服务器编号
        server_num = 1
        arg_text = args.extract_plain_text().strip()
        if arg_text and arg_text.isdigit():
            server_num = int(arg_text)
            if server_num not in [1, 2]:
                await player_list.finish("❌ 服务器编号只能是1或2")
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            message = format_player_list(players)
            await player_list.finish(message)
            
    except Exception as e:
        logger.error(f"获取玩家列表失败: {e}")
        await player_list.finish("❌ 获取玩家列表失败，请稍后重试")


@admin_kill.handle()
async def handle_admin_kill(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理管理员击杀"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await admin_kill.finish("❌ 请输入要击杀的玩家序号\n用法：/击杀 序号 [服务器编号] [原因]")
        
        parts = arg_text.split()
        indices_str = parts[0]
        server_num = 1
        reason = "管理员击杀"
        
        # 解析参数
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await admin_kill.finish("❌ 服务器编号只能是1或2")
            if len(parts) > 2:
                reason = " ".join(parts[2:])
        elif len(parts) > 1:
            reason = " ".join(parts[1:])
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                await admin_kill.finish("❌ 当前没有在线玩家")
            
            # 解析序号范围
            try:
                indices = parse_range(indices_str)
            except ValueError:
                await admin_kill.finish("❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7")
            
            success_count = 0
            failed_players = []
            
            for index in indices:
                if 1 <= index <= len(players):
                    player = players[index - 1]
                    try:
                        success = await client.punish_player(player.player_id, reason)
                        if success:
                            success_count += 1
                        else:
                            failed_players.append(player.name)
                    except Exception as e:
                        failed_players.append(f"{player.name}({e})")
                else:
                    failed_players.append(f"序号{index}(超出范围)")
            
            message = f"⚔️ 管理员击杀执行结果\n"
            message += f"✅ 成功击杀：{success_count} 人\n"
            if failed_players:
                message += f"❌ 失败：{', '.join(failed_players)}"
            
            await admin_kill.finish(message)
            
    except Exception as e:
        logger.error(f"管理员击杀失败: {e}")
        await admin_kill.finish("❌ 管理员击杀失败，请稍后重试")


@kick_player.handle()
async def handle_kick_player(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理踢出玩家"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await kick_player.finish("❌ 请输入要踢出的玩家序号\n用法：/踢出 序号 [服务器编号] [原因]")
        
        parts = arg_text.split()
        indices_str = parts[0]
        server_num = 1
        reason = "违反服务器规则"
        
        # 解析参数
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await kick_player.finish("❌ 服务器编号只能是1或2")
            if len(parts) > 2:
                reason = " ".join(parts[2:])
        elif len(parts) > 1:
            reason = " ".join(parts[1:])
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                await kick_player.finish("❌ 当前没有在线玩家")
            
            # 解析序号范围
            try:
                indices = parse_range(indices_str)
            except ValueError:
                await kick_player.finish("❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7")
            
            success_count = 0
            failed_players = []
            
            for index in indices:
                if 1 <= index <= len(players):
                    player = players[index - 1]
                    try:
                        success = await client.kick_player(player.player_id, reason)
                        if success:
                            success_count += 1
                        else:
                            failed_players.append(player.name)
                    except Exception as e:
                        failed_players.append(f"{player.name}({e})")
                else:
                    failed_players.append(f"序号{index}(超出范围)")
            
            message = f"👢 踢出玩家执行结果\n"
            message += f"✅ 成功踢出：{success_count} 人\n"
            if failed_players:
                message += f"❌ 失败：{', '.join(failed_players)}"
            
            await kick_player.finish(message)
            
    except Exception as e:
        logger.error(f"踢出玩家失败: {e}")
        await kick_player.finish("❌ 踢出玩家失败，请稍后重试")


@ban_player.handle()
async def handle_ban_player(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理封禁玩家"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await ban_player.finish("❌ 请输入封禁参数\n用法：/封禁 序号 时长 [服务器编号] [原因]\n时长：永久 或 小时数")
        
        parts = arg_text.split()
        if len(parts) < 2:
            await ban_player.finish("❌ 参数不足\n用法：/封禁 序号 时长 [服务器编号] [原因]")
        
        indices_str = parts[0]
        duration_str = parts[1]
        server_num = 1
        reason = "违反服务器规则"
        
        # 解析时长
        is_permanent = duration_str in ["永久", "permanent", "perm"]
        duration_hours = 0
        
        if not is_permanent:
            try:
                duration_hours = int(duration_str)
            except ValueError:
                await ban_player.finish("❌ 时长格式错误，请输入数字或'永久'")
        
        # 解析其他参数
        if len(parts) > 2 and parts[2].isdigit():
            server_num = int(parts[2])
            if server_num not in [1, 2]:
                await ban_player.finish("❌ 服务器编号只能是1或2")
            if len(parts) > 3:
                reason = " ".join(parts[3:])
        elif len(parts) > 2:
            reason = " ".join(parts[2:])
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                await ban_player.finish("❌ 当前没有在线玩家")
            
            # 解析序号范围
            try:
                indices = parse_range(indices_str)
            except ValueError:
                await ban_player.finish("❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7")
            
            success_count = 0
            failed_players = []
            
            for index in indices:
                if 1 <= index <= len(players):
                    player = players[index - 1]
                    try:
                        if is_permanent:
                            success = await client.perma_ban_player(player.player_id, reason)
                        else:
                            success = await client.temp_ban_player(player.player_id, duration_hours, reason)
                        
                        if success:
                            success_count += 1
                        else:
                            failed_players.append(player.name)
                    except Exception as e:
                        failed_players.append(f"{player.name}({e})")
                else:
                    failed_players.append(f"序号{index}(超出范围)")
            
            ban_type = "永久封禁" if is_permanent else f"临时封禁({duration_hours}小时)"
            message = f"🚫 {ban_type}执行结果\n"
            message += f"✅ 成功封禁：{success_count} 人\n"
            if failed_players:
                message += f"❌ 失败：{', '.join(failed_players)}"
            
            await ban_player.finish(message)
            
    except Exception as e:
        logger.error(f"封禁玩家失败: {e}")
        await ban_player.finish("❌ 封禁玩家失败，请稍后重试")


@switch_now.handle()
async def handle_switch_now(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理立即调边"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await switch_now.finish("❌ 请输入要调边的玩家序号\n用法：/立即调边 序号 [服务器编号]")
        
        parts = arg_text.split()
        indices_str = parts[0]
        server_num = 1
        
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await switch_now.finish("❌ 服务器编号只能是1或2")
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                await switch_now.finish("❌ 当前没有在线玩家")
            
            # 解析序号范围
            try:
                indices = parse_range(indices_str)
            except ValueError:
                await switch_now.finish("❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7")
            
            success_count = 0
            failed_players = []
            
            for index in indices:
                if 1 <= index <= len(players):
                    player = players[index - 1]
                    try:
                        success = await client.switch_player_now(player.player_id)
                        if success:
                            success_count += 1
                        else:
                            failed_players.append(player.name)
                    except Exception as e:
                        failed_players.append(f"{player.name}({e})")
                else:
                    failed_players.append(f"序号{index}(超出范围)")
            
            message = f"🔄 立即调边执行结果\n"
            message += f"✅ 成功调边：{success_count} 人\n"
            if failed_players:
                message += f"❌ 失败：{', '.join(failed_players)}"
            
            await switch_now.finish(message)
            
    except Exception as e:
        logger.error(f"立即调边失败: {e}")
        await switch_now.finish("❌ 立即调边失败，请稍后重试")


@switch_death.handle()
async def handle_switch_death(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理死后调边"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await switch_death.finish("❌ 请输入要调边的玩家序号\n用法：/死后调边 序号 [服务器编号]")
        
        parts = arg_text.split()
        indices_str = parts[0]
        server_num = 1
        
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await switch_death.finish("❌ 服务器编号只能是1或2")
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                await switch_death.finish("❌ 当前没有在线玩家")
            
            # 解析序号范围
            try:
                indices = parse_range(indices_str)
            except ValueError:
                await switch_death.finish("❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7")
            
            success_count = 0
            failed_players = []
            
            for index in indices:
                if 1 <= index <= len(players):
                    player = players[index - 1]
                    try:
                        success = await client.switch_player_on_death(player.player_id)
                        if success:
                            success_count += 1
                        else:
                            failed_players.append(player.name)
                    except Exception as e:
                        failed_players.append(f"{player.name}({e})")
                else:
                    failed_players.append(f"序号{index}(超出范围)")
            
            message = f"💀 死后调边执行结果\n"
            message += f"✅ 成功设置：{success_count} 人\n"
            if failed_players:
                message += f"❌ 失败：{', '.join(failed_players)}"
            
            await switch_death.finish(message)
            
    except Exception as e:
        logger.error(f"死后调边失败: {e}")
        await switch_death.finish("❌ 死后调边失败，请稍后重试")


@change_map.handle()
async def handle_change_map(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理更换地图"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            # 显示可用地图列表
            message = "🗺️ 常用地图列表：\n"
            for i, map_name in enumerate(COMMON_MAPS, 1):
                message += f"{i:2d}. {map_name}\n"
            message += "\n用法：/换图 地图名称 [服务器编号]"
            await change_map.finish(message)
        
        parts = arg_text.split()
        map_name = parts[0]
        server_num = 1
        
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await change_map.finish("❌ 服务器编号只能是1或2")
        
        # 如果输入的是数字，则从常用地图列表中选择
        if map_name.isdigit():
            map_index = int(map_name)
            if 1 <= map_index <= len(COMMON_MAPS):
                map_name = COMMON_MAPS[map_index - 1]
            else:
                await change_map.finish(f"❌ 地图编号超出范围 (1-{len(COMMON_MAPS)})")
        
        async with await get_api_client(server_num) as client:
            success = await client.set_map(map_name)
            
            if success:
                message = f"✅ 成功更换地图\n"
                message += f"🗺️ 新地图：{map_name}\n"
                message += f"🎮 服务器：{server_num}"
            else:
                message = f"❌ 更换地图失败\n可能原因：地图名称错误或服务器繁忙"
            
            await change_map.finish(message)
            
    except Exception as e:
        logger.error(f"更换地图失败: {e}")
        await change_map.finish("❌ 更换地图失败，请稍后重试")


@set_idle_time.handle()
async def handle_set_idle_time(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理设置闲置踢出时间"""
    try:
        arg_text = args.extract_plain_text().strip()
        if not arg_text:
            await set_idle_time.finish("❌ 请输入闲置时间\n用法：/设置闲置时间 分钟数 [服务器编号]")
        
        parts = arg_text.split()
        try:
            minutes = int(parts[0])
        except ValueError:
            await set_idle_time.finish("❌ 时间格式错误，请输入数字")
        
        server_num = 1
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if server_num not in [1, 2]:
                await set_idle_time.finish("❌ 服务器编号只能是1或2")
        
        if minutes < 0 or minutes > 120:
            await set_idle_time.finish("❌ 闲置时间应在0-120分钟之间")
        
        async with await get_api_client(server_num) as client:
            success = await client.set_idle_autokick_time(minutes)
            
            if success:
                message = f"✅ 成功设置闲置踢出时间\n"
                message += f"⏰ 新时间：{minutes} 分钟\n"
                message += f"🎮 服务器：{server_num}"
            else:
                message = f"❌ 设置闲置时间失败"
            
            await set_idle_time.finish(message)
            
    except Exception as e:
        logger.error(f"设置闲置时间失败: {e}")
        await set_idle_time.finish("❌ 设置闲置时间失败，请稍后重试")


@admin_help.handle()
async def handle_admin_help(bot: Bot, event: Event):
    """处理管理帮助指令"""
    message = "🛡️ CRCON管理机器人 - 管理功能\n"
    message += "=" * 40 + "\n"
    message += "👥 玩家管理：\n"
    message += "  /玩家列表 [服务器编号] - 查看在线玩家\n"
    message += "  /击杀 序号 [服务器编号] [原因] - 管理员击杀\n"
    message += "  /踢出 序号 [服务器编号] [原因] - 踢出玩家\n"
    message += "  /封禁 序号 时长 [服务器编号] [原因] - 封禁玩家\n"
    message += "  /立即调边 序号 [服务器编号] - 立即调边\n"
    message += "  /死后调边 序号 [服务器编号] - 死后调边\n\n"
    message += "🗺️ 地图管理：\n"
    message += "  /换图 [地图名称/编号] [服务器编号] - 更换地图\n\n"
    message += "⚙️ 服务器设置：\n"
    message += "  /设置闲置时间 分钟数 [服务器编号] - 设置闲置踢出时间\n\n"
    message += "📝 说明：\n"
    message += "  • 序号支持范围：1-5 或 1,3,5-7\n"
    message += "  • 封禁时长：数字(小时) 或 '永久'\n"
    message += "  • 服务器编号：1或2，默认为1\n"
    message += "  • 所有管理功能需要超级用户权限\n\n"
    message += "💡 示例：\n"
    message += "  /玩家列表 1\n"
    message += "  /击杀 1-5 1 违规行为\n"
    message += "  /封禁 3 24 1 恶意破坏\n"
    message += "  /换图 foy_warfare 2"
    
    await admin_help.finish(message)