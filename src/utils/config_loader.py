"""
统一配置文件加载器
负责加载和管理 config.yaml 中的所有配置
"""

import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    """统一配置加载器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                logger.error(f"配置文件不存在: {self.config_path}")
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            
            logger.info(f"成功加载配置文件: {self.config_path}")
            
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        
        Args:
            key: 配置键，支持 'section.subsection.key' 格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_global_settings(self) -> Dict[str, Any]:
        """获取全局设置"""
        return self.get('global_settings', {})
    
    def get_servers(self) -> Dict[str, Any]:
        """获取所有服务器配置"""
        return self.get('servers', {})
    
    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定服务器配置
        
        Args:
            server_id: 服务器ID
            
        Returns:
            服务器配置字典，如果不存在返回None
        """
        servers = self.get_servers()
        return servers.get(server_id)
    
    def get_server_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """
        通过别名获取服务器配置
        
        Args:
            alias: 服务器别名
            
        Returns:
            服务器配置字典，如果不存在返回None
        """
        # 先检查别名映射
        aliases = self.get('server_aliases', {})
        server_id = aliases.get(alias, alias)
        
        return self.get_server(server_id)
    
    def get_permission_groups(self) -> Dict[str, Any]:
        """获取所有权限组配置"""
        return self.get('permission_groups', {})
    
    def get_permission_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定权限组配置
        
        Args:
            group_id: 权限组ID
            
        Returns:
            权限组配置字典，如果不存在返回None
        """
        groups = self.get_permission_groups()
        return groups.get(group_id)
    
    def get_server_groups(self) -> Dict[str, Any]:
        """获取服务器组配置"""
        return self.get('server_groups', {})
    
    def get_server_aliases(self) -> Dict[str, str]:
        """获取服务器别名映射"""
        return self.get('server_aliases', {})
    
    def get_features(self) -> Dict[str, Any]:
        """获取功能配置"""
        return self.get('features', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.get('logging', {})
    
    def get_message_templates(self) -> Dict[str, Any]:
        """获取消息模板配置"""
        return self.get('message_templates', {})
    
    def is_server_enabled(self, server_id: str) -> bool:
        """
        检查服务器是否启用
        
        Args:
            server_id: 服务器ID
            
        Returns:
            是否启用
        """
        server_config = self.get_server(server_id)
        if not server_config:
            return False
        
        return server_config.get('enabled', True)
    
    def get_enabled_servers(self) -> List[str]:
        """
        获取所有启用的服务器ID列表
        
        Returns:
            启用的服务器ID列表
        """
        servers = self.get_servers()
        enabled_servers = []
        
        for server_id, config in servers.items():
            if config.get('enabled', True):
                enabled_servers.append(server_id)
        
        return enabled_servers
    
    def get_default_server(self) -> str:
        """
        获取默认服务器ID
        
        Returns:
            默认服务器ID
        """
        return self.get('global_settings.default_server', 'server_1')
    
    def get_default_server_group(self) -> str:
        """
        获取默认服务器组ID
        
        Returns:
            默认服务器组ID
        """
        return self.get('global_settings.default_server_group', 'group_a')
    
    def resolve_server_id(self, server_input: str) -> Optional[str]:
        """
        解析服务器输入，支持ID、别名等
        
        Args:
            server_input: 用户输入的服务器标识
            
        Returns:
            解析后的服务器ID，如果无法解析返回None
        """
        # 如果为空，使用默认服务器
        if not server_input:
            return self.get_default_server()
        
        # 直接检查是否为有效的服务器ID
        if self.get_server(server_input):
            return server_input
        
        # 检查别名映射
        aliases = self.get_server_aliases()
        if server_input in aliases:
            server_id = aliases[server_input]
            if self.get_server(server_id):
                return server_id
        
        return None
    
    def get_servers_in_group(self, group_id: str) -> List[str]:
        """
        获取指定权限组中的所有服务器ID
        
        Args:
            group_id: 权限组ID
            
        Returns:
            服务器ID列表
        """
        group_config = self.get_permission_group(group_id)
        if not group_config:
            return []
        
        game_servers = group_config.get('game_servers', [])
        server_ids = []
        
        for server_info in game_servers:
            if isinstance(server_info, dict):
                server_id = server_info.get('server_id')
                enabled = server_info.get('enabled', True)
                if server_id and enabled:
                    server_ids.append(server_id)
            elif isinstance(server_info, str):
                server_ids.append(server_info)
        
        return server_ids
    
    def format_message(self, template_key: str, **kwargs) -> str:
        """
        格式化消息模板
        
        Args:
            template_key: 模板键，支持 'category.template' 格式
            **kwargs: 模板参数
            
        Returns:
            格式化后的消息
        """
        template = self.get(f'message_templates.{template_key}')
        if not template:
            return f"未找到消息模板: {template_key}"
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"消息模板参数缺失: {e}")
            return template
        except Exception as e:
            logger.error(f"格式化消息模板失败: {e}")
            return template


# 全局配置实例
config = ConfigLoader()

# 便捷函数
def get_config() -> ConfigLoader:
    """获取全局配置实例"""
    return config

def reload_config() -> None:
    """重新加载配置"""
    config.reload()