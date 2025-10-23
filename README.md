# CRCON QQ Bot

一个用于 Hell Let Loose CRCON 管理面板的 QQ 机器人，支持服务器状态查询、玩家管理、地图管理等功能。

## 功能特性

### 🎮 玩家功能
- **服务器信息查询** - 查看服务器状态、在线玩家数、当前地图等
- **VIP状态查询** - 通过玩家名称查询VIP状态
- **帮助指令** - 查看可用指令列表

### 🛡️ 管理功能
本机器人采用三级权限管理系统：

#### 🔴 主人权限 (OWNER)
- 拥有所有系统权限和管理员权限
- 可以执行系统命令（重启机器人、API测试等）
- 配置方式：在 `.env` 文件中设置 `SUPERUSERS`

#### 🟡 超级管理员权限 (SUPER_ADMIN)
- 拥有所有管理员命令权限
- 可以添加/删除普通管理员
- 可以查看权限信息和管理员列表

#### 🟢 普通管理员权限 (ADMIN)
- **玩家管理**
  - 查看在线玩家列表
  - 管理员击杀（punish）
  - 踢出玩家
  - 封禁玩家（临时/永久）
  - 调边玩家（立即/死后）
- **消息管理**
  - 私信玩家
  - 全体私信
- **地图管理**
  - 更换地图
  - 查看地图轮换
  - 设置地图点位
- **VIP管理**
  - 查询VIP状态
  - 添加/删除VIP
- **服务器设置**
  - 设置闲置踢出时间
  - 查看服务器设置
  - 设置自动平衡

### 🔧 系统功能
- **健康检查** - 定期检查API连接状态
- **日志记录** - 完整的操作日志
- **错误处理** - 友好的错误提示和异常处理

## 安装部署

### 环境要求
- Python 3.8+
- Hell Let Loose CRCON 管理面板
- OneBot 协议的 QQ 机器人框架（如 go-cqhttp）

### 1. 克隆项目
```bash
git clone https://github.com/cn-maomao/HLL_CRCON_QQBOT.git
cd HLL_CRCON_QQBOT
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制配置文件模板
cp .env.example .env

# 编辑配置文件
nano .env
```

### 4. 配置说明

#### 基础配置
```env
# 超级用户QQ号（管理员）
SUPERUSERS=["123456789", "987654321"]

# 机器人昵称
NICKNAME=["CRCON机器人", "crcon"]

# 指令前缀
COMMAND_START=["/", ""]
```

#### OneBot 配置
```env
# OneBot WebSocket 地址
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]
```

#### CRCON API 配置
```env
# 服务器1 API地址
CRCON_API_BASE_URL_1=http://your-server1:8010/api

# 服务器2 API地址  
CRCON_API_BASE_URL_2=http://your-server2:8011/api

# API 访问令牌
CRCON_API_TOKEN=your_api_token_here
```

### 5. 启动机器人
```bash
# 推荐使用 nb 命令启动
nb run

# 或直接运行
python bot.py
```

## 使用指南

### 玩家指令

| 指令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/服务器信息` | `/server`, `/status` | 查看服务器状态 | `/服务器信息 1` |
| `/查询vip` | `/vip查询`, `/checkvip` | 查询VIP状态 | `/查询vip PlayerName` |
| `/帮助` | `/help`, `/指令` | 查看指令帮助 | `/帮助` |

### 管理指令

#### 普通管理员权限

#### 玩家管理
| 指令 | 说明 | 示例 |
|------|------|------|
| `/玩家列表` | 查看在线玩家 | `/玩家列表 1` |
| `/击杀` | 管理员击杀 | `/击杀 1-5 1 违规行为` |
| `/踢出` | 踢出玩家 | `/踢出 3 1 违反规则` |
| `/封禁` | 封禁玩家 | `/封禁 2 24 1 恶意破坏` |
| `/立即调边` | 立即调边 | `/立即调边 1,3,5 1` |
| `/死后调边` | 死后调边 | `/死后调边 2-4 1` |

#### 地图管理
| 指令 | 说明 | 示例 |
|------|------|------|
| `/换图` | 更换地图 | `/换图 foy_warfare 1` |

#### 服务器设置
| 指令 | 说明 | 示例 |
|------|------|------|
| `/设置闲置时间` | 设置闲置踢出时间 | `/设置闲置时间 15 1` |

#### 系统管理
| 指令 | 说明 | 示例 |
|------|------|------|
| `/状态` | 查看机器人状态 | `/状态` |
| `/API测试` | 测试API连接 | `/API测试` |
| `/重启机器人` | 重启机器人 | `/重启机器人` |

### 参数说明

#### 序号格式
支持多种序号格式：
- 单个序号：`1`
- 范围序号：`1-5`（表示1到5）
- 多个序号：`1,3,5`
- 混合格式：`1-3,5,7-9`

#### 服务器编号
- `1` - 服务器1
- `2` - 服务器2
- 默认为服务器1

#### 封禁时长
- 数字 - 小时数（如 `24` 表示24小时）
- `永久` - 永久封禁

#### 超级管理员权限

| 指令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/添加管理员` | `/addadmin`, `/管理员添加` | 添加普通管理员 | `/添加管理员 123456789` |
| `/删除管理员` | `/removeadmin`, `/管理员删除` | 删除普通管理员 | `/删除管理员 123456789` |
| `/管理员列表` | `/listadmins`, `/查看管理员` | 查看管理员列表 | `/管理员列表` |
| `/权限信息` | `/perminfo`, `/查看权限` | 查看权限信息 | `/权限信息 123456789` |

