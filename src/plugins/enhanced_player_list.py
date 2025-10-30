#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from nonebot import on_command, get_driver, require
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from loguru import logger

# 导入调度器
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from ..config import config, get_server_name, validate_server_num
from ..crcon_api import CRCONAPIClient

# 注册命令
enhanced_player_list = on_command("详细玩家列表", aliases={"详细在线玩家", "玩家详情", "playerdetails"}, priority=5)

# 全局变量存储玩家数据缓存
player_data_cache: Dict[str, Any] = {}
last_update_time: Optional[datetime] = None

async def get_team_view_data_from_api(server_num: int) -> Optional[Dict[str, Any]]:
    """从API获取团队视图数据"""
    try:
        # 验证服务器编号
        if not validate_server_num(server_num):
            logger.error(f"无效的服务器编号: {server_num}")
            return None
        
        # 获取API客户端
        from ..config import get_api_base_url
        
        base_url = get_api_base_url(server_num)
        api_client = CRCONAPIClient(base_url, config.crcon_api_token)
        
        # 获取团队视图数据
        async with api_client as client:
            team_view_data = await client.get_team_view()
            
            if not team_view_data:
                return None
            
            return team_view_data
            
    except Exception as e:
        logger.error(f"获取服务器 {server_num} 团队视图数据失败: {e}")
        return None

