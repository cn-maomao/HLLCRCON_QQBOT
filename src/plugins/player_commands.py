#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from typing import List, Optional
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from loguru import logger

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from ...maplist import MapList
except ImportError:
    MapList = None

from ..crcon_api import CRCONAPIClient, GameState, VipInfo

# 获取配置
from ..config import config, get_api_base_url, get_server_name, validate_server_num, Constants

# API配置
CRCON_API_BASE_URL_1 = config.crcon_api_base_url_1
CRCON_API_BASE_URL_2 = config.crcon_api_base_url_2
CRCON_API_BASE_URL_3 = config.crcon_api_base_url_3
CRCON_API_BASE_URL_4 = config.crcon_api_base_url_4
CRCON_API_TOKEN = config.crcon_api_token

# 注册指令
server_info = on_command("服务器信息", aliases={"服务器状态", "server", "查服"}, priority=5)
vip_check = on_command("查询vip", aliases={"vip查询", "checkvip"}, priority=5)
online_players = on_command("在线玩家", aliases={"玩家列表", "players", "online"}, priority=5)
help_cmd = on_command("帮助", aliases={"help", "指令"}, priority=5)


def format_time(seconds: int) -> str:
    """格式化时间显示"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


async def get_api_client(server_num: int = 1) -> CRCONAPIClient:
    """获取API客户端"""
    try:
        base_url = get_api_base_url(server_num)
        return CRCONAPIClient(base_url, CRCON_API_TOKEN)
    except Exception as e:
        logger.error(f"创建API客户端失败: {e}")
        raise


async def get_server_info(server_num: int) -> str:
    """获取单个服务器的状态信息"""
    async with await get_api_client(server_num) as client:
        # 获取游戏状态
        gamestate = await client.get_gamestate()
        
        # 解析地图信息
        current_map_name = "未知"
        
        # 处理当前地图信息
        if isinstance(gamestate.current_map, dict):
            # 优先使用嵌套的 map.id 字段
            map_id = gamestate.current_map.get('map', {}).get('id', '')
            if not map_id:
                # 如果没有嵌套的 map.id，使用顶级 id
                map_id = gamestate.current_map.get('id', '')
            
            if map_id and map_id.lower() != 'unknown':
                # 使用 MapList 转换为中文名称，并结合游戏模式
                game_mode = gamestate.current_map.get('game_mode', '')
                mode_text = ""
                if game_mode == 'offensive':
                    mode_text = " · 攻防"
                elif game_mode == 'warfare':
                    mode_text = " · 冲突"
                elif game_mode == 'skirmish':
                    mode_text = " · 遭遇战"
                
                if MapList:
                    current_map_name = MapList.parse_map_name(map_id) + mode_text
                else:
                    current_map_name = map_id + mode_text
            else:
                current_map_name = gamestate.current_map.get('pretty_name', 
                                 gamestate.current_map.get('name', '未知'))
        elif isinstance(gamestate.current_map, str):
            # 尝试解析字符串格式的地图ID
            if MapList:
                current_map_name = MapList.parse_map_name(gamestate.current_map)
            else:
                current_map_name = gamestate.current_map
        
        # 构建消息
        server_name = get_server_name(server_num)
        message = f"🎮 {server_name} 状态信息\n"
        message += "=" * 30 + "\n"
        message += f"📊 当前比分：\n"
        message += f"  🔵 盟军：{gamestate.allied_score} 分 ({gamestate.allied_players} 人)\n"
        message += f"  🔴 轴心：{gamestate.axis_score} 分 ({gamestate.axis_players} 人)\n"
        message += f"👥 总人数：{gamestate.allied_players + gamestate.axis_players} 人\n"
        
        # 格式化剩余时间
        if gamestate.remaining_time:
            message += f"⏰ 剩余时间：{gamestate.remaining_time}\n"
        else:
            message += f"⏰ 剩余时间：未知\n"
            
        message += f"🗺️ 当前地图：{current_map_name}"
        
        return message


@server_info.handle()
async def handle_server_info(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理服务器信息查询"""
    try:
        arg_text = args.extract_plain_text().strip()
        
        # 构建转发消息节点
        nodes = []
        
        # 添加标题节点
        title_node = {
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": "🎮 服务器状态信息"
            }
        }
        nodes.append(title_node)
        
        # 如果没有参数，显示群绑定服务器组的服务器信息
        if not arg_text:
            # 获取群ID和对应的服务器组
            group_id = str(event.group_id) if hasattr(event, 'group_id') else None
            
            # 导入权限管理器来获取群绑定的服务器组
            from ..permission_groups import get_permission_group_manager
            permission_manager = get_permission_group_manager()
            
            if group_id:
                server_group = permission_manager.get_group_for_qq_group(group_id)
                if server_group and server_group.game_servers:
                    # 显示群绑定服务器组中的服务器
                    for server_config in server_group.game_servers:
                        try:
                            # 处理服务器配置对象
                            if isinstance(server_config, dict):
                                server_id = server_config.get('server_id', '')
                                server_name = server_config.get('name', '')
                                enabled = server_config.get('enabled', True)
                                
                                # 跳过禁用的服务器
                                if not enabled:
                                    continue
                            else:
                                # 如果是字符串，直接使用
                                server_id = str(server_config)
                                server_name = ""
                            
                            # 将服务器ID转换为数字（如果是数字字符串）
                            if server_id.isdigit():
                                server_num = int(server_id)
                            elif server_id.startswith('server_') and server_id[7:].isdigit():
                                # 处理 server_1, server_2 等格式
                                server_num = int(server_id[7:])
                            else:
                                # 如果不是数字，尝试通过多服务器管理器解析
                                from ..multi_server_manager import multi_server_manager
                                if multi_server_manager:
                                    resolved_id = multi_server_manager.resolve_server_id(server_id, group_id)
                                    if resolved_id and resolved_id.isdigit():
                                        server_num = int(resolved_id)
                                    else:
                                        continue
                                else:
                                    continue
                            
                            server_msg = await get_server_info(server_num)
                            display_name = server_name if server_name else get_server_name(server_num, group_id)
                            server_node = {
                                "type": "node",
                                "data": {
                                    "name": display_name,
                                    "uin": str(bot.self_id),
                                    "content": server_msg
                                }
                            }
                            nodes.append(server_node)
                        except Exception as e:
                            logger.error(f"获取服务器{server_config}信息失败: {e}")
                            error_msg = f"🎮 {get_server_name(server_id, group_id)} 状态信息\n" + "=" * 30 + "\n❌ 服务器连接失败"
                            error_node = {
                                "type": "node",
                                "data": {
                                    "name": f"{get_server_name(server_id, group_id)}",
                                    "uin": str(bot.self_id),
                                    "content": error_msg
                                }
                            }
                            nodes.append(error_node)
                else:
                    # 如果没有找到群绑定的服务器组，显示默认服务器
                    await server_info.finish("❌ 当前群未绑定任何服务器组，请联系管理员配置")
            else:
                # 私聊情况，显示所有服务器
                for server_num in [1, 2, 3, 4]:
                    try:
                        server_msg = await get_server_info(server_num)
                        server_node = {
                            "type": "node",
                            "data": {
                                "name": f"{get_server_name(server_num)}",
                                "uin": str(bot.self_id),
                                "content": server_msg
                            }
                        }
                        nodes.append(server_node)
                    except Exception as e:
                        logger.error(f"获取{get_server_name(server_num)}信息失败: {e}")
                        error_msg = f"🎮 {get_server_name(server_num)} 状态信息\n" + "=" * 30 + "\n❌ 服务器连接失败"
                        error_node = {
                            "type": "node",
                            "data": {
                                "name": f"{get_server_name(server_num)}",
                                "uin": str(bot.self_id),
                                "content": error_msg
                            }
                        }
                        nodes.append(error_node)
        else:
            # 如果有参数，解析服务器编号或别名
            group_id = str(event.group_id) if hasattr(event, 'group_id') else None
            
            # 尝试通过多服务器管理器解析服务器标识符
            from ..multi_server_manager import multi_server_manager
            
            if multi_server_manager:
                server_config = multi_server_manager.get_server_config(arg_text, group_id)
                if server_config:
                    # 从配置中提取服务器编号
                    server_id = server_config.server_id
                    if server_id.isdigit():
                        server_num = int(server_id)
                        server_msg = await get_server_info(server_num)
                        server_node = {
                            "type": "node",
                            "data": {
                                "name": f"{get_server_name(server_num, group_id)}",
                                "uin": str(bot.self_id),
                                "content": server_msg
                            }
                        }
                        nodes.append(server_node)
                    else:
                        await server_info.finish(f"❌ 服务器配置错误: {arg_text}")
                else:
                    await server_info.finish(f"❌ 未找到服务器: {arg_text}\n请使用正确的服务器编号或别名")
            else:
                # 回退到原来的逻辑
                if arg_text.isdigit():
                    server_num = int(arg_text)
                    if not validate_server_num(server_num, group_id):
                        await server_info.finish("❌ 服务器编号无效或当前群无权访问")
                    
                    server_msg = await get_server_info(server_num)
                    server_node = {
                        "type": "node",
                        "data": {
                            "name": f"{get_server_name(server_num, group_id)}",
                            "uin": str(bot.self_id),
                            "content": server_msg
                        }
                    }
                    nodes.append(server_node)
                else:
                    await server_info.finish("❌ 请输入正确的服务器编号或别名")
        
        # 发送转发消息
        try:
            group_id = event.group_id if hasattr(event, 'group_id') else None
            if group_id:
                await bot.call_api("send_group_forward_msg", group_id=group_id, messages=nodes)
            else:
                await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=nodes)
        except Exception as e:
            logger.error(f"发送转发消息失败: {e}")
            # 回退到普通消息
            if not arg_text:
                messages = []
                for server_num in [1, 2, 3, 4]:
                    try:
                        server_msg = await get_server_info(server_num)
                        messages.append(server_msg)
                    except Exception as e:
                        logger.error(f"获取{get_server_name(server_num)}信息失败: {e}")
                messages.append(f"🎮 {get_server_name(server_num)} 状态信息\n" + "=" * 30 + "\n❌ 服务器连接失败")
                
                final_message = "\n\n".join(messages)
                await server_info.finish(final_message)
            else:
                if arg_text.isdigit():
                    server_num = int(arg_text)
                    server_msg = await get_server_info(server_num)
                    await server_info.finish(server_msg)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询服务器信息失败: {e}")
        await server_info.finish("❌ 查询服务器信息失败，请稍后重试")


