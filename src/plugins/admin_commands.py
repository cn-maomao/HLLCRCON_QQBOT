#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List, Tuple, Optional
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from loguru import logger

from ..crcon_api import CRCONAPIClient, Player, VipInfo

# 尝试导入新权限系统，如果失败则使用旧的SUPERUSER
try:
    from ..permissions import ADMIN, SUPER_ADMIN, OWNER
    # 为了向后兼容，将ADMIN权限作为默认管理员权限
    DEFAULT_ADMIN_PERMISSION = ADMIN
except ImportError:
    from nonebot.permission import SUPERUSER
    DEFAULT_ADMIN_PERMISSION = SUPERUSER
    logger.warning("新权限系统未找到，使用传统SUPERUSER权限")

from ..config import config

# API配置
CRCON_API_BASE_URL_1 = config.crcon_api_base_url_1
CRCON_API_BASE_URL_2 = config.crcon_api_base_url_2
CRCON_API_BASE_URL_3 = config.crcon_api_base_url_3
CRCON_API_TOKEN = config.crcon_api_token


def create_forward_message(bot: Bot, title: str, content_sections: List[Tuple[str, str]]) -> List[dict]:
    """
    创建转发消息格式
    
    Args:
        bot: Bot实例
        title: 转发消息标题
        content_sections: 内容段落列表，每个元素为(发送者名称, 消息内容)的元组
        
    Returns:
        转发消息节点列表
    """
    nodes = []
    
    # 添加标题节点
    title_node = {
        "type": "node",
        "data": {
            "name": "CRCON机器人",
            "uin": str(bot.self_id),
            "content": title
        }
    }
    nodes.append(title_node)
    
    # 添加内容节点
    for sender_name, content in content_sections:
        content_node = {
            "type": "node",
            "data": {
                "name": sender_name,
                "uin": str(bot.self_id),
                "content": content
            }
        }
        nodes.append(content_node)
    
    return nodes


async def send_forward_message(bot: Bot, event: Event, nodes: List[dict], fallback_message: str = None):
    """
    发送转发消息，失败时回退到普通消息
    
    Args:
        bot: Bot实例
        event: 事件对象
        nodes: 转发消息节点列表
        fallback_message: 回退消息内容，如果为None则使用节点内容拼接
    """
    try:
        # 尝试发送转发消息
        group_id = event.group_id if hasattr(event, 'group_id') else None
        if group_id:
            await bot.call_api("send_group_forward_msg", group_id=group_id, messages=nodes)
        else:
            await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=nodes)
    except Exception as e:
        logger.error(f"发送转发消息失败: {e}")
        # 回退到普通消息
        if fallback_message is None:
            # 从节点中提取内容拼接成普通消息
            contents = []
            for node in nodes:
                if node.get("type") == "node" and "data" in node:
                    contents.append(node["data"]["content"])
            fallback_message = "\n\n".join(contents)
        
        # 发送普通消息
        await bot.send(event, fallback_message)


def parse_player_indices(indices_str: str) -> List[int]:
    """
    解析玩家序号字符串，支持单个序号、逗号分隔的多个序号和范围
    
    Args:
        indices_str: 序号字符串，如 "1", "1,3,5", "1-5", "1,3-5,7"
        
    Returns:
        List[int]: 解析后的序号列表
        
    Raises:
        ValueError: 序号格式错误时抛出异常
    """
    indices = []
    
    # 按逗号分割
    parts = indices_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if '-' in part:
            # 处理范围，如 "1-5"
            try:
                start, end = part.split('-', 1)
                start = int(start.strip())
                end = int(end.strip())
                
                if start > end:
                    raise ValueError(f"范围起始值({start})不能大于结束值({end})")
                if start < 1:
                    raise ValueError(f"序号不能小于1")
                if end > 100:
                    raise ValueError(f"序号不能大于100")
                    
                indices.extend(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"无效的范围格式: {part}")
                raise
        else:
            # 处理单个序号
            try:
                index = int(part)
                if index < 1:
                    raise ValueError(f"序号不能小于1")
                if index > 100:
                    raise ValueError(f"序号不能大于100")
                indices.append(index)
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"无效的序号: {part}")
                raise
    
    if not indices:
        raise ValueError("未提供有效的序号")
    
    # 去重并排序
    return sorted(list(set(indices)))


