#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import time
from datetime import datetime
from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.permission import SUPERUSER
from loguru import logger

from ..crcon_api import CRCONAPIClient

# 获取配置
from ..config import config
driver = get_driver()

# API配置
CRCON_API_BASE_URL_1 = config.crcon_api_base_url_1
CRCON_API_BASE_URL_2 = config.crcon_api_base_url_2
CRCON_API_TOKEN = config.crcon_api_token

# 系统指令
status_check = on_command("状态", aliases={"status", "机器人状态"}, priority=5)
api_test = on_command("API测试", aliases={"apitest", "测试连接"}, priority=5, permission=SUPERUSER)
bot_restart = on_command("重启机器人", aliases={"restart"}, priority=5, permission=SUPERUSER)

# 启动时间记录
start_time = time.time()


async def test_api_connection(base_url: str, server_name: str) -> dict:
    """测试API连接"""
    try:
        async with CRCONAPIClient(base_url, CRCON_API_TOKEN) as client:
            start = time.time()
            gamestate = await client.get_gamestate()
            response_time = round((time.time() - start) * 1000, 2)
            
            return {
                "status": "✅ 正常",
                "response_time": response_time,
                "players": gamestate.allied_score + gamestate.axis_score if gamestate else 0,
                "error": None
            }
    except Exception as e:
        return {
            "status": "❌ 异常",
            "response_time": 0,
            "players": 0,
            "error": str(e)
        }


@status_check.handle()
async def handle_status_check(bot: Bot, event: Event):
    """处理状态检查"""
    try:
        # 计算运行时间
        uptime_seconds = int(time.time() - start_time)
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime_secs = uptime_seconds % 60
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建状态消息
        message = "🤖 CRCON QQ Bot 状态报告\n"
        message += "=" * 40 + "\n"
        message += f"📅 当前时间：{current_time}\n"
        message += f"⏰ 运行时长：{uptime_hours:02d}:{uptime_minutes:02d}:{uptime_secs:02d}\n"
        message += f"🔗 API连接：检查中...\n\n"
        
        # 发送初始状态
        await status_check.send(message)
        
        # 测试API连接
        tasks = [
            test_api_connection(CRCON_API_BASE_URL_1, "服务器1"),
            test_api_connection(CRCON_API_BASE_URL_2, "服务器2")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 构建详细状态
        detailed_message = "🔗 API连接状态：\n"
        
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                detailed_message += f"  服务器{i}：❌ 连接失败 ({result})\n"
            else:
                detailed_message += f"  服务器{i}：{result['status']}\n"
                if result['status'] == "✅ 正常":
                    detailed_message += f"    响应时间：{result['response_time']}ms\n"
                    detailed_message += f"    在线玩家：{result['players']}人\n"
                else:
                    detailed_message += f"    错误信息：{result['error']}\n"
        
        detailed_message += f"\n💡 使用 /帮助 查看可用指令"
        
        await status_check.finish(detailed_message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"状态检查失败: {e}")
        await status_check.finish("❌ 状态检查失败，请稍后重试")


@api_test.handle()
async def handle_api_test(bot: Bot, event: Event):
    """处理API测试"""
    try:
        await api_test.send("🔍 正在测试API连接...")
        
        # 测试两个服务器的连接
        test_results = []
        
        for i, base_url in enumerate([CRCON_API_BASE_URL_1, CRCON_API_BASE_URL_2], 1):
            try:
                async with CRCONAPIClient(base_url, CRCON_API_TOKEN) as client:
                    # 测试基本连接
                    start = time.time()
                    gamestate = await client.get_gamestate()
                    response_time = round((time.time() - start) * 1000, 2)
                    
                    # 测试玩家列表
                    start = time.time()
                    players = await client.get_players()
                    players_time = round((time.time() - start) * 1000, 2)
                    
                    # 测试VIP查询
                    start = time.time()
                    vips = await client.get_vip_ids()
                    vips_time = round((time.time() - start) * 1000, 2)
                    
                    test_results.append({
                        "server": i,
                        "status": "✅ 正常",
                        "gamestate_time": response_time,
                        "players_time": players_time,
                        "vips_time": vips_time,
                        "players_count": len(players),
                        "vips_count": len(vips),
                        "error": None
                    })
                    
            except Exception as e:
                test_results.append({
                    "server": i,
                    "status": "❌ 异常",
                    "error": str(e)
                })
        
        # 构建测试结果消息
        message = "🧪 API连接测试结果\n"
        message += "=" * 40 + "\n"
        
        for result in test_results:
            message += f"🎮 服务器{result['server']}：{result['status']}\n"
            if result['status'] == "✅ 正常":
                message += f"  游戏状态查询：{result['gamestate_time']}ms\n"
                message += f"  玩家列表查询：{result['players_time']}ms\n"
                message += f"  VIP列表查询：{result['vips_time']}ms\n"
                message += f"  在线玩家数：{result['players_count']}人\n"
                message += f"  VIP用户数：{result['vips_count']}人\n"
            else:
                message += f"  错误信息：{result['error']}\n"
            message += "\n"
        
        await api_test.finish(message)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"API测试失败: {e}")
        await api_test.finish("❌ API测试失败，请检查配置")


@bot_restart.handle()
async def handle_bot_restart(bot: Bot, event: Event):
    """处理机器人重启"""
    try:
        await bot_restart.send("🔄 机器人正在重启...")
        logger.info("管理员请求重启机器人")
        
        # 延迟一秒后退出程序
        await asyncio.sleep(1)
        import sys
        sys.exit(0)
        
    except Exception as e:
        from nonebot.exception import FinishedException
        # 如果是 NoneBot 的 FinishedException，直接重新抛出
        if isinstance(e, FinishedException):
            raise
        logger.error(f"重启失败: {e}")
        await bot_restart.finish("❌ 重启失败")


# 全局异常处理
@driver.on_startup
async def startup_check():
    """启动时检查API连接"""
    logger.info("正在检查API连接...")
    
    for i, base_url in enumerate([CRCON_API_BASE_URL_1, CRCON_API_BASE_URL_2], 1):
        try:
            async with CRCONAPIClient(base_url, CRCON_API_TOKEN) as client:
                await client.get_gamestate()
                logger.success(f"服务器{i} API连接正常")
        except Exception as e:
            logger.error(f"服务器{i} API连接失败: {e}")
    
    logger.info("API连接检查完成")


# 定期健康检查（可选）
from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("interval", minutes=30, id="health_check")
async def health_check():
    """定期健康检查"""
    try:
        for i, base_url in enumerate([CRCON_API_BASE_URL_1, CRCON_API_BASE_URL_2], 1):
            try:
                async with CRCONAPIClient(base_url, CRCON_API_TOKEN) as client:
                    await client.get_gamestate()
            except Exception as e:
                logger.warning(f"健康检查：服务器{i} API连接异常 - {e}")
    except Exception as e:
        logger.error(f"健康检查失败: {e}")