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
        server_config = config.servers.get(str(server_num))
        if not server_config:
            logger.error(f"服务器 {server_num} 配置不存在")
            return None
            
        async with CRCONAPIClient(server_config['url'], server_config['api_token']) as api_client:
            # 使用GetServerInformation: players获取详细玩家信息
            response = await api_client._request("GET", "get_server_information", {"name": "players"})
            if response and "players" in response:
                # 转换为团队视图格式
                players_data = response["players"]
                team_view = {
                    "allied": {"squads": {}, "players": []},
                    "axis": {"squads": {}, "players": []}
                }
                
                for player in players_data:
                    team_name = "allied" if player.get("team") == 1 else "axis"
                    platoon = player.get("platoon", "无小队")
                    
                    # 初始化小队
                    if platoon not in team_view[team_name]["squads"]:
                        team_view[team_name]["squads"][platoon] = {"players": []}
                    
                    # 添加玩家到小队
                    team_view[team_name]["squads"][platoon]["players"].append(player)
                    team_view[team_name]["players"].append(player)
                
                return team_view
            else:
                logger.warning(f"服务器 {server_num} 返回的数据格式不正确")
                return None
                
    except Exception as e:
        logger.error(f"从API获取团队视图数据失败: {e}")
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
            player_info = {
                'name': player.get('name', '未知玩家'),
                'player_id': player.get('iD', ''),  # API返回的是'iD'
                'team': "盟军" if player.get('team') == 1 else "轴心国",
                'squad': squad_name,
                'role': player.get('role', ''),
                'loadout': player.get('loadout', ''),
                'level': player.get('level', 0),
                'kills': player.get('kills', 0),
                'deaths': player.get('deaths', 0),
                'combat': score_data.get('cOMBAT', 0),  # API返回的是'cOMBAT'
                'offense': score_data.get('offense', 0),
                'defense': score_data.get('defense', 0),
                'support': score_data.get('support', 0),
                'platform': player.get('platform', ''),
                'clan_tag': player.get('clanTag', ''),  # API返回的是'clanTag'
                'is_vip': player.get('is_vip', False),
                'country': player.get('country', ''),
            }
            players.append(player_info)
    
    return players

async def update_player_cache():
    """更新玩家数据缓存"""
    global player_data_cache, last_update_time
    
    try:
        new_cache = {}
        
        # 遍历所有配置的服务器
        for server_num in config.servers.keys():
            server_num_int = int(server_num)
            data = await get_team_view_data_from_api(server_num_int)
            
            if not data:
                logger.warning(f"无法获取服务器 {server_num} 的团队视图数据")
                continue
            
            server_cache = {}
            
            # 解析盟军数据
            if 'allied' in data:
                allied_players = parse_player_data(data['allied'])
                server_cache['allied'] = allied_players
            
            # 解析轴心国数据
            if 'axis' in data:
                axis_players = parse_player_data(data['axis'])
                server_cache['axis'] = axis_players
            
            new_cache[server_num] = server_cache
            logger.info(f"已更新服务器 {server_num} 的玩家数据缓存")
        
        player_data_cache = new_cache
        last_update_time = datetime.now()
        logger.info("玩家数据缓存更新完成")
        
    except Exception as e:
        logger.error(f"更新玩家数据缓存失败: {e}")

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
    
    # 按分数排序（战斗分数 + 进攻分数 + 防守分数 + 支援分数）
    sorted_players = sorted(players, key=lambda p: p['combat'] + p['offense'] + p['defense'] + p['support'], reverse=True)
    
    for i, player in enumerate(sorted_players, 1):
        # 基本信息行
        name = player['name'][:12] + "..." if len(player['name']) > 12 else player['name']
        clan_tag = f"[{player['clan_tag']}]" if player['clan_tag'] else ""
        vip_mark = "👑" if player['is_vip'] else ""
        
        message += f"{i:2d}. {vip_mark}{clan_tag}{name}\n"
        
        # UID信息
        message += f"    🆔 UID: {player['player_id'][:16]}...\n"
        
        # 阵营和小队信息
        squad_info = f"小队{player['squad'].upper()}" if player['squad'] else "无小队"
        role_name = format_role_name(player['role'])
        message += f"    🏷️ {squad_info} | {role_name} | Lv.{player['level']}\n"
        
        # 战斗数据
        kd_ratio = player['kills'] / player['deaths'] if player['deaths'] > 0 else player['kills']
        message += f"    ⚔️ K/D: {player['kills']}/{player['deaths']} ({kd_ratio:.2f})\n"
        
        # 分数数据
        total_score = player['combat'] + player['offense'] + player['defense'] + player['support']
        message += f"    📊 总分: {total_score} (战斗:{player['combat']} 攻击:{player['offense']} 防守:{player['defense']} 支援:{player['support']})\n"
        
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
            server_name = get_server_name(server_num)
            title_msg = f"🎮 {server_name} - 详细在线玩家列表\n👥 总人数: {total_players}人\n🕐 更新时间: {update_time_str}\n⏰ 每6分钟自动更新"
            
            forward_messages.append({
                "type": "node",
                "data": {
                    "name": "CRCON机器人",
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
                        "name": "CRCON机器人",
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
                        "name": "CRCON机器人",
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