#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.log import logger, default_format
import sys

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 配置日志
logger.add(
    "logs/bot.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format=default_format,
    encoding="utf-8"
)

# 在这里加载插件
nonebot.load_builtin_plugins("echo")  # 内置插件
nonebot.load_plugins("src/plugins")  # 本地插件

# 启动事件
@driver.on_startup
async def startup():
    logger.info("CRCON QQ Bot 启动中...")
    logger.info("正在连接到 CRCON API...")

@driver.on_shutdown
async def shutdown():
    logger.info("CRCON QQ Bot 正在关闭...")

if __name__ == "__main__":
    logger.warning("建议使用 `nb run` 命令启动机器人!")
    nonebot.run()