# 管理员指令（需要管理员权限）
player_list = on_command("管理员玩家列表", aliases={"adminplayers", "管理玩家"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
admin_kill = on_command("击杀", aliases={"kill", "管理员击杀"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
kick_player = on_command("踢出", aliases={"kick"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
ban_player = on_command("封禁", aliases={"ban"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
switch_now = on_command("立即调边", aliases={"switch", "调边"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
switch_death = on_command("死后调边", aliases={"switchdeath"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
change_map = on_command("换图", aliases={"changemap", "切换地图"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
set_idle_time = on_command("设置闲置时间", aliases={"setidle"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
admin_help = on_command("管理帮助", aliases={"adminhelp"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)

# VIP管理指令
vip_query = on_command("VIP查询", aliases={"vipquery", "查询VIP"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
vip_add = on_command("添加VIP", aliases={"addvip", "VIP添加"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
vip_remove = on_command("删除VIP", aliases={"removevip", "VIP删除"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)

# 地图管理指令
map_objectives = on_command("地图点位", aliases={"objectives", "点位状态"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
set_objectives = on_command("设置点位", aliases={"setobjectives", "点位设置"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
map_list = on_command("地图列表", aliases={"maplist", "地图编号"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)

# 服务器设置指令
server_settings = on_command("服务器设置", aliases={"serversettings", "设置查看"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
set_autobalance = on_command("设置自动平衡", aliases={"setautobalance", "自动平衡"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
set_switch_cooldown = on_command("设置调边冷却", aliases={"setswitchcooldown", "调边冷却"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)

# 消息管理指令
private_message = on_command("私信玩家", aliases={"私信", "发消息"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)
broadcast_message = on_command("全体私信", aliases={"广播消息", "全体消息"}, priority=5, permission=DEFAULT_ADMIN_PERMISSION)

# 常用地图列表 - 基于实际服务器轮换更新
COMMON_MAPS = [
    # 当前服务器轮换中的地图（warfare模式）
    "carentan_warfare",
    "driel_warfare", 
    "foy_warfare",
    "kharkov_warfare",
    "kursk_warfare",
    "omahabeach_warfare",
    "PHL_L_1944_Warfare",
    "remagen_warfare",
    "stmereeglise_warfare",
    "stmariedumont_warfare",
    # 常用的offensive模式地图
    "stmereeglise_offensive_ger",
    "stmereeglise_offensive_us",
    "utahbeach_offensive_ger",
    "utahbeach_offensive_us",
    "driel_offensive_ger", 
    "driel_offensive_us",
    "omahabeach_offensive_ger",
    "omahabeach_offensive_us",
    "kharkov_offensive_ger",
    "kharkov_offensive_us",
    "carentan_offensive_ger",
    "carentan_offensive_us",
    "stalingrad_offensive_ger",
    "stalingrad_offensive_us",
    "kharkov_offensive_ger",
    "kharkov_offensive_us",
    "kharkov_warfare",
    "carentan_offensive_ger",
    "carentan_offensive_us",
    "carentan_warfare",
    "kursk_offensive_ger",
    "kursk_offensive_us",
    "kursk_warfare",
    "foy_offensive_ger",
    "foy_offensive_us",
    "foy_warfare",
]


async def get_api_client(server_num: int = 1) -> CRCONAPIClient:
    """获取API客户端"""
    if server_num == 2:
        base_url = CRCON_API_BASE_URL_2
    elif server_num == 3:
        base_url = CRCON_API_BASE_URL_3
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
            if server_num not in [1, 2, 3]:
                await player_list.finish("❌ 服务器编号只能是1、2或3")
        
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            message = format_player_list(players)
            await player_list.finish(message)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await admin_kill.finish("❌ 服务器编号只能是1、2或3")
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await kick_player.finish("❌ 服务器编号只能是1、2或3")
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await ban_player.finish("❌ 服务器编号只能是1、2或3")
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await switch_now.finish("❌ 服务器编号只能是1、2或3")
        
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await switch_death.finish("❌ 服务器编号只能是1、2或3")
        
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await change_map.finish("❌ 服务器编号只能是1、2或3")
        
        # 如果输入的是数字，则从常用地图列表中选择
        if map_name.isdigit():
            map_index = int(map_name)
            if 1 <= map_index <= len(COMMON_MAPS):
                map_name = COMMON_MAPS[map_index - 1]
            else:
                await change_map.finish(f"❌ 地图编号超出范围 (1-{len(COMMON_MAPS)})")
        
        async with await get_api_client(server_num) as client:
            # 添加调试日志
            logger.info(f"尝试更换地图: {map_name} (服务器{server_num})")
            success = await client.set_map(map_name)
            
            if success:
                message = f"✅ 地图切换命令已执行\n"
                message += f"🗺️ 目标地图：{map_name}\n"
                message += f"🎮 服务器：{server_num}\n"
                message += f"⏰ 预计1分钟后生效"
            else:
                message = f"❌ 更换地图失败\n"
                message += f"🗺️ 尝试的地图：{map_name}\n"
                message += f"🎮 服务器：{server_num}\n"
                message += f"可能原因：地图名称错误或服务器繁忙"
            
            await change_map.finish(message)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
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
            if server_num not in [1, 2, 3]:
                await set_idle_time.finish("❌ 服务器编号只能是1、2或3")
        
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
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"设置闲置时间失败: {e}")
        await set_idle_time.finish("❌ 设置闲置时间失败，请稍后重试")


@admin_help.handle()
async def handle_admin_help(bot: Bot, event: Event):
    """处理管理帮助指令"""
    try:
        # 构建转发消息内容段落
        content_sections = [
            ("CRCON机器人", "🛡️ CRCON管理机器人 - 管理功能"),
            ("玩家管理", "👥 玩家管理：\n  /管理员玩家列表 [服务器编号] - 查看在线玩家（管理版）\n  /击杀 序号 [服务器编号] [原因] - 管理员击杀\n  /踢出 序号 [服务器编号] [原因] - 踢出玩家\n  /封禁 序号 时长 [服务器编号] [原因] - 封禁玩家\n  /立即调边 序号 [服务器编号] - 立即调边\n  /死后调边 序号 [服务器编号] - 死后调边"),
            ("地图管理", "🗺️ 地图管理：\n  /换图 [地图名称/编号] [服务器编号] - 更换地图\n  /地图点位 [服务器编号] - 查看当前地图点位控制情况\n  /设置点位 点位配置 [服务器编号] - 设置地图点位位置"),
            ("服务器设置", "⚙️ 服务器设置：\n  /设置闲置时间 分钟数 [服务器编号] - 设置闲置踢出时间\n  /服务器设置 [服务器编号] - 查看服务器设置状态\n  /设置自动平衡 启用/禁用 [阈值] [服务器编号] - 设置自动人数平衡\n  /设置调边冷却 分钟数 [服务器编号] - 设置调边冷却时间"),
            ("VIP管理", "👑 VIP管理：\n  /VIP查询 玩家ID [服务器编号] - 查询VIP信息\n  /添加VIP 玩家ID [时长] [服务器编号] [描述] - 添加VIP\n  /删除VIP 玩家ID [服务器编号] - 删除VIP"),
            ("使用说明", "📝 说明：\n  • 序号支持范围：1-5 或 1,3,5-7\n  • 封禁时长：数字(小时) 或 '永久'\n  • VIP时长：数字(小时) 或 '永久'，默认永久\n  • 点位配置：下中上中下 (上=第一个点位, 中=中间点位, 下=最后一个点位) 或 12321 (1=第一个点位, 2=中间点位, 3=最后一个点位)\n  • 服务器编号：1、2或3，默认为1；VIP支持'全部'同时操作三个服务器\n  • 所有管理功能需要管理员权限"),
            ("使用示例", "💡 示例：\n  /管理员玩家列表 1\n  /击杀 1-5 1 违规行为\n  /封禁 3 24 1 恶意破坏\n  /换图 foy_warfare 2\n  /设置闲置时间 15 1\n  /地图点位 1\n  /设置点位 下中上中下 1\n  /服务器设置 1\n  /设置自动平衡 启用 2 1\n  /VIP查询 76561198123456789 1\n  /添加VIP 76561198123456789 72 全部 赞助用户\n  /删除VIP 76561198123456789 全部")
        ]
        
        # 创建转发消息
        nodes = create_forward_message(bot, "🛡️ CRCON管理机器人 - 管理功能", content_sections)
        
        # 发送转发消息
        await send_forward_message(bot, event, nodes)
        
    except Exception as e:
        logger.error(f"发送管理帮助失败: {e}")
        # 回退到原始消息格式
        message = "🛡️ CRCON管理机器人 - 管理功能\n"
        message += "=" * 40 + "\n"
        message += "👥 玩家管理：\n"
        message += "  /管理员玩家列表 [服务器编号] - 查看在线玩家（管理版）\n"
        message += "  /击杀 序号 [服务器编号] [原因] - 管理员击杀\n"
        message += "  /踢出 序号 [服务器编号] [原因] - 踢出玩家\n"
        message += "  /封禁 序号 时长 [服务器编号] [原因] - 封禁玩家\n"
        message += "  /立即调边 序号 [服务器编号] - 立即调边\n"
        message += "  /死后调边 序号 [服务器编号] - 死后调边\n\n"
        message += "🗺️ 地图管理：\n"
        message += "  /换图 [地图名称/编号] [服务器编号] - 更换地图\n"
        message += "  /地图点位 [服务器编号] - 查看当前地图点位控制情况\n"
        message += "  /设置点位 点位配置 [服务器编号] - 设置地图点位位置\n\n"
        message += "⚙️ 服务器设置：\n"
        message += "  /设置闲置时间 分钟数 [服务器编号] - 设置闲置踢出时间\n"
        message += "  /服务器设置 [服务器编号] - 查看服务器设置状态\n"
        message += "  /设置自动平衡 启用/禁用 [阈值] [服务器编号] - 设置自动人数平衡\n"
        message += "  /设置调边冷却 分钟数 [服务器编号] - 设置调边冷却时间\n\n"
        message += "👑 VIP管理：\n"
        message += "  /VIP查询 玩家ID [服务器编号] - 查询VIP信息\n"
        message += "  /添加VIP 玩家ID [时长] [服务器编号] [描述] - 添加VIP\n"
        message += "  /删除VIP 玩家ID [服务器编号] - 删除VIP\n\n"
        message += "📝 说明：\n"
        message += "  • 序号支持范围：1-5 或 1,3,5-7\n"
        message += "  • 封禁时长：数字(小时) 或 '永久'\n"
        message += "  • VIP时长：数字(小时) 或 '永久'，默认永久\n"
        message += "  • 点位配置：下中上中下 (上=第一个点位, 中=中间点位, 下=最后一个点位) 或 12321 (1=第一个点位, 2=中间点位, 3=最后一个点位)\n"
        message += "  • 服务器编号：1、2或3，默认为1；VIP支持'全部'同时操作三个服务器\n"
        message += "  • 所有管理功能需要管理员权限\n\n"
        message += "💡 示例：\n"
        message += "  /管理员玩家列表 1\n"
        message += "  /击杀 1-5 1 违规行为\n"
        message += "  /封禁 3 24 1 恶意破坏\n"
        message += "  /换图 foy_warfare 2\n"
        message += "  /设置闲置时间 15 1\n"
        message += "  /地图点位 1\n"
        message += "  /设置点位 下中上中下 1\n"
        message += "  /服务器设置 1\n"
        message += "  /设置自动平衡 启用 2 1\n"
        message += "  /VIP查询 76561198123456789 1\n"
        message += "  /添加VIP 76561198123456789 72 全部 赞助用户\n"
        message += "  /删除VIP 76561198123456789 全部"
        
        await admin_help.finish(message)


@vip_query.handle()
async def handle_vip_query(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理VIP查询指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await vip_query.finish("❌ 请提供玩家ID\n用法：/VIP查询 玩家ID [服务器编号]")
        
        parts = arg_text.split()
        player_id = parts[0]
        server_num = int(parts[1]) if len(parts) > 1 else 1
        
        if server_num not in [1, 2, 3]:
                await vip_query.finish("❌ 服务器编号只能是1、2或3")
        
        # 获取API客户端并使用异步上下文管理器
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 查询VIP信息
            vip_list = await api_client.get_vip_ids()
        
        # 查找指定玩家的VIP信息
        player_vip = None
        for vip in vip_list:
            if vip.player_id == player_id:
                player_vip = vip
                break
        
        if not player_vip:
            await vip_query.finish(f"❌ 玩家 {player_id} 不是VIP用户")
        
        # 格式化VIP信息
        message = f"👑 VIP信息查询结果\n"
        message += "=" * 30 + "\n"
        message += f"🆔 玩家ID: {player_vip.player_id}\n"
        message += f"👤 玩家名称: {player_vip.name}\n"
        message += f"📝 描述: {player_vip.description or '无'}\n"
        
        if player_vip.expiration:
            message += f"⏰ 到期时间: {player_vip.expiration}\n"
        else:
            message += f"⏰ VIP类型: 永久VIP\n"
        
        message += f"🖥️ 服务器: {server_num}号服务器"
        
        await vip_query.finish(message)
        
    except ValueError:
        await vip_query.finish("❌ 服务器编号必须是数字")
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"VIP查询失败: {e}")
        await vip_query.finish("❌ VIP查询失败，请稍后重试")


@vip_add.handle()
async def handle_vip_add(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理添加VIP指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await vip_add.finish("❌ 请提供完整参数\n用法：/添加VIP 玩家ID [时长] [服务器编号] [描述]\n时长：数字(小时) 或 '永久'，默认永久")
        
        parts = arg_text.split(maxsplit=3)
        player_id = parts[0]
        
        # 解析时长
        duration = None
        server_nums = [1]  # 默认服务器1
        description = "管理员添加"
        
        if len(parts) > 1:
            # 检查第二个参数是否为时长
            if parts[1].isdigit() or parts[1] == "永久":
                if parts[1] != "永久":
                    duration = int(parts[1])
                
                # 检查第三个参数是否为服务器编号
                if len(parts) > 2:
                    if parts[2] in ["1", "2", "3", "1,2", "2,1", "1,3", "3,1", "2,3", "3,2", "1,2,3", "全部"]:
                        if parts[2] == "全部" or "," in parts[2]:
                            if parts[2] == "全部":
                                server_nums = [1, 2, 3]
                            else:
                                server_nums = [int(x) for x in parts[2].split(",")]
                        else:
                            server_nums = [int(parts[2])]
                        
                        # 第四个参数为描述
                        if len(parts) > 3:
                            description = parts[3]
                    else:
                        # 第三个参数为描述
                        description = parts[2]
            else:
                # 第二个参数不是时长，检查是否为服务器编号
                if parts[1] in ["1", "2", "3", "1,2", "2,1", "1,3", "3,1", "2,3", "3,2", "1,2,3", "全部"]:
                    if parts[1] == "全部" or "," in parts[1]:
                        if parts[1] == "全部":
                            server_nums = [1, 2, 3]
                        else:
                            server_nums = [int(x) for x in parts[1].split(",")]
                    else:
                        server_nums = [int(parts[1])]
                    
                    # 第三个参数为描述
                    if len(parts) > 2:
                        description = parts[2]
                else:
                    # 第二个参数为描述
                    description = parts[1]
        
        # 执行添加VIP操作
        success_servers = []
        failed_servers = []
        
        for server_num in server_nums:
            try:
                api_client = await get_api_client(server_num)
                
                async with api_client:
                    # 构建到期时间
                    expiration = None
                    if duration:
                        from datetime import datetime, timedelta
                        expiration = (datetime.now() + timedelta(hours=duration)).isoformat()
                    
                    # 添加VIP
                    await api_client.add_vip(player_id, description, expiration)
                    success_servers.append(server_num)
                
            except Exception as e:
                logger.error(f"服务器{server_num}添加VIP失败: {e}")
                failed_servers.append(server_num)
        
        # 构建结果消息
        message = f"👑 VIP添加操作结果\n"
        message += "=" * 30 + "\n"
        message += f"🆔 玩家ID: {player_id}\n"
        message += f"📝 描述: {description}\n"
        
        if duration:
            message += f"⏰ VIP时长: {duration}小时\n"
        else:
            message += f"⏰ VIP类型: 永久VIP\n"
        
        if success_servers:
            message += f"✅ 成功添加到服务器: {', '.join(map(str, success_servers))}\n"
        
        if failed_servers:
            message += f"❌ 添加失败的服务器: {', '.join(map(str, failed_servers))}\n"
        
        await vip_add.finish(message)
        
    except ValueError as e:
        await vip_add.finish(f"❌ 参数错误: {e}")
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"添加VIP失败: {e}")
        await vip_add.finish("❌ 添加VIP失败，请稍后重试")


@vip_remove.handle()
async def handle_vip_remove(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理删除VIP指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await vip_remove.finish("❌ 请提供玩家ID\n用法：/删除VIP 玩家ID [服务器编号]\n服务器编号：1、2、3、全部，默认为1")
        
        parts = arg_text.split()
        player_id = parts[0]
        
        # 解析服务器编号
        server_nums = [1]  # 默认服务器1
        if len(parts) > 1:
            if parts[1] in ["1", "2", "3"]:
                server_nums = [int(parts[1])]
            elif parts[1] in ["1,2", "2,1", "1,3", "3,1", "2,3", "3,2", "1,2,3", "全部"]:
                if parts[1] == "全部":
                    server_nums = [1, 2, 3]
                else:
                    server_nums = [int(x) for x in parts[1].split(",")]
            else:
                await vip_remove.finish("❌ 服务器编号只能是1、2、3或全部")
        
        # 执行删除VIP操作
        success_servers = []
        failed_servers = []
        not_found_servers = []
        
        for server_num in server_nums:
            try:
                api_client = await get_api_client(server_num)
                
                async with api_client:
                    # 先查询VIP是否存在
                    vip_list = await api_client.get_vip_ids()
                    player_vip = None
                    for vip in vip_list:
                        if vip.player_id == player_id:
                            player_vip = vip
                            break
                    
                    if not player_vip:
                        not_found_servers.append(server_num)
                        continue
                    
                    # 删除VIP
                    await api_client.remove_vip(player_id)
                    success_servers.append(server_num)
                
            except Exception as e:
                logger.error(f"服务器{server_num}删除VIP失败: {e}")
                failed_servers.append(server_num)
        
        # 构建结果消息
        message = f"👑 VIP删除操作结果\n"
        message += "=" * 30 + "\n"
        message += f"🆔 玩家ID: {player_id}\n"
        
        if success_servers:
            message += f"✅ 成功删除的服务器: {', '.join(map(str, success_servers))}\n"
        
        if not_found_servers:
            message += f"ℹ️ 未找到VIP的服务器: {', '.join(map(str, not_found_servers))}\n"
        
        if failed_servers:
            message += f"❌ 删除失败的服务器: {', '.join(map(str, failed_servers))}\n"
        
        if not success_servers and not not_found_servers and not failed_servers:
            message += "❌ 未执行任何操作"
        
        await vip_remove.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"删除VIP失败: {e}")
        await vip_remove.finish("❌ 删除VIP失败，请稍后重试")


@map_objectives.handle()
async def handle_map_objectives(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理地图点位查询指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        server_num = 1
        
        if arg_text:
            try:
                server_num = int(arg_text)
                if server_num not in [1, 2, 3]:
                    await map_objectives.finish("❌ 服务器编号只能是1、2或3")
            except ValueError:
                await map_objectives.finish("❌ 服务器编号必须是数字")
        
        # 获取API客户端
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 获取游戏状态和点位得分
            gamestate = await api_client.get_gamestate()
            objective_scores = await api_client.get_team_objective_scores()
        
        # 构建消息
        message = f"🗺️ 地图点位状态\n"
        message += "=" * 30 + "\n"
        message += f"🖥️ 服务器: {server_num}号服务器\n"
        
        # 显示当前地图
        if gamestate and gamestate.current_map:
            from ..maplist import MapList
            if isinstance(gamestate.current_map, dict):
                map_id = gamestate.current_map.get('map', {}).get('id', '') or gamestate.current_map.get('id', '')
                game_mode = gamestate.current_map.get('game_mode', '')
                
                # 解析地图名称
                map_name = MapList.parse_map_name(map_id)
                if game_mode == "offensive":
                    map_name += " · 攻防"
                elif game_mode == "warfare":
                    map_name += " · 冲突"
                elif game_mode == "skirmish":
                    map_name += " · 遭遇战"
                
                message += f"🗺️ 当前地图: {map_name}\n"
            else:
                map_name = MapList.parse_map_name(str(gamestate.current_map))
                message += f"🗺️ 当前地图: {map_name}\n"
        else:
            message += f"🗺️ 当前地图: 未知\n"
        
        # 显示队伍得分
        if gamestate:
            message += f"🔵 盟军得分: {gamestate.allied_score}\n"
            message += f"🔴 轴心得分: {gamestate.axis_score}\n"
        
        # 显示点位控制情况
        allied_objectives, axis_objectives = objective_scores
        total_objectives = allied_objectives + axis_objectives
        
        message += f"\n📍 点位控制情况:\n"
        message += f"🔵 盟军控制: {allied_objectives} 个点位\n"
        message += f"🔴 轴心控制: {axis_objectives} 个点位\n"
        message += f"📊 总点位数: {total_objectives} 个\n"
        
        if total_objectives > 0:
            allied_percentage = (allied_objectives / total_objectives) * 100
            axis_percentage = (axis_objectives / total_objectives) * 100
            message += f"📈 控制比例: 盟军 {allied_percentage:.1f}% | 轴心 {axis_percentage:.1f}%"
        
        await map_objectives.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询地图点位失败: {e}")
        await map_objectives.finish("❌ 查询地图点位失败，请稍后重试")


@server_settings.handle()
async def handle_server_settings(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理服务器设置查询指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        server_num = 1
        
        if arg_text:
            try:
                server_num = int(arg_text)
                if server_num not in [1, 2, 3]:
                    await server_settings.finish("❌ 服务器编号只能是1、2或3")
            except ValueError:
                await server_settings.finish("❌ 服务器编号必须是数字")
        
        # 获取API客户端并使用异步上下文管理器
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 获取各项设置
            idle_time = await api_client.get_idle_autokick_time()
            autobalance_enabled = await api_client.get_autobalance_enabled()
            autobalance_threshold = await api_client.get_autobalance_threshold()
            switch_cooldown = await api_client.get_team_switch_cooldown()
        
        # 构建消息
        message = f"⚙️ 服务器设置状态\n"
        message += "=" * 30 + "\n"
        message += f"🖥️ 服务器: {server_num}号服务器\n\n"
        
        message += f"⏰ 闲置踢出时间: {idle_time} 分钟\n"
        message += f"⚖️ 自动人数平衡: {'✅ 启用' if autobalance_enabled else '❌ 禁用'}\n"
        message += f"📊 自动平衡阈值: {autobalance_threshold} 人\n"
        message += f"🔄 调边冷却时间: {switch_cooldown} 分钟\n\n"
        
        message += f"💡 修改设置命令:\n"
        message += f"  /设置闲置时间 分钟数 [服务器编号]\n"
        message += f"  /设置自动平衡 启用/禁用 [阈值] [服务器编号]\n"
        message += f"  /设置调边冷却 分钟数 [服务器编号]"
        
        await server_settings.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询服务器设置失败: {e}")
        await server_settings.finish("❌ 查询服务器设置失败，请稍后重试")


@set_autobalance.handle()
async def handle_set_autobalance(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理设置自动平衡指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await set_autobalance.finish("❌ 请提供完整参数\n用法：/设置自动平衡 启用/禁用 [阈值] [服务器编号]")
        
        parts = arg_text.split()
        
        # 解析启用/禁用状态
        if parts[0] in ["启用", "开启", "true", "1", "on", "enable"]:
            enabled = True
        elif parts[0] in ["禁用", "关闭", "false", "0", "off", "disable"]:
            enabled = False
        else:
            await set_autobalance.finish("❌ 第一个参数必须是 启用/禁用")
        
        # 解析阈值和服务器编号
        threshold = None
        server_num = 1
        
        if len(parts) > 1:
            # 检查第二个参数是否为数字（阈值）
            if parts[1].isdigit():
                threshold = int(parts[1])
                # 第三个参数为服务器编号
                if len(parts) > 2:
                    try:
                        server_num = int(parts[2])
                        if server_num not in [1, 2, 3]:
                            await set_autobalance.finish("❌ 服务器编号只能是1、2或3")
                    except ValueError:
                        await set_autobalance.finish("❌ 服务器编号必须是数字")
            else:
                # 第二个参数为服务器编号
                try:
                    server_num = int(parts[1])
                    if server_num not in [1, 2, 3]:
                        await set_autobalance.finish("❌ 服务器编号只能是1、2或3")
                except ValueError:
                    await set_autobalance.finish("❌ 服务器编号必须是数字")
        
        # 获取API客户端
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 设置自动平衡状态
            success = await api_client.set_autobalance_enabled(enabled)
            
            if not success:
                await set_autobalance.finish("❌ 设置自动平衡状态失败")
            
            # 如果提供了阈值，也设置阈值
            threshold_success = True
            if threshold is not None:
                threshold_success = await api_client.set_autobalance_threshold(threshold)
        
        # 构建结果消息
        message = f"⚖️ 自动平衡设置结果\n"
        message += "=" * 30 + "\n"
        message += f"🖥️ 服务器: {server_num}号服务器\n"
        message += f"✅ 自动平衡: {'启用' if enabled else '禁用'}\n"
        
        if threshold is not None:
            if threshold_success:
                message += f"✅ 平衡阈值: {threshold} 人\n"
            else:
                message += f"❌ 平衡阈值设置失败\n"
        
        await set_autobalance.finish(message)
        
    except ValueError as e:
        await set_autobalance.finish(f"❌ 参数错误: {e}")
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"设置自动平衡失败: {e}")
        await set_autobalance.finish("❌ 设置自动平衡失败，请稍后重试")


@set_switch_cooldown.handle()
async def handle_set_switch_cooldown(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理设置调边冷却指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await set_switch_cooldown.finish("❌ 请提供冷却时间\n用法：/设置调边冷却 分钟数 [服务器编号]")
        
        parts = arg_text.split()
        
        # 解析冷却时间
        try:
            cooldown_minutes = int(parts[0])
            if cooldown_minutes < 0:
                await set_switch_cooldown.finish("❌ 冷却时间不能为负数")
        except ValueError:
            await set_switch_cooldown.finish("❌ 冷却时间必须是数字")
        
        # 解析服务器编号
        server_num = 1
        if len(parts) > 1:
            try:
                server_num = int(parts[1])
                if server_num not in [1, 2, 3]:
                    await set_switch_cooldown.finish("❌ 服务器编号只能是1、2或3")
            except ValueError:
                await set_switch_cooldown.finish("❌ 服务器编号必须是数字")
        
        # 获取API客户端
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 设置调边冷却时间
            success = await api_client.set_team_switch_cooldown(cooldown_minutes)
        
        if success:
            message = f"🔄 调边冷却设置成功\n"
            message += "=" * 30 + "\n"
            message += f"🖥️ 服务器: {server_num}号服务器\n"
            message += f"✅ 冷却时间: {cooldown_minutes} 分钟"
            
            await set_switch_cooldown.finish(message)
        else:
            await set_switch_cooldown.finish("❌ 设置调边冷却时间失败")
            
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"设置调边冷却失败: {e}")
        await set_switch_cooldown.finish("❌ 设置调边冷却失败，请稍后重试")


@set_objectives.handle()
async def handle_set_objectives(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理设置地图点位指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await set_objectives.finish("❌ 请提供点位设置\n用法：/设置点位 点位配置 [服务器编号]\n示例：/设置点位 上上中上上 1")
        
        parts = arg_text.split()
        
        # 解析点位配置
        objective_config = parts[0]
        
        # 解析服务器编号
        server_num = 1
        if len(parts) > 1:
            try:
                server_num = int(parts[1])
                if server_num not in [1, 2, 3]:
                    await set_objectives.finish("❌ 服务器编号只能是1、2或3")
            except ValueError:
                await set_objectives.finish("❌ 服务器编号必须是数字")
        
        # 获取API客户端
        api_client = await get_api_client(server_num)
        
        async with api_client:
            # 获取当前地图的点位行信息
            objective_rows = await api_client.get_objective_rows()
            
            if not objective_rows:
                await set_objectives.finish("❌ 无法获取当前地图的点位信息")
            
            # 解析点位配置字符串
            objectives = parse_objective_config(objective_config, objective_rows)
            
            if objectives is None:
                await set_objectives.finish("❌ 点位配置格式错误\n支持的格式：\n- 下中上中下 (上=第一个点位, 中=中间点位, 下=最后一个点位)\n- 12321 (1=第一个点位, 2=中间点位, 3=最后一个点位)")
            
            # 设置地图点位
            success = await api_client.set_game_layout(objectives)
        
        if success:
            # 构建结果消息
            message = f"🗺️ 点位设置成功\n"
            message += "=" * 30 + "\n"
            message += f"🖥️ 服务器: {server_num}号服务器\n"
            message += f"📍 点位配置: {objective_config}\n\n"
            
            # 显示详细的点位设置
            message += "📋 详细设置:\n"
            for i, objective_name in enumerate(objectives):
                row_objectives = objective_rows[i]
                position_desc = ""
                
                if objective_name == row_objectives[0]:
                    position_desc = "上位置"
                elif len(row_objectives) > 1 and objective_name == row_objectives[-1]:
                    position_desc = "下位置"
                elif len(row_objectives) > 1:
                    position_desc = "中位置"
                else:
                    position_desc = "唯一位置"
                
                message += f"第{i+1}行: {objective_name} ({position_desc})\n"
                message += f"  可选点位: {' | '.join(row_objectives)}\n"
            
            await set_objectives.finish(message)
        else:
            await set_objectives.finish("❌ 设置点位失败，请检查权限或稍后重试")
            
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"设置地图点位失败: {e}")
        await set_objectives.finish("❌ 设置地图点位失败，请稍后重试")


def parse_objective_config(config: str, objective_rows: List[List[str]]) -> Optional[List[str]]:
    """
    解析点位位置配置字符串
    
    Args:
        config: 点位位置配置字符串，如 "下中上中下"
        objective_rows: 当前地图的点位行信息
        
    Returns:
        点位位置设置列表，每个元素是点位名称，None表示解析失败
    """
    try:
        objectives = []
        
        # 确保配置长度与点位行数匹配
        if len(config) != len(objective_rows):
            return None
        
        for i, char in enumerate(config):
            # 获取当前行的点位列表
            row_objectives = objective_rows[i]
            
            if char in ["上", "1"]:
                # 选择该行的第一个点位（上位置）
                if len(row_objectives) > 0:
                    objectives.append(row_objectives[0])
                else:
                    return None
            elif char in ["中", "2"]:
                # 选择该行的中间点位（中位置）
                if len(row_objectives) > 1:
                    middle_index = len(row_objectives) // 2
                    objectives.append(row_objectives[middle_index])
                elif len(row_objectives) == 1:
                    objectives.append(row_objectives[0])
                else:
                    return None
            elif char in ["下", "3"]:
                # 选择该行的最后一个点位（下位置）
                if len(row_objectives) > 0:
                    objectives.append(row_objectives[-1])
                else:
                    return None
            else:
                # 无效字符
                return None
        
        return objectives
        
    except Exception:
        return None


@map_list.handle()
async def handle_map_list(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理地图列表查询"""
    try:
        arg_text = args.extract_plain_text().strip()
        server_num = 1
        
        # 解析服务器编号
        if arg_text and arg_text.isdigit():
            server_num = int(arg_text)
            if server_num not in [1, 2, 3]:
                await map_list.finish("❌ 服务器编号只能是1、2或3")
        
        async with await get_api_client(server_num) as api_client:
            # 获取服务器地图轮换列表
            rotation_maps = await api_client.get_map_rotation()
            
            # 构建转发消息内容段落
            content_sections = []
            
            # 添加标题
            content_sections.append(("CRCON机器人", f"🗺️ 服务器{server_num} 地图轮换列表"))
            
            # 构建轮换地图列表
            if rotation_maps:
                rotation_content = "📋 当前轮换地图：\n"
                for i, map_data in enumerate(rotation_maps, 1):
                    # 使用MapList解析地图名称
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                        from maplist import MapList
                        
                        # 处理不同格式的地图数据
                        if isinstance(map_data, dict):
                            # 如果是字典，提取地图ID
                            map_name = map_data.get('id', '') or map_data.get('name', '') or str(map_data)
                        else:
                            # 如果是字符串，直接使用
                            map_name = str(map_data)
                        
                        chinese_name = MapList.parse_map_name(map_name)
                        rotation_content += f"{i:2d}. {chinese_name} ({map_name})\n"
                    except Exception as e:
                        logger.error(f"解析地图名称出错: {e}")
                        # 显示原始数据作为备选
                        display_name = str(map_data)
                        rotation_content += f"{i:2d}. {display_name}\n"
                
                content_sections.append(("地图轮换", rotation_content.strip()))
            
            # 构建常用地图列表
            common_maps_content = "🎯 常用地图编号（换图时可直接使用编号）：\n"
            for i, map_name in enumerate(COMMON_MAPS, 1):
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from maplist import MapList
                    chinese_name = MapList.parse_map_name(map_name)
                    common_maps_content += f"{i:2d}. {chinese_name} ({map_name})\n"
                except Exception as e:
                    common_maps_content += f"{i:2d}. {map_name}\n"
            
            content_sections.append(("常用地图", common_maps_content.strip()))
            
            # 添加使用说明
            usage_content = "💡 使用方法：\n"
            usage_content += "• /换图 编号 [服务器] - 使用编号换图\n"
            usage_content += "• /换图 地图名 [服务器] - 使用地图名换图\n"
            usage_content += f"• 示例：/换图 1 {server_num} 或 /换图 {COMMON_MAPS[0]} {server_num}"
            
            content_sections.append(("使用说明", usage_content))
            
            # 创建转发消息
            nodes = create_forward_message(bot, f"🗺️ 服务器{server_num} 地图信息", content_sections)
            
            # 发送转发消息
            await send_forward_message(bot, event, nodes)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"获取地图列表失败: {e}")
        await map_list.finish("❌ 获取地图列表失败，请稍后重试")


@private_message.handle()
async def handle_private_message(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理私信玩家指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await private_message.finish("❌ 请提供参数\n用法：/私信玩家 玩家序号 消息内容 [服务器编号]")
        
        parts = arg_text.split(maxsplit=2)
        if len(parts) < 2:
            await private_message.finish("❌ 参数不足\n用法：/私信玩家 玩家序号 消息内容 [服务器编号]")
        
        # 解析参数
        player_indices_str = parts[0]
        message_content = parts[1]
        server_num = 1
        
        # 检查是否有第三个参数（服务器编号）
        if len(parts) > 2:
            try:
                server_num = int(parts[2])
                if server_num not in [1, 2, 3]:
                    await private_message.finish("❌ 服务器编号只能是1、2或3")
            except ValueError:
                # 如果第三个参数不是数字，可能是消息内容的一部分
                message_content = f"{message_content} {parts[2]}"
        
        # 解析玩家序号
        try:
            player_indices = parse_player_indices(player_indices_str)
        except ValueError as e:
            await private_message.finish(f"❌ 玩家序号格式错误：{e}")
        
        # 获取API客户端和玩家列表
        api_client = await get_api_client(server_num)
        
        async with api_client:
            players = await api_client.get_players()
        
        if not players:
            await private_message.finish(f"❌ 服务器{server_num}当前没有玩家在线")
        
        # 发送私信
        success_count = 0
        failed_players = []
        
        for index in player_indices:
            if 1 <= index <= len(players):
                player = players[index - 1]
                try:
                    async with api_client:
                        success = await api_client.message_player(player.player_id, message_content)
                    
                    if success:
                        success_count += 1
                    else:
                        failed_players.append(f"{index}({player.name})")
                except Exception as e:
                    logger.error(f"发送私信给玩家 {player.name} 失败: {e}")
                    failed_players.append(f"{index}({player.name})")
            else:
                failed_players.append(f"{index}(序号无效)")
        
        # 构建结果消息
        message = f"💬 私信发送结果\n"
        message += "=" * 30 + "\n"
        message += f"📝 消息内容：{message_content}\n"
        message += f"🎮 服务器：{server_num}\n"
        message += f"✅ 成功发送：{success_count} 人\n"
        if failed_players:
            message += f"❌ 发送失败：{', '.join(failed_players)}"
        
        await private_message.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"发送私信失败: {e}")
        await private_message.finish("❌ 发送私信失败，请稍后重试")


@broadcast_message.handle()
async def handle_broadcast_message(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理全体私信指令"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        if not arg_text:
            await broadcast_message.finish("❌ 请提供消息内容\n用法：/全体私信 消息内容 [服务器编号]")
        
        parts = arg_text.rsplit(maxsplit=1)
        message_content = parts[0]
        server_num = 1
        
        # 检查最后一个参数是否为服务器编号
        if len(parts) > 1 and parts[1].isdigit():
            potential_server = int(parts[1])
            if potential_server in [1, 2, 3]:
                server_num = potential_server
                message_content = parts[0]
            else:
                # 不是有效的服务器编号，当作消息内容的一部分
                message_content = arg_text
        else:
            message_content = arg_text
        
        # 获取API客户端和玩家列表
        api_client = await get_api_client(server_num)
        
        async with api_client:
            players = await api_client.get_players()
        
        if not players:
            await broadcast_message.finish(f"❌ 服务器{server_num}当前没有玩家在线")
        
        # 检查玩家数量限制
        if len(players) > 100:
            await broadcast_message.finish(f"❌ 当前在线玩家数量({len(players)})超过限制(100人)，请稍后重试")
        
        # 发送全体私信
        success_count = 0
        failed_players = []
        
        for i, player in enumerate(players, 1):
            try:
                async with api_client:
                    success = await api_client.message_player(player.player_id, message_content)
                
                if success:
                    success_count += 1
                else:
                    failed_players.append(f"{i}({player.name})")
            except Exception as e:
                logger.error(f"发送私信给玩家 {player.name} 失败: {e}")
                failed_players.append(f"{i}({player.name})")
        
        # 构建结果消息
        message = f"📢 全体私信发送结果\n"
        message += "=" * 30 + "\n"
        message += f"📝 消息内容：{message_content}\n"
        message += f"🎮 服务器：{server_num}\n"
        message += f"👥 目标玩家：{len(players)} 人\n"
        message += f"✅ 成功发送：{success_count} 人\n"
        if failed_players:
            message += f"❌ 发送失败：{', '.join(failed_players[:10])}"  # 只显示前10个失败的玩家
            if len(failed_players) > 10:
                message += f" 等{len(failed_players)}人"
        
        await broadcast_message.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"发送全体私信失败: {e}")
        await broadcast_message.finish("❌ 发送全体私信失败，请稍后重试")


# 权限管理指令（需要超级管理员或主人权限）
try:
    from ..permissions import ADMIN, SUPER_ADMIN, OWNER, permission_manager, get_permission_level_name, PermissionLevel
    
    add_admin_cmd = on_command("添加管理员", aliases={"addadmin", "管理员添加"}, priority=5, permission=SUPER_ADMIN)
    remove_admin_cmd = on_command("删除管理员", aliases={"removeadmin", "管理员删除"}, priority=5, permission=SUPER_ADMIN)
    list_admins_cmd = on_command("管理员列表", aliases={"listadmins", "查看管理员"}, priority=5, permission=ADMIN)
    permission_info_cmd = on_command("权限信息", aliases={"perminfo", "查看权限"}, priority=5, permission=ADMIN)
    
    @add_admin_cmd.handle()
    async def handle_add_admin(bot: Bot, event: Event, args: Message = CommandArg()):
        """添加普通管理员"""
        try:
            operator_id = str(event.get_user_id())
            args_text = args.extract_plain_text().strip()
            
            if not args_text:
                await add_admin_cmd.finish("❌ 请提供要添加的用户QQ号\n格式：/添加管理员 <QQ号>")
            
            # 解析参数
            parts = args_text.split()
            if len(parts) != 1:
                await add_admin_cmd.finish("❌ 参数格式错误\n格式：/添加管理员 <QQ号>")
            
            target_user_id = parts[0].strip()
            
            # 验证QQ号格式
            if not target_user_id.isdigit():
                await add_admin_cmd.finish("❌ QQ号格式错误，请输入纯数字")
            
            # 添加管理员
            success, message = permission_manager.add_admin(target_user_id, operator_id)
            
            if success:
                await add_admin_cmd.finish(f"✅ {message}\n👤 用户：{target_user_id}\n🔑 权限：普通管理员")
            else:
                await add_admin_cmd.finish(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"添加管理员失败: {e}")
            await add_admin_cmd.finish("❌ 添加管理员失败，请稍后重试")
    
    @remove_admin_cmd.handle()
    async def handle_remove_admin(bot: Bot, event: Event, args: Message = CommandArg()):
        """删除普通管理员"""
        try:
            operator_id = str(event.get_user_id())
            args_text = args.extract_plain_text().strip()
            
            if not args_text:
                await remove_admin_cmd.finish("❌ 请提供要删除的用户QQ号\n格式：/删除管理员 <QQ号>")
            
            # 解析参数
            parts = args_text.split()
            if len(parts) != 1:
                await remove_admin_cmd.finish("❌ 参数格式错误\n格式：/删除管理员 <QQ号>")
            
            target_user_id = parts[0].strip()
            
            # 验证QQ号格式
            if not target_user_id.isdigit():
                await remove_admin_cmd.finish("❌ QQ号格式错误，请输入纯数字")
            
            # 删除管理员
            success, message = permission_manager.remove_admin(target_user_id, operator_id)
            
            if success:
                await remove_admin_cmd.finish(f"✅ {message}\n👤 用户：{target_user_id}")
            else:
                await remove_admin_cmd.finish(f"❌ {message}")
                
        except Exception as e:
            logger.error(f"删除管理员失败: {e}")
            await remove_admin_cmd.finish("❌ 删除管理员失败，请稍后重试")
    
    @list_admins_cmd.handle()
    async def handle_list_admins(bot: Bot, event: Event):
        """查看管理员列表"""
        try:
            permissions = permission_manager.get_all_permissions()
            
            message = "👑 权限管理系统\n\n"
            
            # 主人列表
            owners = permissions['owners']
            message += f"🔱 主人 ({len(owners)}人)：\n"
            if owners:
                for i, user_id in enumerate(owners, 1):
                    message += f"  {i}. {user_id}\n"
            else:
                message += "  暂无\n"
            message += "\n"
            
            # 超级管理员列表
            super_admins = permissions['super_admins']
            message += f"⭐ 超级管理员 ({len(super_admins)}人)：\n"
            if super_admins:
                for i, user_id in enumerate(super_admins, 1):
                    message += f"  {i}. {user_id}\n"
            else:
                message += "  暂无\n"
            message += "\n"
            
            # 普通管理员列表
            admins = permissions['admins']
            message += f"🛡️ 普通管理员 ({len(admins)}人)：\n"
            if admins:
                for i, user_id in enumerate(admins, 1):
                    message += f"  {i}. {user_id}\n"
            else:
                message += "  暂无\n"
            
            message += "\n📝 权限说明：\n"
            message += "• 主人：拥有所有权限，可管理超级管理员\n"
            message += "• 超级管理员：拥有全部管理命令 + 管理员管理权限\n"
            message += "• 普通管理员：拥有全部管理命令（除管理员管理外）"
            
            await list_admins_cmd.finish(message)
            
        except Exception as e:
            # FinishedException 是正常的框架行为，不记录为错误
            if "FinishedException" not in str(type(e)):
                logger.error(f"查看管理员列表失败: {e}")
                await list_admins_cmd.finish("❌ 查看管理员列表失败，请稍后重试")
    
    @permission_info_cmd.handle()
    async def handle_permission_info(bot: Bot, event: Event, args: Message = CommandArg()):
        """查看用户权限信息"""
        try:
            logger.info(f"权限信息命令被调用，用户ID: {event.get_user_id()}")
            args_text = args.extract_plain_text().strip()
            
            # 如果没有参数，查看自己的权限
            if not args_text:
                target_user_id = str(event.get_user_id())
            else:
                # 解析参数
                parts = args_text.split()
                if len(parts) != 1:
                    await permission_info_cmd.finish("❌ 参数格式错误\n格式：/权限信息 [QQ号]")
                
                target_user_id = parts[0].strip()
                
                # 验证QQ号格式
                if not target_user_id.isdigit():
                    await permission_info_cmd.finish("❌ QQ号格式错误，请输入纯数字")
            
            logger.info(f"查询目标用户权限: {target_user_id}")
            
            # 获取用户权限
            user_level = permission_manager.get_user_permission(target_user_id)
            level_name = get_permission_level_name(user_level)
            
            logger.info(f"用户 {target_user_id} 的权限级别: {user_level}, 名称: {level_name}")
            
            message = f"👤 用户权限信息\n\n"
            message += f"🆔 QQ号：{target_user_id}\n"
            message += f"🔑 权限级别：{level_name}\n\n"
            
            logger.info(f"准备发送权限信息消息: {message[:50]}...")
            
            # 权限详情
            if user_level == PermissionLevel.OWNER:
                message += "🔱 主人权限包括：\n"
                message += "• 所有管理命令\n"
                message += "• 管理超级管理员\n"
                message += "• 管理普通管理员\n"
                message += "• 系统命令"
            elif user_level == PermissionLevel.SUPER_ADMIN:
                message += "⭐ 超级管理员权限包括：\n"
                message += "• 所有管理命令\n"
                message += "• 管理普通管理员\n"
                message += "• 系统命令"
            elif user_level == PermissionLevel.ADMIN:
                message += "🛡️ 普通管理员权限包括：\n"
                message += "• 玩家管理命令\n"
                message += "• VIP管理命令\n"
                message += "• 地图管理命令\n"
                message += "• 服务器设置命令\n"
                message += "• 消息管理命令"
            else:
                message += "👥 普通用户权限包括：\n"
                message += "• 查看服务器信息\n"
                message += "• 查询VIP状态\n"
                message += "• 查看帮助信息"
            
            logger.info("准备发送权限信息回复")
            await permission_info_cmd.finish(message)
            logger.info("权限信息回复已发送")
            
        except Exception as e:
            # FinishedException 是正常的框架行为，不记录为错误
            if "FinishedException" not in str(type(e)):
                logger.error(f"查看权限信息失败: {e}")
                await permission_info_cmd.finish("❌ 查看权限信息失败，请稍后重试")

except ImportError:
    logger.warning("权限管理模块未找到，跳过权限管理命令注册")