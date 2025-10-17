#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from pydantic import Field


class Config(BaseSettings):
    """配置类"""
    # NoneBot 配置
    superusers: List[str] = Field(default_factory=list, description="超级用户列表")
    nickname: List[str] = Field(default=["CRCON机器人"], description="机器人昵称")
    command_start: List[str] = Field(default=["/", ""], description="命令前缀")
    command_sep: List[str] = Field(default=["."], description="命令分隔符")
    
    # OneBot 配置
    onebot_ws_urls: List[str] = Field(default=["ws://127.0.0.1:3001"], description="OneBot WebSocket地址")
    onebot_access_token: Optional[str] = Field(default=None, description="OneBot访问令牌")
    
    # CRCON API 配置
    crcon_api_base_url_1: str = Field(default="http://127.0.0.1:8010/api", description="服务器1 API地址")
    crcon_api_base_url_2: str = Field(default="http://127.0.0.1:8011/api", description="服务器2 API地址")
    crcon_api_token: str = Field(default="", description="CRCON API令牌")
    
    # 服务器名称配置
    server_name_1: str = Field(default="服务器1", description="服务器1名称")
    server_name_2: str = Field(default="服务器2", description="服务器2名称")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="logs/bot.log", description="日志文件路径")
    
    # 功能开关
    enable_auto_health_check: bool = Field(default=True, description="启用自动健康检查")
    health_check_interval: int = Field(default=5, description="健康检查间隔(分钟)")
    enable_cache: bool = Field(default=True, description="启用缓存")
    cache_expire_time: int = Field(default=300, description="缓存过期时间(秒)")
    
    # API 请求配置
    api_timeout: int = Field(default=30, description="API请求超时时间(秒)")
    api_retry_times: int = Field(default=3, description="API请求重试次数")
    api_retry_delay: float = Field(default=1.0, description="API请求重试延迟(秒)")
    
    # 权限配置
    admin_groups: List[str] = Field(default_factory=list, description="管理员群组列表")
    player_groups: List[str] = Field(default_factory=list, description="玩家群组列表")
    
    # 环境配置
    environment: str = Field(default="prod", description="环境类型")
    
    # 额外字段（允许但不验证）
    description: Optional[str] = Field(default=None, description="项目描述")
    version: Optional[str] = Field(default=None, description="版本信息")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外字段而不是禁止
        case_sensitive = False


# 全局配置实例
config = Config()


def get_api_base_url(server_num: int = 1) -> str:
    """获取指定服务器的API基础URL"""
    if server_num == 1:
        return config.crcon_api_base_url_1
    elif server_num == 2:
        return config.crcon_api_base_url_2
    else:
        raise ValueError(f"Invalid server number: {server_num}")


def get_server_name(server_num: int = 1) -> str:
    """获取指定服务器的名称"""
    if server_num == 1:
        return config.server_name_1
    elif server_num == 2:
        return config.server_name_2
    else:
        raise ValueError(f"Invalid server number: {server_num}")


def validate_server_num(server_num: int) -> bool:
    """验证服务器编号是否有效"""
    return server_num in [1, 2]


def is_admin_user(user_id: str) -> bool:
    """检查用户是否为管理员"""
    return user_id in config.superusers


def is_admin_group(group_id: str) -> bool:
    """检查群组是否允许使用管理功能"""
    if not config.admin_groups:
        return True  # 如果未配置，则允许所有群组
    return group_id in config.admin_groups


def is_player_group(group_id: str) -> bool:
    """检查群组是否允许使用玩家功能"""
    if not config.player_groups:
        return True  # 如果未配置，则允许所有群组
    return group_id in config.player_groups


# 常量定义
class Constants:
    """常量定义"""
    
    # 地图列表
    COMMON_MAPS = [
        "carentan_warfare", "foy_warfare", "hill400_warfare", "hurtgenforest_warfare",
        "kursk_warfare", "omahabeach_warfare", "purpleheartlane_warfare", 
        "sainte-mere-eglise_warfare", "stalingrad_warfare", "stmariedumont_warfare",
        "utahbeach_warfare", "driel_warfare", "elalamein_warfare", "kharkov_warfare",
        "mortain_warfare", "remagen_warfare"
    ]
    
    # 地图中文名称映射
    MAP_NAMES_CN = {
        "carentan_warfare": "卡朗坦",
        "foy_warfare": "福伊",
        "hill400_warfare": "400高地",
        "hurtgenforest_warfare": "许特根森林",
        "kursk_warfare": "库尔斯克",
        "omahabeach_warfare": "奥马哈海滩",
        "purpleheartlane_warfare": "紫心小道",
        "sainte-mere-eglise_warfare": "圣梅尔埃格利斯",
        "stalingrad_warfare": "斯大林格勒",
        "stmariedumont_warfare": "圣玛丽杜蒙",
        "utahbeach_warfare": "犹他海滩",
        "driel_warfare": "德里尔",
        "elalamein_warfare": "阿拉曼",
        "kharkov_warfare": "哈尔科夫",
        "mortain_warfare": "莫尔坦",
        "remagen_warfare": "雷马根"
    }
    
    # 队伍名称映射
    TEAM_NAMES = {
        "Allies": "盟军",
        "Axis": "轴心"
    }
    
    # 错误消息
    ERROR_MESSAGES = {
        "api_connection_failed": "❌ API连接失败，请稍后重试",
        "invalid_server_num": "❌ 服务器编号只能是1或2",
        "no_players_online": "❌ 当前没有在线玩家",
        "invalid_index_format": "❌ 序号格式错误，请使用如：1 或 1-5 或 1,3,5-7",
        "index_out_of_range": "❌ 序号超出范围",
        "permission_denied": "❌ 权限不足，需要管理员权限",
        "invalid_parameters": "❌ 参数错误，请检查输入格式",
        "operation_failed": "❌ 操作失败，请稍后重试"
    }
    
    # 成功消息
    SUCCESS_MESSAGES = {
        "operation_completed": "✅ 操作完成",
        "player_kicked": "✅ 玩家已被踢出",
        "player_banned": "✅ 玩家已被封禁",
        "player_switched": "✅ 玩家已调边",
        "map_changed": "✅ 地图已更换",
        "setting_updated": "✅ 设置已更新"
    }


# 导出配置和常量
__all__ = [
    "Config", "config", "Constants",
    "get_api_base_url", "get_server_name", "validate_server_num",
    "is_admin_user", "is_admin_group", "is_player_group"
]