#### 系统命令（主人权限）

| 指令 | 别名 | 说明 | 示例 |
|------|------|------|------|
| `/状态` | `/status`, `/机器人状态` | 查看机器人状态 | `/状态` |
| `/API测试` | `/apitest`, `/测试连接` | 测试API连接 | `/API测试` |
| `/重启机器人` | `/restart` | 重启机器人 | `/重启机器人` |

## 常用地图列表

| 编号 | 地图名称 | 中文名称 |
|------|----------|----------|
| 1 | carentan_warfare | 卡朗坦 |
| 2 | foy_warfare | 福伊 |
| 3 | hill400_warfare | 400高地 |
| 4 | hurtgenforest_warfare | 许特根森林 |
| 5 | kursk_warfare | 库尔斯克 |
| 6 | omahabeach_warfare | 奥马哈海滩 |
| 7 | purpleheartlane_warfare | 紫心小道 |
| 8 | sainte-mere-eglise_warfare | 圣梅尔埃格利斯 |
| 9 | stalingrad_warfare | 斯大林格勒 |
| 10 | stmariedumont_warfare | 圣玛丽杜蒙 |
| 11 | utahbeach_warfare | 犹他海滩 |
| 12 | driel_warfare | 德里尔 |
| 13 | elalamein_warfare | 阿拉曼 |
| 14 | kharkov_warfare | 哈尔科夫 |
| 15 | mortain_warfare | 莫尔坦 |
| 16 | remagen_warfare | 雷马根 |

## 故障排除

### 常见问题

#### 1. API连接失败
- 检查 CRCON API 地址是否正确
- 确认 API Token 是否有效
- 验证网络连接是否正常

#### 2. 权限不足
- 确认您的权限级别是否足够
- 普通管理员：由超级管理员或主人添加
- 超级管理员：由主人添加
- 主人：在 `.env` 文件中设置 `SUPERUSERS`

#### 3. 机器人无响应
- 检查 OneBot 连接是否正常
- 确认机器人是否正确启动
- 查看日志文件排查错误

### 日志查看
```bash
# 查看实时日志
tail -f logs/bot.log

# 查看错误日志
grep "ERROR" logs/bot.log
```

### 测试连接
```bash
# 运行测试脚本
python test_bot.py
```

## 开发说明

### 项目结构
```
CRCON_QQBOT/
├── bot.py                 # 机器人主程序
├── requirements.txt       # 依赖包列表
├── pyproject.toml        # 项目配置
├── .env.example          # 环境变量模板
├── test_bot.py           # 测试脚本
├── src/
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   ├── crcon_api.py      # CRCON API客户端
│   └── plugins/          # 插件目录
│       ├── __init__.py
│       ├── player_commands.py    # 玩家功能
│       ├── admin_commands.py     # 管理功能
│       └── system_commands.py    # 系统功能
└── logs/                 # 日志目录
```

### 添加新功能
1. 在相应的插件文件中添加新的指令处理器
2. 在 `crcon_api.py` 中添加新的API方法（如需要）
3. 更新配置文件和文档

### API权限
机器人需要以下CRCON API权限：
- `api.can_view_get_gamestate` - 查看游戏状态
- `api.can_view_get_players` - 查看玩家列表
- `api.can_view_vip_ids` - 查看VIP列表
- `api.can_kick_players` - 踢出玩家
- `api.can_temp_ban_players` - 临时封禁
- `api.can_perma_ban_players` - 永久封禁
- `api.can_punish_players` - 惩罚玩家
- `api.can_switch_players_immediately` - 立即调边
- `api.can_switch_players_on_death` - 死后调边
- `api.can_change_current_map` - 更换地图
- `api.can_change_idle_autokick_time` - 设置闲置时间

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 支持

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**注意：使用本机器人需要确保遵守相关服务器规则和法律法规。**