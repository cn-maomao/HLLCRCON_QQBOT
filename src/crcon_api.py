#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from loguru import logger


@dataclass
class GameState:
    """游戏状态数据类"""
    allied_players: int
    axis_players: int
    allied_score: int
    axis_score: int
    remaining_time: str
    current_map: str
    next_map: str
    time_remaining: Optional[float] = None  # 添加缺失的属性


@dataclass
class Player:
    """玩家数据类"""
    name: str
    player_id: str
    team: str
    role: str
    level: int
    kills: int
    deaths: int
    score: int
    time_seconds: int


@dataclass
class VipInfo:
    """VIP信息数据类"""
    player_id: str
    name: str
    expiration: Optional[str]
    description: str


class CRCONAPIClient:
    """CRCON API客户端"""
    
    def __init__(self, base_url: str, api_token: str):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            api_token: API认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=data) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                async with self.session.post(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"API请求失败: {url}  错误: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise
    
    async def get_gamestate(self) -> GameState:
        """
        获取游戏状态
        
        Returns:
            游戏状态信息
        """
        response = await self._request("GET", "get_gamestate")
        result = response.get("result", {})
        
        return GameState(
            allied_players=result.get("num_allied_players", 0),
            axis_players=result.get("num_axis_players", 0),
            allied_score=result.get("allied_score", 0),
            axis_score=result.get("axis_score", 0),
            remaining_time=result.get("raw_time_remaining", ""),
            current_map=result.get("current_map", ""),
            next_map=result.get("next_map", ""),
            time_remaining=result.get("time_remaining", 0.0)
        )
    
    async def get_players(self) -> List[Player]:
        """
        获取在线玩家列表
        
        Returns:
            玩家列表
        """
        response = await self._request("GET", "get_players")
        players_data = response.get("result", [])
        
        players = []
        for player_data in players_data:
            players.append(Player(
                name=player_data.get("name", ""),
                player_id=player_data.get("player_id", ""),
                team=player_data.get("team", ""),
                role=player_data.get("role", ""),
                level=player_data.get("level", 0),
                kills=player_data.get("kills", 0),
                deaths=player_data.get("deaths", 0),
                score=player_data.get("score", 0),
                time_seconds=player_data.get("time_seconds", 0)
            ))
        
        return players
    
    async def get_player_info(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定玩家的详细信息
        
        Args:
            player_id: 玩家ID (Steam ID 64)
            
        Returns:
            玩家信息字典，如果未找到则返回None
        """
        try:
            response = await self._request("GET", "get_player_info", {"player_id": player_id})
            return response.get("result")
        except Exception as e:
            logger.error(f"获取玩家信息失败: {e}")
            return None

    async def get_detailed_player_info(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定玩家的详细信息
        
        Args:
            player_id: 玩家ID (Steam ID 64)
            
        Returns:
            详细玩家信息字典，如果未找到则返回None
        """
        try:
            response = await self._request("GET", "get_detailed_player_info", {"player_id": player_id})
            return response.get("result")
        except Exception as e:
            logger.error(f"获取详细玩家信息失败: {e}")
            return None

    async def get_players_history(self, player_id: Optional[str] = None, 
                                 player_name: Optional[str] = None,
                                 page: int = 1, 
                                 page_size: int = 500,
                                 exact_name_match: bool = False,
                                 ignore_accent: bool = True) -> Optional[Dict[str, Any]]:
        """
        获取玩家历史记录
        
        Args:
            player_id: 玩家ID（可选）
            player_name: 玩家名称（可选）
            page: 页码，默认为1
            page_size: 每页大小，默认为500
            exact_name_match: 是否精确匹配名称，默认为False
            ignore_accent: 是否忽略重音符号，默认为True
            
        Returns:
            玩家历史记录数据，如果失败返回None
        """
        try:
            data = {
                "page": page,
                "page_size": page_size,
                "exact_name_match": str(exact_name_match).lower(),
                "ignore_accent": str(ignore_accent).lower()
            }
            
            if player_id:
                data["player_id"] = player_id
            if player_name:
                data["player_name"] = player_name
            
            response = await self._request("POST", "get_players_history", data)
            return response.get("result")
        except Exception as e:
            logger.error(f"获取玩家历史记录失败: {e}")
            return None

    async def get_vip_ids(self) -> List[VipInfo]:
        """
        获取VIP玩家列表
        
        Returns:
            VIP玩家信息列表
        """
        response = await self._request("GET", "get_vip_ids")
        vips_data = response.get("result", [])
        
        vips = []
        for vip_data in vips_data:
            vips.append(VipInfo(
                player_id=vip_data.get("player_id", ""),
                name=vip_data.get("name", ""),
                expiration=vip_data.get("expiration"),
                description=vip_data.get("description", "")
            ))
        
        return vips
    
    async def kick_player(self, player_id: str, reason: str = "", by: str = "QQ机器人") -> bool:
        """
        踢出玩家
        
        Args:
            player_id: 玩家ID
            reason: 踢出原因
            by: 操作者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "reason": reason,
            "by": by
        }
        
        response = await self._request("POST", "kick", data)
        return response.get("result", False)
    
    async def temp_ban_player(self, player_id: str, duration_hours: int = 2, 
                             reason: str = "", by: str = "QQ机器人") -> bool:
        """
        临时封禁玩家
        
        Args:
            player_id: 玩家ID
            duration_hours: 封禁时长（小时）
            reason: 封禁原因
            by: 操作者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "duration_hours": duration_hours,
            "reason": reason,
            "by": by
        }
        
        response = await self._request("POST", "temp_ban", data)
        return response.get("result", False)
    
    async def perma_ban_player(self, player_id: str, reason: str = "", by: str = "QQ机器人") -> bool:
        """
        永久封禁玩家
        
        Args:
            player_id: 玩家ID
            reason: 封禁原因
            by: 操作者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "reason": reason,
            "by": by
        }
        
        response = await self._request("POST", "perma_ban", data)
        return response.get("result", False)
    
    async def punish_player(self, player_id: str, reason: str = "", by: str = "QQ机器人") -> bool:
        """
        惩罚玩家（管理员击杀）
        
        Args:
            player_id: 玩家ID
            reason: 惩罚原因
            by: 操作者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "reason": reason,
            "by": by
        }
        
        response = await self._request("POST", "punish", data)
        return response.get("result", False)
    
    async def switch_player_now(self, player_id: str) -> bool:
        """
        立即调边玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            操作是否成功
        """
        data = {"player_id": player_id}
        response = await self._request("POST", "switch_player_now", data)
        return response.get("result", False)
    
    async def switch_player_on_death(self, player_id: str, by: str = "QQ机器人") -> bool:
        """
        死后调边玩家
        
        Args:
            player_id: 玩家ID
            by: 操作者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "by": by
        }
        
        response = await self._request("POST", "switch_player_on_death", data)
        return response.get("result", False)
    
    async def set_map(self, map_name: str) -> bool:
        """
        更换地图
        
        Args:
            map_name: 地图名称
            
        Returns:
            操作是否成功
        """
        data = {"map_name": map_name}
        try:
            response = await self._request("POST", "set_map", data)
            logger.info(f"set_map API响应: {response}")
            
            # 检查响应结构
            if "result" in response:
                # 根据测试结果，即使result为None，命令也可能已经执行成功
                # 只要API调用没有失败（failed=False），就认为命令已执行
                failed = response.get("failed", True)
                error = response.get("error")
                
                # 如果没有失败且没有错误，认为命令已执行
                if not failed and error is None:
                    return True
                else:
                    logger.warning(f"set_map可能失败: failed={failed}, error={error}")
                    return False
            else:
                logger.error(f"set_map API响应缺少result字段: {response}")
                return False
                
        except Exception as e:
            logger.error(f"set_map API调用失败: {e}")
            return False
    
    async def get_map_rotation(self) -> List[str]:
        """
        获取地图轮换列表
        
        Returns:
            地图列表
        """
        response = await self._request("GET", "get_map_rotation")
        return response.get("result", [])
    
    async def get_team_objective_scores(self) -> tuple[int, int]:
        """
        获取队伍点位得分 (盟军, 轴心)
        
        Returns:
            队伍点位得分元组
        """
        try:
            response = await self._request("GET", "get_team_objective_scores")
            result = response.get("result", (0, 0))
            return tuple(result) if isinstance(result, (list, tuple)) else (0, 0)
        except Exception as e:
            logger.error(f"获取队伍点位得分失败: {e}")
            return (0, 0)
    
    async def get_autobalance_enabled(self) -> bool:
        """
        获取自动平衡是否启用
        
        Returns:
            自动平衡启用状态
        """
        try:
            response = await self._request("GET", "get_autobalance_enabled")
            return response.get("result", False)
        except Exception as e:
            logger.error(f"获取自动平衡状态失败: {e}")
            return False
    
    async def set_autobalance_enabled(self, enabled: bool) -> bool:
        """
        设置自动平衡启用状态
        
        Args:
            enabled: 是否启用自动平衡
            
        Returns:
            操作是否成功
        """
        try:
            data = {"value": enabled}
            response = await self._request("POST", "set_autobalance_enabled", data)
            return response.get("result", False)
        except Exception as e:
            logger.error(f"设置自动平衡状态失败: {e}")
            return False
    
    async def get_autobalance_threshold(self) -> int:
        """
        获取自动平衡阈值
        
        Returns:
            自动平衡阈值
        """
        try:
            response = await self._request("GET", "get_autobalance_threshold")
            return response.get("result", 0)
        except Exception as e:
            logger.error(f"获取自动平衡阈值失败: {e}")
            return 0
    
    async def set_autobalance_threshold(self, threshold: int) -> bool:
        """
        设置自动平衡阈值
        
        Args:
            threshold: 自动平衡阈值
            
        Returns:
            操作是否成功
        """
        try:
            data = {"max_diff": threshold}
            response = await self._request("POST", "set_autobalance_threshold", data)
            return response.get("result", False)
        except Exception as e:
            logger.error(f"设置自动平衡阈值失败: {e}")
            return False
    
    async def get_team_switch_cooldown(self) -> int:
        """
        获取调边冷却时间（分钟）
        
        Returns:
            调边冷却时间
        """
        try:
            response = await self._request("GET", "get_team_switch_cooldown")
            return response.get("result", 0)
        except Exception as e:
            logger.error(f"获取调边冷却时间失败: {e}")
            return 0
    
    async def set_team_switch_cooldown(self, minutes: int) -> bool:
        """
        设置调边冷却时间（分钟）
        
        Args:
            minutes: 冷却时间（分钟）
            
        Returns:
            操作是否成功
        """
        try:
            data = {"minutes": minutes}
            response = await self._request("POST", "set_team_switch_cooldown", data)
            return response.get("result", False)
        except Exception as e:
            logger.error(f"设置调边冷却时间失败: {e}")
            return False
    
    async def get_idle_autokick_time(self) -> int:
        """
        获取闲置踢出时间
        
        Returns:
            闲置时间（秒）
        """
        response = await self._request("GET", "get_idle_autokick_time")
        return response.get("result", 0)
    
    async def set_idle_autokick_time(self, minutes: int) -> bool:
        """
        设置闲置踢出时间
        
        Args:
            minutes: 闲置时间（分钟）
            
        Returns:
            操作是否成功
        """
        data = {"minutes": minutes}
        response = await self._request("POST", "set_idle_autokick_time", data)
        return response.get("result", False)
    
    async def message_player(self, player_id: str, message: str, by: str = "QQ机器人") -> bool:
        """
        向玩家发送消息
        
        Args:
            player_id: 玩家ID
            message: 消息内容
            by: 发送者
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "message": message,
            "by": by
        }
        
        response = await self._request("POST", "message_player", data)
        return response.get("result", False)
    
    async def add_vip(self, player_id: str, description: str = "", expiration: Optional[str] = None) -> bool:
        """
        添加VIP玩家
        
        Args:
            player_id: 玩家ID
            description: VIP描述
            expiration: 过期时间（可选，格式：YYYY-MM-DD HH:MM:SS）
            
        Returns:
            操作是否成功
        """
        data = {
            "player_id": player_id,
            "description": description
        }
        
        if expiration:
            data["expiration"] = expiration
        
        response = await self._request("POST", "add_vip", data)
        return response.get("result", False)
    
    async def remove_vip(self, player_id: str) -> bool:
        """
        删除VIP玩家
        
        Args:
            player_id: 玩家ID
            
        Returns:
            操作是否成功
        """
        data = {"player_id": player_id}
        response = await self._request("POST", "remove_vip", data)
        return response.get("result", False)

    async def get_objective_rows(self) -> List[List[str]]:
        """
        获取当前地图的点位行信息
        
        Returns:
            二维列表，每行包含该行的点位名称
        """
        response = await self._request("GET", "get_objective_rows")
        return response.get("result", [])

    async def set_game_layout(self, objectives: List[Union[str, int, None]], 
                             random_constraints: int = 0) -> bool:
        """
        设置地图点位布局
        
        Args:
            objectives: 点位设置列表，每个元素可以是:
                       - None: 中立点位
                       - 0 或 "axis": 轴心控制
                       - 1 或 "allied": 盟军控制
            random_constraints: 随机约束标志，默认为0
            
        Returns:
            操作是否成功
        """
        data = {
            "objectives": objectives,
            "random_constraints": str(random_constraints)
        }
        response = await self._request("POST", "set_game_layout", data)
        return response.get("result", True)  # 如果没有返回结果，默认认为成功