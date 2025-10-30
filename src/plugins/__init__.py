# -*- coding: utf-8 -*-

# 导入所有插件模块
from . import player_commands
from . import admin_commands
from . import system_commands
from . import enhanced_player_list
from . import server_management
from . import permission_management

__all__ = [
    "player_commands",
    "admin_commands", 
    "system_commands",
    "enhanced_player_list",
    "server_management",
    "permission_management"
]