def parse_player_data(team_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """解析团队数据中的玩家信息"""
    players = []
    
    if not team_data or 'squads' not in team_data:
        return players
    
    for squad_name, squad_data in team_data['squads'].items():
        if 'players' not in squad_data:
            continue
            
        for player in squad_data['players']:
            # 提取关键玩家信息，适配新的API数据格式
            score_data = player.get('scoreData', {})
            
            # 更灵活的队伍判断逻辑
            team_value = player.get('team', 0)
            if isinstance(team_value, str):
                if 'allied' in team_value.lower() or team_value == '1':
                    team_name = "盟军"
                elif 'axis' in team_value.lower() or team_value == '0':
                    team_name = "轴心国"
                else:
                    team_name = "未知"
            else:
                # 数字类型的队伍判断
                team_name = "盟军" if team_value == 1 else "轴心国"
            
            player_info = {
                'name': player.get('name', '未知玩家'),
                'player_id': player.get('iD', '') or player.get('id', '') or player.get('player_id', ''),  # 尝试多种可能的字段名
                'team': team_name,
                'squad': squad_name,
                'role': player.get('role', ''),
                'loadout': player.get('loadout', ''),
                'level': player.get('level', 0),
                'kills': player.get('kills', 0),
                'deaths': player.get('deaths', 0),
                'combat': score_data.get('cOMBAT', 0) or score_data.get('combat', 0),  # 尝试多种可能的字段名
                'offense': score_data.get('offense', 0) or score_data.get('attack', 0),
                'defense': score_data.get('defense', 0) or score_data.get('defend', 0),
                'support': score_data.get('support', 0),
                'platform': player.get('platform', ''),
                'clan_tag': player.get('clanTag', '') or player.get('clan_tag', ''),  # 尝试多种可能的字段名
                'is_vip': player.get('is_vip', False) or player.get('vip', False),
                'country': player.get('country', ''),
            }
            players.append(player_info)
    
    return players

async def update_player_cache():
    """更新玩家数据缓存"""
    global player_data_cache, last_update_time
    
    try:
        new_cache = {}
        
        # 遍历所有配置的服务器 (1-4)
        for server_num in [1, 2, 3, 4]:
            if not validate_server_num(server_num):
                continue
                
            data = await get_team_view_data_from_api(server_num)
            
            if not data:
                logger.warning(f"无法获取服务器 {server_num} 的团队视图数据")
                continue
            
            # 添加调试日志查看数据结构
            logger.info(f"服务器 {server_num} team_view 数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            
            server_cache = {}
            
            # 检查不同可能的数据结构
            if isinstance(data, dict):
                # 方式1: 直接包含 allies 和 axis 键
                if 'allies' in data:
                    allied_players = parse_player_data(data['allies'])
                    server_cache['allied'] = allied_players
                    logger.info(f"服务器 {server_num} 盟军玩家数: {len(allied_players)}")
                
                if 'axis' in data:
                    axis_players = parse_player_data(data['axis'])
                    server_cache['axis'] = axis_players
                    logger.info(f"服务器 {server_num} 轴心玩家数: {len(axis_players)}")
                
                # 方式2: 包含 teams 字典
                if 'teams' in data:
                    teams = data['teams']
                    if isinstance(teams, dict):
                        for team_key, team_data in teams.items():
                            logger.info(f"服务器 {server_num} 发现队伍: {team_key}")
                            if 'allied' in team_key.lower() or 'allies' in team_key.lower() or team_key == '1':
                                allied_players = parse_player_data(team_data)
                                server_cache['allied'] = allied_players
                                logger.info(f"服务器 {server_num} 盟军玩家数: {len(allied_players)}")
                            elif 'axis' in team_key.lower() or team_key == '0':
                                axis_players = parse_player_data(team_data)
                                server_cache['axis'] = axis_players
                                logger.info(f"服务器 {server_num} 轴心玩家数: {len(axis_players)}")
                
                # 方式3: 直接遍历所有键寻找队伍数据
                if not server_cache:
                    for key, value in data.items():
                        if isinstance(value, dict) and 'squads' in value:
                            logger.info(f"服务器 {server_num} 发现可能的队伍数据: {key}")
                            players = parse_player_data(value)
                            if players:
                                # 根据第一个玩家的队伍信息判断
                                first_player_team = players[0].get('team', '')
                                if '盟军' in first_player_team or 'allied' in first_player_team.lower():
                                    server_cache['allied'] = players
                                    logger.info(f"服务器 {server_num} 识别为盟军数据: {len(players)} 人")
                                elif '轴心' in first_player_team or 'axis' in first_player_team.lower():
                                    server_cache['axis'] = players
                                    logger.info(f"服务器 {server_num} 识别为轴心数据: {len(players)} 人")
            
            server_key = f"server_{server_num}"
            new_cache[server_key] = server_cache
            logger.info(f"已更新服务器 {server_num} 的玩家数据缓存")
        
        # 更新全局缓存
        player_data_cache = new_cache
        last_update_time = datetime.now()
        
        logger.info(f"玩家数据缓存更新完成，共 {len(new_cache)} 个服务器")
        
    except Exception as e:
        logger.error(f"更新玩家数据缓存失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

# 定时任务：每6分钟更新一次玩家数据
@scheduler.scheduled_job("interval", minutes=6, id="update_player_data")
async def scheduled_update_player_data():
    """定时更新玩家数据"""
    logger.info("开始定时更新玩家数据...")
    await update_player_cache()

def format_role_name(role: str) -> str:
    """格式化兵种名称为中文"""
    role_mapping = {
        'officer': '军官',
        'rifleman': '步枪兵',
        'assault': '突击兵',
        'automaticrifleman': '自动步枪兵',
        'medic': '医疗兵',
        'support': '支援兵',
        'machinegunner': '机枪手',
        'antitank': '反坦克兵',
        'engineer': '工程兵',
        'tankcommander': '坦克指挥官',
        'crewman': '坦克兵',
        'spotter': '侦察兵',
        'sniper': '狙击手',
        'commander': '指挥官'
    }
    return role_mapping.get(role.lower(), role)

def format_platform_name(platform: str) -> str:
    """格式化平台名称"""
    platform_mapping = {
        'steam': 'Steam',
        'epic': 'Epic',
        'xbox': 'Xbox',
        'playstation': 'PlayStation'
    }
    return platform_mapping.get(platform.lower(), platform)

def create_player_table_message(players: List[Dict[str, Any]], team_name: str) -> str:
    """创建玩家表格消息"""
    if not players:
        return f"📭 {team_name} 暂无玩家在线"
    
    message = f"🎮 {team_name} ({len(players)}人)\n"
    message += "=" * 40 + "\n"
    
    # 按等级排序
    sorted_players = sorted(players, key=lambda p: p['level'], reverse=True)
    
    for i, player in enumerate(sorted_players, 1):
        # 基本信息行
        name = player['name'][:12] + "..." if len(player['name']) > 12 else player['name']
        clan_tag = f"[{player['clan_tag']}]" if player['clan_tag'] else ""
        vip_mark = "👑" if player['is_vip'] else ""
        
        message += f"{i:2d}. {vip_mark}{clan_tag}{name}\n"
        
        # UID信息
        player_id = player['player_id'] or "未知"
        if len(player_id) > 20:
            uid_display = f"{player_id[:20]}..."
        else:
            uid_display = player_id
        message += f"    🆔 UID: {uid_display}\n"
        
        # 阵营和小队信息
        squad_info = f"小队{player['squad'].upper()}" if player['squad'] else "无小队"
        role_name = format_role_name(player['role'])
        message += f"    🏷️ {squad_info} | {role_name} | Lv.{player['level']}\n"
        
        # 平台信息
        platform = format_platform_name(player['platform'])
        message += f"    💻 平台: {platform}\n"
        
        if i < len(sorted_players):
            message += "\n"
    
    return message

@enhanced_player_list.handle()
async def handle_enhanced_player_list(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理详细玩家列表查询"""
    try:
        # 解析参数
        arg_text = args.extract_plain_text().strip()
        server_num = None
        
        if arg_text:
            try:
                server_num = int(arg_text)
                if not validate_server_num(server_num):
                    await enhanced_player_list.finish(f"❌ 无效的服务器编号: {server_num}")
            except ValueError:
                await enhanced_player_list.finish("❌ 服务器编号必须是数字")
        
        # 如果缓存为空或数据过期，立即更新
        if not player_data_cache or not last_update_time or \
           (datetime.now() - last_update_time).total_seconds() > 360:  # 6分钟
            await update_player_cache()
        
        if not player_data_cache:
            await enhanced_player_list.finish("❌ 无法获取玩家数据，请稍后重试")
        
        # 获取群组ID
        group_id = str(event.group_id) if hasattr(event, 'group_id') else None
        
        # 如果指定了服务器编号，只显示该服务器的数据
        if server_num:
            server_key = f"server_{server_num}"
            if server_key not in player_data_cache:
                await enhanced_player_list.finish(f"❌ 服务器{server_num}数据不可用")
            
            server_data = player_data_cache[server_key]
            allies_players = server_data.get('allied', [])
            axis_players = server_data.get('axis', [])
            total_players = len(allies_players) + len(axis_players)
            
            if total_players == 0:
                await enhanced_player_list.finish(f"📭 服务器{server_num}当前没有玩家在线")
            
            # 创建转发消息
            forward_messages = []
            
            # 添加标题消息
            update_time_str = last_update_time.strftime("%H:%M:%S") if last_update_time else "未知"
            server_name = get_server_name(server_num, group_id)
            title_msg = f"🎮 {server_name} - 详细在线玩家列表\n👥 总人数: {total_players}人\n🕐 更新时间: {update_time_str}\n⏰ 每6分钟自动更新"
            
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": server_name,
                    "uin": str(bot.self_id),
                    "content": title_msg
                }
            })
            
            # 添加盟军玩家信息
            if allies_players:
                allies_msg = create_player_table_message(allies_players, "盟军")
                forward_messages.append({
                    "type": "node",
                    "data": {
                        "name": server_name,
                        "uin": str(bot.self_id),
                        "content": allies_msg
                    }
                })
            
            # 添加轴心国玩家信息
            if axis_players:
                axis_msg = create_player_table_message(axis_players, "轴心国")
                forward_messages.append({
                    "type": "node",
                    "data": {
                        "name": server_name,
                        "uin": str(bot.self_id),
                        "content": axis_msg
                    }
                })
        else:
            # 显示所有服务器的汇总数据
            all_allies = []
            all_axis = []
            total_players = 0
            
            for server_key, server_data in player_data_cache.items():
                allies = server_data.get('allied', [])
                axis = server_data.get('axis', [])
                all_allies.extend(allies)
                all_axis.extend(axis)
                total_players += len(allies) + len(axis)
            
            if total_players == 0:
                await enhanced_player_list.finish("📭 所有服务器当前都没有玩家在线")
            
            # 创建转发消息
            forward_messages = []
            
            # 添加标题消息
            update_time_str = last_update_time.strftime("%H:%M:%S") if last_update_time else "未知"
            title_msg = f"🎮 所有服务器 - 详细在线玩家列表\n👥 总人数: {total_players}人\n🕐 更新时间: {update_time_str}\n⏰ 每6分钟自动更新\n💡 使用 /详细玩家列表 [服务器编号] 查看指定服务器"
            
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": "CRCON机器人",
                    "uin": str(bot.self_id),
                    "content": title_msg
                }
            })
            
            # 添加盟军玩家信息
            if all_allies:
                allies_msg = create_player_table_message(all_allies, "盟军")
                forward_messages.append({
                    "type": "node",
                    "data": {
                        "name": "CRCON机器人",
                        "uin": str(bot.self_id),
                        "content": allies_msg
                    }
                })
            
            # 添加轴心国玩家信息
            if all_axis:
                axis_msg = create_player_table_message(all_axis, "轴心国")
                forward_messages.append({
                    "type": "node",
                    "data": {
                        "name": "CRCON机器人",
                        "uin": str(bot.self_id),
                        "content": axis_msg
                    }
                })
        
        # 添加说明信息
        info_msg = "💡 功能说明:\n"
        info_msg += "• 👑 表示VIP玩家\n"
        info_msg += "• [标签] 表示战队标签\n"
        info_msg += "• UID显示前16位字符\n"
        info_msg += "• 数据每6分钟自动更新\n"
        info_msg += "• 按总分数排序显示"
        
        forward_messages.append({
            "type": "node",
            "data": {
                "name": "CRCON机器人",
                "uin": str(bot.self_id),
                "content": info_msg
            }
        })
        
        # 发送转发消息
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=forward_messages)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise
        logger.error(f"查询详细玩家列表失败: {e}")
        await enhanced_player_list.finish("❌ 查询详细玩家列表失败，请稍后重试")

# 启动时初始化数据
@get_driver().on_startup
async def init_player_data():
    """启动时初始化玩家数据"""
    logger.info("初始化玩家数据缓存...")
    await update_player_cache()