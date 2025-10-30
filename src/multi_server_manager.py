#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from loguru import logger
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@dataclass
class ServerConfig:
    """服务器配置数据类"""
    server_id: str
    name: str
    display_name: str
    description: str
    api_base_url: str
    api_token: str
    max_players: int
    region: str
    timezone: str
    enabled: bool
    maintenance_mode: bool
    admin_groups: List[str]
    player_groups: List[str]
    custom_params: Dict[str, Any]

@dataclass
class GlobalSettings:
    """全局设置数据类"""
    default_server: str
    api_timeout: int
    api_retry_times: int
    api_retry_delay: float
    enable_cache: bool
    cache_expire_time: int
    enable_auto_health_check: bool
    health_check_interval: int

class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更监听器"""
    
    def __init__(self, manager):
        self.manager = manager
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if event.src_path.endswith('servers_config.yaml'):
            # 防止重复触发
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            
            logger.info("检测到服务器配置文件变更，重新加载配置...")
            self.manager.reload_config()

class MultiServerManager:
    """多服务器管理器"""
    
    def __init__(self, config_file: str = "servers_config.yaml"):
        self.config_file = Path(config_file)
        self.servers: Dict[str, ServerConfig] = {}
        self.server_groups: Dict[str, Dict[str, Any]] = {}
        self.server_aliases: Dict[str, str] = {}
        self.global_settings: Optional[GlobalSettings] = None
        self._lock = threading.RLock()
        self._observer = None
        
        # 加载配置
        self.load_config()
        
        # 启动文件监听
        self.start_file_watcher()
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            with self._lock:
                if not self.config_file.exists():
                    logger.error(f"服务器配置文件不存在: {self.config_file}")
                    return False
                
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                # 解析全局设置
                global_config = config_data.get('global_settings', {})
                self.global_settings = GlobalSettings(
                    default_server=global_config.get('default_server', 'server_1'),
                    api_timeout=global_config.get('api_timeout', 30),
                    api_retry_times=global_config.get('api_retry_times', 3),
                    api_retry_delay=global_config.get('api_retry_delay', 1.0),
                    enable_cache=global_config.get('enable_cache', True),
                    cache_expire_time=global_config.get('cache_expire_time', 300),
                    enable_auto_health_check=global_config.get('enable_auto_health_check', True),
                    health_check_interval=global_config.get('health_check_interval', 5)
                )
                
                # 解析服务器配置
                servers_config = config_data.get('servers', {})
                self.servers.clear()
                
                for server_id, server_data in servers_config.items():
                    # 处理环境变量
                    api_token = server_data.get('api_token', '')
                    if api_token.startswith('${') and api_token.endswith('}'):
                        env_var = api_token[2:-1]
                        api_token = os.getenv(env_var, '')
                    
                    server_config = ServerConfig(
                        server_id=server_id,
                        name=server_data.get('name', f'服务器{server_id}'),
                        display_name=server_data.get('display_name', server_id),
                        description=server_data.get('description', ''),
                        api_base_url=server_data.get('api_base_url', ''),
                        api_token=api_token,
                        max_players=server_data.get('max_players', 100),
                        region=server_data.get('region', 'Unknown'),
                        timezone=server_data.get('timezone', 'UTC'),
                        enabled=server_data.get('enabled', True),
                        maintenance_mode=server_data.get('maintenance_mode', False),
                        admin_groups=server_data.get('admin_groups', []),
                        player_groups=server_data.get('player_groups', []),
                        custom_params=server_data.get('custom_params', {})
                    )
                    
                    self.servers[server_id] = server_config
                
                # 解析服务器组配置
                self.server_groups = config_data.get('server_groups', {})
                
                # 解析服务器别名
                self.server_aliases = config_data.get('server_aliases', {})
                
                logger.info(f"成功加载 {len(self.servers)} 个服务器配置")
                return True
                
        except Exception as e:
            logger.error(f"加载服务器配置失败: {e}")
            return False
    
    def reload_config(self) -> bool:
        """重新加载配置"""
        return self.load_config()
    
    def start_file_watcher(self):
        """启动配置文件监听"""
        try:
            if self._observer:
                self._observer.stop()
                self._observer.join()
            
            self._observer = Observer()
            handler = ConfigFileHandler(self)
            self._observer.schedule(handler, str(self.config_file.parent), recursive=False)
            self._observer.start()
            logger.info("配置文件监听已启动")
            
        except Exception as e:
            logger.error(f"启动配置文件监听失败: {e}")
    
    def stop_file_watcher(self):
        """停止配置文件监听"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("配置文件监听已停止")
    
    def resolve_server_id(self, server_identifier: Union[str, int]) -> Optional[str]:
        """解析服务器标识符为服务器ID"""
        with self._lock:
            # 转换为字符串
            identifier = str(server_identifier)
            
            # 直接匹配服务器ID
            if identifier in self.servers:
                return identifier
            
            # 通过别名匹配
            if identifier in self.server_aliases:
                return self.server_aliases[identifier]
            
            # 通过显示名称匹配
            for server_id, config in self.servers.items():
                if config.display_name == identifier or config.name == identifier:
                    return server_id
            
            return None
    
    def get_server_config(self, server_identifier: Union[str, int]) -> Optional[ServerConfig]:
        """获取服务器配置"""
        server_id = self.resolve_server_id(server_identifier)
        if server_id:
            return self.servers.get(server_id)
        return None
    
    def get_all_servers(self, enabled_only: bool = True) -> Dict[str, ServerConfig]:
        """获取所有服务器配置"""
        with self._lock:
            if enabled_only:
                return {k: v for k, v in self.servers.items() if v.enabled and not v.maintenance_mode}
            return self.servers.copy()
    
    def get_server_list(self, enabled_only: bool = True) -> List[Dict[str, str]]:
        """获取服务器列表（用于显示）"""
        servers = self.get_all_servers(enabled_only)
        result = []
        
        for server_id, config in servers.items():
            result.append({
                'id': server_id,
                'name': config.name,
                'display_name': config.display_name,
                'description': config.description,
                'status': '维护中' if config.maintenance_mode else '正常'
            })
        
        return result
    
    def get_server_group(self, group_name: str) -> Optional[Dict[str, Any]]:
        """获取服务器组配置"""
        return self.server_groups.get(group_name)
    
    def get_servers_in_group(self, group_name: str) -> List[ServerConfig]:
        """获取服务器组中的所有服务器"""
        group = self.get_server_group(group_name)
        if not group:
            return []
        
        servers = []
        for server_id in group.get('servers', []):
            config = self.get_server_config(server_id)
            if config:
                servers.append(config)
        
        return servers
    
    def is_server_enabled(self, server_identifier: Union[str, int]) -> bool:
        """检查服务器是否启用"""
        config = self.get_server_config(server_identifier)
        return config is not None and config.enabled and not config.maintenance_mode
    
    def get_default_server(self) -> Optional[ServerConfig]:
        """获取默认服务器配置"""
        if self.global_settings:
            return self.get_server_config(self.global_settings.default_server)
        return None
    
    def get_api_base_url(self, server_identifier: Union[str, int]) -> Optional[str]:
        """获取服务器API基础URL"""
        config = self.get_server_config(server_identifier)
        return config.api_base_url if config else None
    
    def get_api_token(self, server_identifier: Union[str, int]) -> Optional[str]:
        """获取服务器API令牌"""
        config = self.get_server_config(server_identifier)
        return config.api_token if config else None
    
    def get_server_name(self, server_identifier: Union[str, int]) -> str:
        """获取服务器名称"""
        config = self.get_server_config(server_identifier)
        return config.name if config else f"未知服务器({server_identifier})"
    
    def get_server_display_name(self, server_identifier: Union[str, int]) -> str:
        """获取服务器显示名称"""
        config = self.get_server_config(server_identifier)
        return config.display_name if config else f"未知({server_identifier})"
    
    def validate_server(self, server_identifier: Union[str, int]) -> bool:
        """验证服务器标识符是否有效"""
        return self.resolve_server_id(server_identifier) is not None
    
    def add_server(self, server_config: ServerConfig) -> bool:
        """动态添加服务器配置（仅内存中，不保存到文件）"""
        try:
            with self._lock:
                self.servers[server_config.server_id] = server_config
                logger.info(f"已添加服务器配置: {server_config.name}")
                return True
        except Exception as e:
            logger.error(f"添加服务器配置失败: {e}")
            return False
    
    def remove_server(self, server_identifier: Union[str, int]) -> bool:
        """动态移除服务器配置（仅内存中，不保存到文件）"""
        try:
            with self._lock:
                server_id = self.resolve_server_id(server_identifier)
                if server_id and server_id in self.servers:
                    del self.servers[server_id]
                    logger.info(f"已移除服务器配置: {server_id}")
                    return True
                return False
        except Exception as e:
            logger.error(f"移除服务器配置失败: {e}")
            return False
    
    def __del__(self):
        """析构函数，停止文件监听"""
        self.stop_file_watcher()

# 全局多服务器管理器实例
multi_server_manager = MultiServerManager()