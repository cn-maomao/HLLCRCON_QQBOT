# CRCON QQ Bot 安装部署指南

本文档提供详细的安装和部署步骤，帮助您快速搭建 CRCON QQ 机器人。

## 前置要求

### 系统要求
- **操作系统**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.15+
- **Python**: 3.8 或更高版本
- **内存**: 至少 512MB 可用内存
- **存储**: 至少 100MB 可用空间

### 服务要求
- **CRCON 管理面板**: 需要有可访问的 CRCON API 接口
- **QQ 机器人框架**: 支持 OneBot 协议的框架（推荐 go-cqhttp）
- **网络**: 机器人服务器需要能访问 CRCON API 和 QQ 服务

## 第一步：环境准备

### 1.1 安装 Python

#### Windows
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.8+ 版本
3. 安装时勾选 "Add Python to PATH"
4. 验证安装：
```cmd
python --version
pip --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

#### macOS
```bash
# 使用 Homebrew
brew install python3
python3 --version
pip3 --version
```

### 1.2 安装 Git（可选）
如果需要从 Git 仓库克隆项目：

#### Windows
下载并安装 [Git for Windows](https://git-scm.com/download/win)

#### Linux
```bash
sudo apt install git
```

#### macOS
```bash
brew install git
```

## 第二步：获取项目代码

### 方法一：Git 克隆（推荐）
```bash
git clone <repository-url>
cd CRCON_QQBOT
```

### 方法二：下载压缩包
1. 下载项目压缩包
2. 解压到目标目录
3. 进入项目目录

## 第三步：安装依赖

### 3.1 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3.2 安装 Python 依赖
```bash
pip install -r requirements.txt
```

如果安装过程中遇到网络问题，可以使用国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3.3 验证安装
```bash
python test_bot.py
```

## 第四步：配置 QQ 机器人

### 4.1 安装 go-cqhttp

#### 下载 go-cqhttp
1. 访问 [go-cqhttp Releases](https://github.com/Mrs4s/go-cqhttp/releases)
2. 下载适合您系统的版本
3. 解压到独立目录

#### 配置 go-cqhttp
1. 首次运行 go-cqhttp 生成配置文件
2. 编辑 `config.yml`：

```yaml
# go-cqhttp 配置示例
account:
  uin: 你的QQ号
  password: '你的QQ密码'
  encrypt: false
  status: 0
  relogin:
    delay: 3
    count: 3
    interval: 3

heartbeat:
  interval: 5

message:
  post-format: string
  ignore-invalid-cqcode: false
  force-fragment: false
  fix-url: false
  proxy-rewrite: ''
  report-self-message: false
  remove-reply-at: false
  extra-reply-data: false
  skip-mime-scan: false

output:
  log-level: warn
  log-aging: 15
  log-force-new: true
  log-colorful: true
  debug: false

default-middlewares: &default
  access-token: ''
  filter: ''
  rate-limit:
    enabled: false
    frequency: 1
    bucket: 1

database:
  leveldb:
    enable: true

servers:
  - ws:
      address: 127.0.0.1:3001
      middlewares:
        <<: *default
```

3. 启动 go-cqhttp：
```bash
./go-cqhttp
```

### 4.2 配置机器人

#### 创建配置文件
```bash
cp .env.example .env
```

#### 编辑配置文件
使用文本编辑器编辑 `.env` 文件：

```env
# QQ机器人基础配置
SUPERUSERS=["你的QQ号"]
NICKNAME=["CRCON机器人", "crcon"]
COMMAND_START=["/", ""]

# OneBot 连接配置
ONEBOT_WS_URLS=["ws://127.0.0.1:3001"]

# CRCON API 配置
CRCON_API_BASE_URL_1=http://你的服务器IP:8010/api
CRCON_API_BASE_URL_2=http://你的服务器IP:8011/api
CRCON_API_TOKEN=你的API令牌

# 日志配置
LOG_LEVEL=INFO
```

## 第五步：获取 CRCON API 令牌

### 5.1 登录 CRCON 管理面板
1. 打开浏览器访问 CRCON 管理面板
2. 使用管理员账号登录

### 5.2 生成 API 令牌
1. 进入 "Settings" -> "API Keys"
2. 点击 "Create New API Key"
3. 设置权限（建议勾选以下权限）：
   - `api.can_view_get_gamestate`
   - `api.can_view_get_players`
   - `api.can_view_vip_ids`
   - `api.can_kick_players`
   - `api.can_temp_ban_players`
   - `api.can_perma_ban_players`
   - `api.can_punish_players`
   - `api.can_switch_players_immediately`
   - `api.can_switch_players_on_death`
   - `api.can_change_current_map`
   - `api.can_change_idle_autokick_time`
4. 复制生成的令牌到配置文件

## 第六步：启动机器人

### 6.1 测试配置
```bash
python test_bot.py
```

确保所有测试项都显示 ✅

### 6.2 启动机器人
```bash
# 推荐方式
nb run

