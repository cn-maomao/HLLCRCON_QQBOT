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

# 导入定时任务
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from ..config import config, get_server_name, validate_server_num

# 注册命令
enhanced_player_list = on_command("详细玩家列表", aliases={"详细在线玩家", "玩家详情", "playerdetails"}, priority=5)

# 全局变量存储玩家数据缓存
player_data_cache: Dict[str, Any] = {}
last_update_time: Optional[datetime] = None

# 数据文件路径
DATA_FILE_PATH = Path("d:/daima code/CRCON_QQBOT/get_team_view.json")

def load_team_view_data() -> Optional[Dict[str, Any]]:
    """从文件加载团队视图数据"""
    try:
        if not DATA_FILE_PATH.exists():
            logger.warning(f"团队视图数据文件不存在: {DATA_FILE_PATH}")
            return None
            
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        logger.error(f"加载团队视图数据失败: {e}")
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
            # 提取关键玩家信息
            player_info = {
                'name': player.get('name', '未知玩家'),
                'player_id': player.get('player_id', ''),
                'team': player.get('team', ''),
                'squad': squad_name,
                'role': player.get('role', ''),
                'loadout': player.get('loadout', ''),
                'level': player.get('level', 0),
                'kills': player.get('kills', 0),
                'deaths': player.get('deaths', 0),
                'combat': player.get('combat', 0),
                'offense': player.get('offense', 0),
                'defense': player.get('defense', 0),
                'support': player.get('support', 0),
                'platform': player.get('platform', ''),
                'clan_tag': player.get('clan_tag', ''),
                'is_vip': player.get('is_vip', False),
                'country': player.get('country', ''),
            }
            players.append(player_info)
    
    return players

def update_player_cache():
    """更新玩家数据缓存"""
    global player_data_cache, last_update_time
    
    try:
        data = load_team_view_data()
        if not data or 'result' not in data:
            logger.warning("无法获取有效的团队视图数据")
            return
        
        result = data['result']
        new_cache = {}
        
        # 解析盟军数据
        if 'allies' in result:
            allies_players = parse_player_data(result['allies'])
            new_cache['allies'] = allies_players
        
        # 解析轴心国数据
        if 'axis' in result:
            axis_players = parse_player_data(result['axis'])
            new_cache['axis'] = axis_players
        
        player_data_cache = new_cache
        last_update_time = datetime.now()
        
        total_players = len(new_cache.get('allies', [])) + len(new_cache.get('axis', []))
        logger.info(f"玩家数据缓存已更新，共 {total_players} 名玩家")
        
    except Exception as e:
        logger.error(f"更新玩家数据缓存失败: {e}")

# 定时任务：每6分钟更新一次玩家数据
@scheduler.scheduled_job("interval", minutes=6, id="update_player_data")
async def scheduled_update_player_data():
    """定时更新玩家数据"""
    logger.info("开始定时更新玩家数据...")
    update_player_cache()

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
        # 如果缓存为空或数据过期，立即更新
        if not player_data_cache or not last_update_time or \
           (datetime.now() - last_update_time).total_seconds() > 360:  # 6分钟
            update_player_cache()
        
        if not player_data_cache:
            await enhanced_player_list.finish("❌ 无法获取玩家数据，请稍后重试")
        
        # 获取盟军和轴心国玩家数据
        allies_players = player_data_cache.get('allies', [])
        axis_players = player_data_cache.get('axis', [])
        
        total_players = len(allies_players) + len(axis_players)
        
        if total_players == 0:
            await enhanced_player_list.finish("📭 当前没有玩家在线")
        
        # 创建转发消息
        forward_messages = []
        
        # 添加标题消息
        update_time_str = last_update_time.strftime("%H:%M:%S") if last_update_time else "未知"
        title_msg = f"🎮 详细在线玩家列表\n👥 总人数: {total_players}人\n🕐 更新时间: {update_time_str}\n⏰ 每6分钟自动更新"
        
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
    update_player_cache()