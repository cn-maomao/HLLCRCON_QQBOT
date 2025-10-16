#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CRCON QQ Bot 测试脚本
用于测试机器人功能和API连接
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.crcon_api import CRCONAPIClient
from src.config import config, get_api_base_url, Constants


async def test_api_connection():
    """测试API连接"""
    print("🔍 测试API连接...")
    
    for server_num in [1, 2]:
        print(f"\n📡 测试服务器{server_num}...")
        base_url = get_api_base_url(server_num)
        
        try:
            async with CRCONAPIClient(base_url, config.crcon_api_token) as client:
                # 测试游戏状态
                gamestate = await client.get_gamestate()
                print(f"  ✅ 游戏状态: {gamestate.current_map} - {gamestate.allied_score}:{gamestate.axis_score}")
                
                # 测试玩家列表
                players = await client.get_players()
                print(f"  ✅ 在线玩家: {len(players)}人")
                
                # 测试VIP列表
                vips = await client.get_vip_ids()
                print(f"  ✅ VIP用户: {len(vips)}人")
                
                # 测试地图轮换
                rotation = await client.get_map_rotation()
                print(f"  ✅ 地图轮换: {len(rotation)}张地图")
                
        except Exception as e:
            print(f"  ❌ 连接失败: {e}")


async def test_data_parsing():
    """测试数据解析"""
    print("\n🧪 测试数据解析...")
    
    try:
        base_url = get_api_base_url(1)
        async with CRCONAPIClient(base_url, config.crcon_api_token) as client:
            # 测试玩家数据解析
            players = await client.get_players()
            if players:
                player = players[0]
                print(f"  ✅ 玩家数据: {player.name} ({player.team}) K:{player.kills} D:{player.deaths}")
            
            # 测试游戏状态解析
            gamestate = await client.get_gamestate()
            if gamestate:
                print(f"  ✅ 游戏状态: {gamestate.current_map}")
                print(f"    盟军: {gamestate.allied_score} 轴心: {gamestate.axis_score}")
                print(f"    时间: {gamestate.time_remaining}")
            
    except Exception as e:
        print(f"  ❌ 数据解析失败: {e}")


def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    print(f"  API Token: {'已配置' if config.crcon_api_token else '未配置'}")
    print(f"  服务器1 URL: {config.crcon_api_base_url_1}")
    print(f"  服务器2 URL: {config.crcon_api_base_url_2}")
    print(f"  超级用户: {len(config.superusers)}个")
    print(f"  日志级别: {config.log_level}")
    
    # 测试常量
    print(f"  常用地图: {len(Constants.COMMON_MAPS)}张")
    print(f"  地图中文名: {len(Constants.MAP_NAMES_CN)}个")


def test_utils():
    """测试工具函数"""
    print("\n🔧 测试工具函数...")
    
    # 简单的序号解析测试（不导入NoneBot模块）
    def parse_range(range_str: str) -> list:
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
    
    # 测试序号解析
    test_cases = [
        "1",
        "1-5", 
        "1,3,5",
        "1-3,5,7-9"
    ]
    
    for case in test_cases:
        try:
            result = parse_range(case)
            print(f"  ✅ '{case}' -> {result}")
        except Exception as e:
            print(f"  ❌ '{case}' -> {e}")


async def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    # 测试无效API Token
    try:
        async with CRCONAPIClient(get_api_base_url(1), "invalid_token") as client:
            await client.get_gamestate()
    except Exception as e:
        print(f"  ✅ 无效Token错误处理: {type(e).__name__}")
    
    # 测试无效URL
    try:
        async with CRCONAPIClient("http://invalid.url/api", config.crcon_api_token) as client:
            await client.get_gamestate()
    except Exception as e:
        print(f"  ✅ 无效URL错误处理: {type(e).__name__}")


def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖...")
    
    required_packages = [
        "nonebot2",
        "requests",
        "aiohttp",
        "pydantic",
        "python-dotenv",
        "loguru"
    ]
    
    for package in required_packages:
        try:
            if package == "nonebot2":
                import nonebot
            elif package == "python-dotenv":
                import dotenv
            else:
                __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 未安装")


def check_files():
    """检查文件结构"""
    print("\n📁 检查文件结构...")
    
    required_files = [
        "bot.py",
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
        "src/__init__.py",
        "src/config.py",
        "src/crcon_api.py",
        "src/plugins/__init__.py",
        "src/plugins/player_commands.py",
        "src/plugins/admin_commands.py",
        "src/plugins/system_commands.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - 缺失")


async def main():
    """主测试函数"""
    print("🤖 CRCON QQ Bot 测试开始")
    print("=" * 50)
    
    # 检查基础环境
    check_dependencies()
    check_files()
    test_config()
    test_utils()
    
    # 检查API连接（需要有效的API Token）
    if config.crcon_api_token and config.crcon_api_token != "your_api_token_here":
        await test_api_connection()
        await test_data_parsing()
        await test_error_handling()
    else:
        print("\n⚠️ 跳过API测试 - 请先配置有效的API Token")
    
    print("\n✅ 测试完成!")
    print("\n💡 使用说明:")
    print("1. 复制 .env.example 为 .env")
    print("2. 配置 .env 文件中的API Token和其他参数")
    print("3. 安装依赖: pip install -r requirements.txt")
    print("4. 启动机器人: nb run 或 python bot.py")


if __name__ == "__main__":
    asyncio.run(main())