# 或者直接运行
python bot.py
```

### 6.3 验证运行
1. 机器人启动后，在 QQ 中向机器人发送 `/状态`
2. 如果收到状态报告，说明配置成功

## 第七步：进程管理（生产环境）

### 7.1 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/crcon-qqbot.service`：

```ini
[Unit]
Description=CRCON QQ Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/CRCON_QQBOT
Environment=PATH=/path/to/CRCON_QQBOT/venv/bin
ExecStart=/path/to/CRCON_QQBOT/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable crcon-qqbot
sudo systemctl start crcon-qqbot
```

### 7.2 使用 PM2（跨平台）

安装 PM2：
```bash
npm install -g pm2
```

创建 PM2 配置文件 `ecosystem.config.js`：
```javascript
module.exports = {
  apps: [{
    name: 'crcon-qqbot',
    script: 'bot.py',
    interpreter: 'python',
    cwd: '/path/to/CRCON_QQBOT',
    env: {
      NODE_ENV: 'production'
    },
    restart_delay: 10000,
    max_restarts: 10
  }]
}
```

启动：
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 故障排除

### 常见问题及解决方案

#### 1. Python 版本问题
**错误**: `SyntaxError` 或版本不兼容
**解决**: 确保使用 Python 3.8+

#### 2. 依赖安装失败
**错误**: `pip install` 失败
**解决**: 
- 使用国内镜像源
- 升级 pip: `pip install --upgrade pip`
- 检查网络连接

#### 3. go-cqhttp 连接失败
**错误**: 机器人无法连接到 go-cqhttp
**解决**:
- 检查 go-cqhttp 是否正常运行
- 确认端口配置是否一致
- 检查防火墙设置

#### 4. CRCON API 连接失败
**错误**: API 请求失败
**解决**:
- 验证 API 地址是否正确
- 检查 API 令牌是否有效
- 确认网络连接和防火墙设置

#### 5. 权限不足
**错误**: 执行管理命令时提示权限不足
**解决**:
- 确认 QQ 号在 `SUPERUSERS` 列表中
- 检查 API 令牌权限设置

### 日志分析

#### 查看日志
```bash
# 实时查看日志
tail -f logs/bot.log

# 查看错误日志
grep "ERROR" logs/bot.log

# 查看最近的日志
tail -n 100 logs/bot.log
```

#### 常见日志信息
- `INFO` - 正常运行信息
- `WARNING` - 警告信息，通常不影响运行
- `ERROR` - 错误信息，需要处理
- `DEBUG` - 调试信息（需要设置 LOG_LEVEL=DEBUG）

### 性能优化

#### 1. 内存优化
- 定期重启机器人（每天一次）
- 监控内存使用情况
- 适当调整缓存设置

#### 2. 网络优化
- 使用稳定的网络连接
- 配置合适的超时时间
- 启用连接池

#### 3. 日志优化
- 定期清理旧日志文件
- 调整日志级别
- 使用日志轮转

## 安全建议

### 1. 配置文件安全
- 不要将 `.env` 文件提交到版本控制
- 定期更换 API 令牌
- 使用强密码保护服务器

### 2. 网络安全
- 使用防火墙限制访问
- 启用 HTTPS（如果可能）
- 定期更新依赖包

### 3. 权限管理
- 最小权限原则
- 定期审查超级用户列表
- 监控管理操作日志

## 更新升级

### 1. 备份数据
```bash
# 备份配置文件
cp .env .env.backup

# 备份日志（可选）
cp -r logs logs.backup
```

### 2. 更新代码
```bash
git pull origin main
```

### 3. 更新依赖
```bash
pip install -r requirements.txt --upgrade
```

### 4. 重启服务
```bash
# systemd
sudo systemctl restart crcon-qqbot

# PM2
pm2 restart crcon-qqbot

# 手动
# 停止当前进程，然后重新启动
```

---

如果在安装过程中遇到问题，请查看项目的 Issue 页面或联系维护者获取帮助。