async def get_player_real_name(player_id: str, server_num: int) -> Optional[str]:
    """通过玩家ID获取真实玩家名称，只使用get_players_history接口"""
    try:
        async with await get_api_client(server_num) as client:
            # 使用get_players_history接口获取玩家历史记录
            history_data = await client.get_players_history(player_id=player_id, page_size=1)
            if history_data and isinstance(history_data, dict):
                players_history = history_data.get('players', [])
                if players_history:
                    # 获取最新的玩家记录
                    latest_player = players_history[0]
                    names = latest_player.get('names', [])
                    if names:
                        # 返回最新使用的名称
                        return names[0].get('name') if isinstance(names[0], dict) else names[0]
            
            # 如果没有找到历史记录，返回None
            logger.warning(f"未找到玩家 {player_id} 的历史记录")
            return None
            
    except Exception as e:
        logger.error(f"获取玩家名称失败: {e}")
        return None

async def search_vip_in_server(player_name: str, server_num: int) -> Optional[VipInfo]:
    """在指定服务器中搜索VIP玩家"""
    try:
        async with await get_api_client(server_num) as client:
            vip_list = await client.get_vip_ids()
            
            # 查找指定玩家
            for vip in vip_list:
                # 支持通过玩家名称或玩家ID搜索
                if (player_name.lower() in vip.name.lower() or 
                    player_name == vip.player_id):
                    
                    # 如果找到的是玩家ID，尝试获取真实玩家名称
                    if player_name == vip.player_id:
                        real_name = await get_player_real_name(vip.player_id, server_num)
                        if real_name:
                            # 创建一个新的VipInfo对象，使用真实名称
                            return VipInfo(
                                player_id=vip.player_id,
                                name=real_name,
                                expiration=vip.expiration,
                                description=vip.description
                            )
                    
                    return vip
            return None
    except Exception as e:
        logger.error(f"在{get_server_name(server_num)}中搜索VIP失败: {e}")
        return None


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
        server_num = None
        
        # 检查是否指定了服务器编号
        if len(parts) > 1 and parts[1].isdigit():
            server_num = int(parts[1])
            if not validate_server_num(server_num):
                await vip_check.finish("❌ 服务器编号只能是1、2、3或4")
        
        # 构建转发消息节点
        nodes = []
        
        # 添加标题节点
        title_node = {
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": f"🔍 VIP查询结果 - {player_name}"
            }
        }
        nodes.append(title_node)
        
        # 如果指定了服务器编号，只查询该服务器
        if server_num:
            found_vip = await search_vip_in_server(player_name, server_num)
            
            if found_vip:
                server_name = get_server_name(server_num)
                message = f"🎮 服务器：{server_name}\n"
                message += f"👤 玩家：{found_vip.name}\n"
                message += f"🆔 Steam ID：{found_vip.player_id}\n"
                message += f"💎 VIP状态：✅ 有效\n"
                
                # 格式化到期时间
                if found_vip.expiration:
                    try:
                        from datetime import datetime
                        # 尝试解析时间格式
                        if 'T' in found_vip.expiration:
                            dt = datetime.fromisoformat(found_vip.expiration.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_time = found_vip.expiration
                        message += f"⏰ 到期时间：{formatted_time}\n"
                    except:
                        message += f"⏰ 到期时间：{found_vip.expiration}\n"
                else:
                    message += f"⏰ 到期时间：🔄 永久有效\n"
                
                if found_vip.description:
                    message += f"📝 备注：{found_vip.description}\n"
                
                message += "\n💡 提示：VIP用户享有优先进入服务器等特权"
                
                vip_node = {
                    "type": "node",
                    "data": {
                        "name": f"VIP信息 - {server_name}",
                        "uin": str(bot.self_id),
                        "content": message
                    }
                }
                nodes.append(vip_node)
            else:
                server_name = get_server_name(server_num)
                message = f"🎮 服务器：{server_name}\n"
                message += f"👤 查询玩家：{player_name}\n"
                message += f"💎 VIP状态：❌ 未找到\n\n"
                message += f"📋 可能原因：\n"
                message += f"  • 该玩家不是VIP用户\n"
                message += f"  • 玩家名称输入错误\n"
                message += f"  • VIP已过期\n\n"
                message += f"💡 提示：请检查玩家名称拼写或联系管理员"
                
                error_node = {
                    "type": "node",
                    "data": {
                        "name": f"查询结果 - {server_name}",
                        "uin": str(bot.self_id),
                        "content": message
                    }
                }
                nodes.append(error_node)
        
        # 如果没有指定服务器编号，查询所有服务器
        else:
            found_vips = []
            for srv_num in [1, 2, 3, 4]:
                vip_info = await search_vip_in_server(player_name, srv_num)
                if vip_info:
                    found_vips.append((srv_num, vip_info))
            
            if found_vips:
                for srv_num, vip_info in found_vips:
                    server_name = get_server_name(srv_num)
                    message = f"🎮 服务器：{server_name}\n"
                    message += f"👤 玩家：{vip_info.name}\n"
                    message += f"🆔 Steam ID：{vip_info.player_id}\n"
                    message += f"💎 VIP状态：✅ 有效\n"
                    
                    # 格式化到期时间
                    if vip_info.expiration:
                        try:
                            from datetime import datetime
                            if 'T' in vip_info.expiration:
                                dt = datetime.fromisoformat(vip_info.expiration.replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                            else:
                                formatted_time = vip_info.expiration
                            message += f"⏰ 到期时间：{formatted_time}\n"
                        except:
                            message += f"⏰ 到期时间：{vip_info.expiration}\n"
                    else:
                        message += f"⏰ 到期时间：🔄 永久有效\n"
                    
                    if vip_info.description:
                        message += f"📝 备注：{vip_info.description}\n"
                    
                    message += "\n💡 提示：VIP用户享有优先进入服务器等特权"
                    
                    vip_node = {
                        "type": "node",
                        "data": {
                            "name": f"VIP信息 - {server_name}",
                            "uin": str(bot.self_id),
                            "content": message
                        }
                    }
                    nodes.append(vip_node)
            else:
                message = f"👤 查询玩家：{player_name}\n"
                message += f"💎 VIP状态：❌ 未找到\n"
                message += f"🔍 搜索范围：所有服务器\n\n"
                message += f"📋 可能原因：\n"
                message += f"  • 该玩家不是VIP用户\n"
                message += f"  • 玩家名称输入错误\n"
                message += f"  • VIP已过期或被移除\n\n"
                message += f"💡 建议：\n"
                message += f"  • 检查玩家名称拼写\n"
                message += f"  • 尝试使用完整的玩家名称\n"
                message += f"  • 联系管理员确认VIP状态"
                
                error_node = {
                    "type": "node",
                    "data": {
                        "name": "查询结果 - 全服务器",
                        "uin": str(bot.self_id),
                        "content": message
                    }
                }
                nodes.append(error_node)
        
        # 发送转发消息
        try:
            group_id = event.group_id if hasattr(event, 'group_id') else None
            if group_id:
                await bot.call_api("send_group_forward_msg", group_id=group_id, messages=nodes)
            else:
                await bot.call_api("send_private_forward_msg", user_id=event.user_id, messages=nodes)
        except Exception as e:
            logger.error(f"发送转发消息失败: {e}")
            # 回退到普通消息
            if server_num:
                found_vip = await search_vip_in_server(player_name, server_num)
                
                if found_vip:
                    server_name = get_server_name(server_num)
                    message = f"🔍 VIP查询结果\n"
                    message += "=" * 25 + "\n"
                    message += f"🎮 服务器：{server_name}\n"
                    message += f"👤 玩家：{found_vip.name}\n"
                    message += f"🆔 Steam ID：{found_vip.player_id}\n"
                    message += f"💎 VIP状态：✅ 有效\n"
                    
                    # 格式化到期时间
                    if found_vip.expiration:
                        try:
                            from datetime import datetime
                            # 尝试解析时间格式
                            if 'T' in found_vip.expiration:
                                dt = datetime.fromisoformat(found_vip.expiration.replace('Z', '+00:00'))
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                            else:
                                formatted_time = found_vip.expiration
                            message += f"⏰ 到期时间：{formatted_time}\n"
                        except:
                            message += f"⏰ 到期时间：{found_vip.expiration}\n"
                    else:
                        message += f"⏰ 到期时间：🔄 永久有效\n"
                    
                    if found_vip.description:
                        message += f"📝 备注：{found_vip.description}\n"
                    
                    message += "\n💡 提示：VIP用户享有优先进入服务器等特权"
                else:
                    server_name = get_server_name(server_num)
                    message = f"❌ VIP查询结果\n"
                    message += "=" * 25 + "\n"
                    message += f"🎮 服务器：{server_name}\n"
                    message += f"👤 查询玩家：{player_name}\n"
                    message += f"💎 VIP状态：❌ 未找到\n\n"
                    message += f"📋 可能原因：\n"
                    message += f"  • 该玩家不是VIP用户\n"
                    message += f"  • 玩家名称输入错误\n"
                    message += f"  • VIP已过期\n\n"
                    message += f"💡 提示：请检查玩家名称拼写或联系管理员"
                
                await vip_check.finish(message)
            else:
                # 查询所有服务器的回退逻辑
                found_vips = []
                for srv_num in [1, 2, 3, 4]:
                    vip_info = await search_vip_in_server(player_name, srv_num)
                    if vip_info:
                        found_vips.append((srv_num, vip_info))
                
                if found_vips:
                    if len(found_vips) == 1:
                        # 只有一个服务器找到VIP，使用简洁格式
                        srv_num, vip_info = found_vips[0]
                        server_name = get_server_name(srv_num)
                        message = f"🔍 VIP查询结果\n"
                        message += "=" * 25 + "\n"
                        message += f"🎮 服务器：{server_name}\n"
                        message += f"👤 玩家：{vip_info.name}\n"
                        message += f"🆔 Steam ID：{vip_info.player_id}\n"
                        message += f"💎 VIP状态：✅ 有效\n"
                        
                        # 格式化到期时间
                        if vip_info.expiration:
                            try:
                                from datetime import datetime
                                if 'T' in vip_info.expiration:
                                    dt = datetime.fromisoformat(vip_info.expiration.replace('Z', '+00:00'))
                                    formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                                else:
                                    formatted_time = vip_info.expiration
                                message += f"⏰ 到期时间：{formatted_time}\n"
                            except:
                                message += f"⏰ 到期时间：{vip_info.expiration}\n"
                        else:
                            message += f"⏰ 到期时间：🔄 永久有效\n"
                        
                        if vip_info.description:
                            message += f"📝 备注：{vip_info.description}\n"
                        
                        message += "\n💡 提示：VIP用户享有优先进入服务器等特权"
                        await vip_check.finish(message)
                    else:
                        # 多个服务器找到VIP，使用多服务器格式
                        message = f"🔍 VIP查询结果 - 多服务器\n"
                        message += "=" * 30 + "\n"
                        message += f"👤 查询玩家：{player_name}\n"
                        message += f"📊 找到 {len(found_vips)} 个服务器的VIP记录\n\n"
                        
                        for i, (srv_num, vip_info) in enumerate(found_vips, 1):
                            server_name = get_server_name(srv_num)
                            message += f"🎮 【{server_name}】\n"
                            message += f"  👤 玩家名：{vip_info.name}\n"
                            message += f"  🆔 Steam ID：{vip_info.player_id}\n"
                            message += f"  💎 状态：✅ 有效\n"
                            
                            # 格式化到期时间
                            if vip_info.expiration:
                                try:
                                    from datetime import datetime
                                    if 'T' in vip_info.expiration:
                                        dt = datetime.fromisoformat(vip_info.expiration.replace('Z', '+00:00'))
                                        formatted_time = dt.strftime('%Y-%m-%d %H:%M')
                                    else:
                                        formatted_time = vip_info.expiration
                                    message += f"  ⏰ 到期：{formatted_time}\n"
                                except:
                                    message += f"  ⏰ 到期：{vip_info.expiration}\n"
                            else:
                                message += f"  ⏰ 到期：🔄 永久\n"
                            
                            if vip_info.description:
                                message += f"  📝 备注：{vip_info.description}\n"
                            
                            if i < len(found_vips):
                                message += "\n"
                        
                        message += "\n💡 提示：该玩家在多个服务器都拥有VIP特权"
                        await vip_check.finish(message)
                else:
                    message = f"❌ VIP查询结果 - 全服务器\n"
                    message += "=" * 30 + "\n"
                    message += f"👤 查询玩家：{player_name}\n"
                    message += f"💎 VIP状态：❌ 未找到\n"
                    message += f"🔍 搜索范围：所有服务器\n\n"
                    message += f"📋 可能原因：\n"
                    message += f"  • 该玩家不是VIP用户\n"
                    message += f"  • 玩家名称输入错误\n"
                    message += f"  • VIP已过期或被移除\n\n"
                    message += f"💡 建议：\n"
                    message += f"  • 检查玩家名称拼写\n"
                    message += f"  • 尝试使用完整的玩家名称\n"
                    message += f"  • 联系管理员确认VIP状态"
                    await vip_check.finish(message)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询VIP状态失败: {e}")
        await vip_check.finish("❌ 查询VIP状态失败，请稍后重试")


@online_players.handle()
async def handle_online_players(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理在线玩家查询指令"""
    try:
        # 解析参数
        args_text = args.extract_plain_text().strip()
        server_num = 1  # 默认服务器1
        
        if args_text:
            try:
                server_num = int(args_text)
                if not validate_server_num(server_num):
                    await online_players.finish(config.get_message("invalid_server_num"))
            except ValueError:
                await online_players.finish("❌ 服务器编号格式错误，请输入1、2或3")
        
        # 获取在线玩家信息
        async with await get_api_client(server_num) as client:
            players = await client.get_players()
            
            if not players:
                server_name = get_server_name(server_num)
                message = f"🎮 {server_name} - 在线玩家\n"
                message += "=" * 30 + "\n"
                message += "📭 当前没有玩家在线"
                await online_players.finish(message)
            
            # 构建转发消息列表
            server_name = get_server_name(server_num)
            
            # 按玩家分数排序（如果有的话）
            sorted_players = sorted(players, key=lambda p: getattr(p, 'score', 0), reverse=True)
            
            # 创建转发消息节点列表
            forward_messages = []
            
            # 添加标题消息
            title_msg = f"🎮 {server_name} - 在线玩家\n👥 在线人数：{len(players)}"
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": "CRCON机器人",
                    "uin": str(bot.self_id),
                    "content": title_msg
                }
            })
            
            # 添加每个玩家的信息
            for i, player in enumerate(sorted_players, 1):
                # 获取玩家基本信息
                name = player.name or "未知玩家"
                score = getattr(player, 'score', 0)
                kills = getattr(player, 'kills', 0)
                deaths = getattr(player, 'deaths', 0)
                
                # 计算K/D比率
                kd_ratio = kills / deaths if deaths > 0 else kills
                
                player_msg = f"{i:2d}. 👤 {name}\n🎯 分数: {score} | 击杀: {kills} | 死亡: {deaths} | K/D: {kd_ratio:.2f}"
                
                forward_messages.append({
                    "type": "node",
                    "data": {
                        "name": "CRCON机器人",
                        "uin": str(bot.self_id),
                        "content": player_msg
                    }
                })
            
            # 发送转发消息
            await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=forward_messages)
            
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询在线玩家失败: {e}")
        await online_players.finish("❌ 查询在线玩家失败，请稍后重试")





@help_cmd.handle()
async def handle_help(bot: Bot, event: Event):
    """处理帮助指令"""
    try:
        # 创建转发消息节点列表
        forward_messages = []
        
        # 添加标题消息
        title_msg = "🤖 CRCON管理机器人 - 玩家功能"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": title_msg
            }
        })
        
        # 添加服务器信息查询说明
        server_info_msg = "📊 服务器信息查询：\n/服务器信息 [服务器编号]\n/server [1|2]\n/status [1|2]"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": server_info_msg
            }
        })
        
        # 添加VIP查询说明
        vip_msg = "💎 VIP状态查询：\n/查询vip 玩家名称 [服务器编号]\n/vip查询 玩家名称 [服务器编号]\n/checkvip 玩家名称 [服务器编号]"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": vip_msg
            }
        })
        
        # 添加在线玩家查询说明
        players_msg = "👥 在线玩家查询：\n/在线玩家 [服务器编号]\n/玩家列表 [服务器编号]\n/players [1|2]\n/online [1|2]\n/详细玩家列表 [服务器编号] - 查看详细玩家信息（包含UID、阵营、兵种等）\n/详细在线玩家 [服务器编号] - 同上\n/玩家详情 [服务器编号] - 同上\n/团队视图 [服务器编号] - 查看团队视图（按小队分组显示）"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": players_msg
            }
        })
        
        # 添加服务器管理说明
        server_mgmt_msg = "🖥️ 服务器管理：\n/服务器列表 - 查看所有可用服务器\n/服务器详情 [服务器编号] - 查看指定服务器详细信息\n/重载配置 - 重新加载服务器配置（管理员）"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": server_mgmt_msg
            }
        })
        
        # 添加权限管理说明
        permission_msg = "🔐 权限管理：\n/权限组列表 - 查看所有权限组\n/权限组详情 [组ID] - 查看权限组详细信息\n/我的权限 - 查看自己的权限信息\n/添加权限 [QQ号] [组ID] [权限级别] - 添加权限（管理员）\n/移除权限 [QQ号] [组ID] - 移除权限（管理员）\n/重载权限配置 - 重新加载权限配置（管理员）"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": permission_msg
            }
        })
        
        # 添加使用说明
        usage_msg = "📝 使用说明：\n• 服务器编号：1、2、3或4，默认为1\n• 玩家名称支持模糊匹配\n• 详细玩家列表每6分钟自动更新数据\n• 团队视图显示按小队分组的玩家信息\n• 支持动态配置文件管理\n• 所有指令都支持别名"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": usage_msg
            }
        })
        
        # 添加示例
        example_msg = "💡 使用示例：\n/服务器信息 1\n/查询vip PlayerName 2\n/在线玩家 1\n/详细玩家列表 2 - 查看详细玩家信息（含UID、阵营等）\n/团队视图 1 - 查看团队视图（按小队分组）\n/服务器列表 - 查看所有可用服务器\n/权限组列表 - 查看权限组\n/我的权限 - 查看自己权限"
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": example_msg
            }
        })
        
        # 发送转发消息
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=forward_messages)
        
    except Exception as e:
        logger.error(f"发送帮助信息失败: {e}")
        # 如果转发消息失败，发送普通消息作为备用
        message = "🤖 CRCON管理机器人 - 玩家功能\n"
        message += "=" * 35 + "\n"
        message += "📊 服务器信息查询：/服务器信息 [服务器编号]\n"
        message += "💎 VIP状态查询：/查询vip 玩家名称 [服务器编号]\n"
        message += "👥 在线玩家查询：/在线玩家 [服务器编号]\n"
        message += "📝 说明：服务器编号1、2或3，默认为1"
        await help_cmd.finish(message)