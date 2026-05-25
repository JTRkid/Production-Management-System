# 生产管理系统

中小型制造企业生产管理系统，覆盖从客户订单、采购供应、生产计划、工单派发、过程跟踪、质量检验、库存管理到报表分析的全业务流程。

## 目录

| 章节 | 内容 |
|------|------|
| [技术栈](#技术栈) | 后端/前端/数据库技术选型 |
| [项目结构](#项目结构) | 目录结构说明 |
| [功能模块](#功能模块) | 9 大业务模块概览 |
| [角色体系](#角色体系) | 9 种用户角色与权限 |
| [快速启动](#快速启动) | 开发环境搭建与生产部署 |
| ↳ [环境要求](#1-环境要求) | Python / Node / MySQL 版本要求 |
| ↳ [一键启动](#2-一键启动推荐) | start.cmd 双击启动 |
| ↳ [手动启动](#3-手动启动) | 前后端分别启动 |
| ↳ [访问系统](#4-访问系统) | 地址与默认账号 |
| ↳ [Docker 部署](#5-docker-部署生产环境) | docker-compose 生产环境容器化部署 |
| ↳ [Ubuntu 24 生产部署](#6-ubuntu-24-生产环境部署) | 完整生产环境搭建 |
| [API 接口文档](#api-接口文档) | 全部 REST API 接口说明 |
| [操作手册](#操作手册) | 典型业务流程与常用操作 |
| [数据库表说明](#数据库表说明) | 21 张数据表结构 |
| [开发规范](#开发规范) | 代码规范与提交约定 |

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Django + DRF | 5.0 |
| 数据库 | SQLite（开发）/ MySQL 8.0（生产） | — |
| 认证 | JWT（djangorestframework-simplejwt） | — |
| 过滤 | django-filters | 24.2 |
| 前端框架 | Vue 3 + Vite | 3.5 |
| UI 组件库 | Element Plus | 2.14 |
| 状态管理 | Pinia | 3.0 |
| 路由 | Vue Router | 4.6 |
| 图表 | ECharts | 5.x |

## 项目结构

```
生产管理系统/
├── backend/                        # Django 后端
│   ├── teach_platform/             # 项目配置
│   │   ├── settings.py             # Django 配置（支持环境变量）
│   │   └── urls.py                 # 根路由
│   ├── apps/                       # 业务应用
│   │   ├── accounts/               # 用户认证与系统管理
│   │   ├── sys_admin/              # 系统管理（路由占位）
│   │   ├── business/               # 业务管理（客户/销售/供应商/采购）
│   │   ├── base_data/              # 基础数据（物料/BOM/工艺/设备）
│   │   ├── prod_plan/              # 生产计划
│   │   ├── work_order/             # 工单管理
│   │   ├── prod_track/             # 生产过程跟踪（报工）
│   │   ├── quality/                # 质量管理（检验标准/记录）
│   │   ├── inventory/              # 库存管理（仓库/库存/出入库）
│   │   └── dashboard/              # 报表看板（聚合查询）
│   ├── Dockerfile                  # 后端容器镜像
│   ├── entrypoint.sh               # 容器启动脚本
│   ├── media/                      # 媒体文件
│   ├── manage.py                   # Django 管理入口
│   ├── requirements.txt            # Python 依赖
│   └── seed_data.py                # 种子数据脚本
├── frontend/                       # Vue 3 前端
│   ├── src/
│   │   ├── api/index.js            # API 层（Axios 封装 + 全部接口）
│   │   ├── router/index.js         # 路由配置（26 条路由）
│   │   ├── stores/auth.js          # Pinia 认证状态管理
│   │   ├── layouts/MainLayout.vue  # 主布局（侧边栏 + 顶栏）
│   │   ├── views/                  # 页面组件（24 个）
│   │   │   ├── Login.vue           # 登录页
│   │   │   ├── dashboard/          # 生产看板 + 生产报表
│   │   │   ├── sys-admin/          # 系统管理（用户/车间/日志）
│   │   │   ├── business/           # 业务管理（客户/销售/供应商/采购）
│   │   │   ├── base-data/          # 基础数据（物料/BOM/工艺/设备）
│   │   │   ├── prod-plan/          # 生产计划
│   │   │   ├── work-order/         # 工单管理
│   │   │   ├── prod-track/         # 过程跟踪（报工/看板）
│   │   │   ├── quality/            # 质量管理（标准/检验）
│   │   │   └── inventory/          # 库存管理（仓库/库存/出入库）
│   │   └── utils/constants.js      # 常量映射
│   ├── Dockerfile                  # 前端容器镜像
│   ├── nginx.conf                  # Nginx 配置（反向代理 + WebSocket）
│   ├── public/favicon.svg          # 网站图标
│   ├── index.html                  # HTML 入口
│   ├── vite.config.js              # Vite 构建配置
│   └── package.json                # Node 依赖
├── venv/                           # Python 虚拟环境（项目根目录）
├── docs/                           # 项目文档
│   ├── README.md                   # 本文件
│   ├── SRS-生产管理系统需求规格说明书.md
│   └── 需求文档.md
├── docker-compose.yml              # Docker 生产编排
├── .env.example                    # 生产环境变量模板
├── start.cmd                       # Windows 一键启动脚本
└── stop.cmd                        # Windows 一键停止脚本
```

## 功能模块

| 编号 | 模块 | Django App | 功能数 | 数据表 |
|------|------|------------|--------|--------|
| 1 | 系统管理 | accounts + sys_admin | 用户/车间/操作日志 | 3 |
| 2 | 业务管理 | business | 客户/销售订单/供应商/采购订单 | 4 |
| 3 | 基础数据 | base_data | 物料/BOM/工艺路线/工作中心/设备 | 6 |
| 4 | 生产计划 | prod_plan | 主生产计划/审批/下发 | 1 |
| 5 | 工单管理 | work_order | 工单生成/派发/状态流转/报工 | 1 |
| 6 | 过程跟踪 | prod_track | 工序报工/生产看板 | 1 |
| 7 | 质量管理 | quality | 检验标准/过程检验/完工检验 | 2 |
| 8 | 库存管理 | inventory | 仓库/库存/出入库 | 3 |
| 9 | 报表分析 | dashboard | 生产日报/完成率/质量趋势 | 0（聚合查询） |

## 角色体系

| 角色 | 编码 | 权限范围 |
|------|------|----------|
| 系统管理员 | admin | 全部权限 |
| 生产计划员 | planner | 计划制定、工单下发 |
| 车间主任 | workshop_director | 工单审核、人员调度 |
| 班组长 | foreman | 任务分配、报工审核 |
| 工人 | worker | 工序报工 |
| 质检员 | inspector | 检验执行、报告出具 |
| 库管员 | storekeeper | 出入库操作 |
| 业务员 | salesman | 客户管理、销售订单 |
| 采购员 | purchaser | 供应商管理、采购订单 |

## 快速启动

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0（可选，默认使用 SQLite）

### 2. 一键启动（推荐）

```bash
# Windows 双击 start.cmd 即可同时启动前后端
# 或在命令行执行：
start.cmd
```

启动后自动打开 http://localhost:3000，默认账号 `admin` / `123456`。

### 3. 手动启动

#### 后端

```bash
# 在项目根目录创建虚拟环境
python -m venv venv

# 安装依赖
venv\Scripts\pip install -r backend\requirements.txt   # Windows
# source venv/bin/activate && pip install -r backend/requirements.txt  # Linux/macOS

# 进入后端目录
cd backend

# 数据库迁移（使用根目录的虚拟环境）
../venv/Scripts/python manage.py makemigrations
../venv/Scripts/python manage.py migrate

# 填充种子数据
../venv/Scripts/python seed_data.py

# 启动开发服务器（默认 8000 端口）
../venv/Scripts/python manage.py runserver
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认 3000 端口）
npm run dev
```

### 4. 访问系统

- 前端地址：http://localhost:3000
- 后端 API：http://localhost:8000/api/v1/
- 默认账号：`admin` / `123456`

### 5. Docker 部署（生产环境）

项目支持 Docker Compose 一键部署，包含 4 个服务：MySQL、Redis、后端（Gunicorn）、前端（Nginx）。

#### 5.1 部署架构

```
浏览器(HTTPS)
    │
    ▼
┌───────────────────────────────────────────┐
│  Nginx (prod-frontend :80)                │
│  ├── /          → Vue SPA 静态文件        │
│  ├── /static/   → Django collectstatic    │
│  ├── /api/      → proxy → backend:8000    │
│  └── /ws/       → proxy → backend:8000    │
└──────────────┬────────────────────────────┘
               │
               ▼
┌───────────────────────────────────────────┐
│  Gunicorn + Uvicorn (prod-backend :8000)  │
│  Django REST Framework + Channels         │
└───────┬──────────────────────┬────────────┘
        │                      │
        ▼                      ▼
┌───────────────┐   ┌───────────────┐
│  MySQL 8.0    │   │  Redis 7      │
│  (业务数据)    │   │  (Channel 层) │
└───────────────┘   └───────────────┘
```

#### 5.2 环境要求

- Docker 20.10+
- Docker Compose v2+
- 服务器内存建议 2GB+

#### 5.3 创建环境变量文件

项目根目录提供了 `.env.example` 模板，复制后填入真实值：

```bash
cp .env.example .env
```

编辑 `.env`，配置以下变量：

```env
# ── Django ──
DJANGO_SECRET_KEY=替换为一串很长的随机字符串（可用 python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 生成）
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# ── CORS（逗号分隔的前端域名）──
CORS_ALLOWED_ORIGINS=https://your-domain.com

# ── MySQL ──
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=prod_mgmt
MYSQL_USER=prod_user
MYSQL_PASSWORD=替换为强密码
MYSQL_ROOT_PASSWORD=替换为强密码

# ── Redis ──
REDIS_URL=redis://redis:6379/0
```

> **注意**：`.env` 包含敏感密码，已加入 `.gitignore`，不会提交到代码仓库。

#### 5.4 构建并启动

```bash
# 在项目根目录执行（包含 docker-compose.yml 的目录）
docker-compose up -d --build
```

首次启动会自动执行以下操作：
1. 拉取 MySQL 8.0、Redis 7、Python 3.12、Node 20、Nginx 镜像
2. 构建后端镜像：安装 Python 依赖 → 收集静态文件 → 数据库迁移 → 填充种子数据
3. 构建前端镜像：npm ci → npm run build → 复制 dist 到 Nginx
4. 启动全部 4 个服务，MySQL 和 Redis 就绪后后端才启动（healthcheck）

#### 5.5 创建管理员账号

种子数据已包含默认管理员 `admin / 123456`。如需创建额外管理员：

```bash
docker exec -it prod-backend python manage.py createsuperuser
```

#### 5.6 访问系统

- 前端地址：`http://your-server-ip`（80 端口）
- 后端 API：`http://your-server-ip/api/v1/`
- 默认账号：`admin` / `123456`

#### 5.7 数据持久化

| 数据 | 存储方式 | 说明 |
|------|----------|------|
| MySQL 数据 | Docker named volume `mysql_data` | `docker-compose down` 不丢失，`down -v` 会删除 |
| Redis 数据 | Docker named volume `redis_data` | 缓存数据，丢失不影响业务 |
| 上传文件 | 宿主机挂载 `./backend/media/` | 直接映射到宿主机目录 |
| 静态文件 | Docker named volume `static_files` | 后端 collectstatic 产物，前端 Nginx 共享读取 |

#### 5.8 常用运维命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看实时日志（所有服务）
docker-compose logs -f

# 查看单个服务日志
docker-compose logs -f backend
docker-compose logs -f mysql

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart backend

# 停止所有服务（数据不丢失）
docker-compose down

# 停止并删除所有数据（慎用！会清除数据库）
docker-compose down -v

# 重新构建并启动（代码更新后）
docker-compose up -d --build

# 进入后端容器调试
docker exec -it prod-backend bash

# 在容器内执行 Django 管理命令
docker exec -it prod-backend python manage.py shell
docker exec -it prod-backend python manage.py dbshell
```

#### 5.9 更新部署

代码更新后，执行以下命令重新部署：

```bash
cd /path/to/生产管理系统

# 拉取最新代码
git pull

# 重新构建并启动（仅重建有变更的服务）
docker-compose up -d --build

# 查看迁移是否成功
docker-compose logs backend | grep "迁移"
```

#### 5.10 数据库备份、恢复与自动清理

**手动备份：**

```bash
# 导出数据库（文件名含日期）
docker exec prod-mysql mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" prod_mgmt > backup_$(date +%Y%m%d).sql
```

**手动恢复：**

```bash
# 从备份文件恢复（会覆盖当前数据）
docker exec -i prod-mysql mysql -u root -p"$MYSQL_ROOT_PASSWORD" prod_mgmt < backup_20260526.sql
```

**配置每日自动备份 + 循环清理：**

```bash
# 1. 创建备份目录
sudo mkdir -p /data/backup/mysql

# 2. 用 vim 创建备份脚本
sudo vim /data/backup/mysql/backup.sh
```

写入以下内容：

```bash
#!/bin/bash
set -e

BACKUP_DIR="/data/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7   # 保留最近 7 天，超过自动删除

# 读取 .env 中的密码
MYSQL_ROOT_PASSWORD=$(grep MYSQL_ROOT_PASSWORD /path/to/生产管理系统/.env | cut -d= -f2)

# 执行备份（gzip 压缩）
docker exec prod-mysql mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" prod_mgmt \
  | gzip > "$BACKUP_DIR/prod_mgmt_${DATE}.sql.gz"

# 清理超过 KEEP_DAYS 天的旧备份
find "$BACKUP_DIR" -name "prod_mgmt_*.sql.gz" -mtime +$KEEP_DAYS -delete

echo "[$(date)] 备份完成: prod_mgmt_${DATE}.sql.gz，已清理 ${KEEP_DAYS} 天前的旧备份"
```

```bash
# 3. 设置脚本权限
sudo chmod +x /data/backup/mysql/backup.sh

# 4. 加入 crontab：每天凌晨 3 点执行
sudo crontab -e
```

在 crontab 末尾添加一行：

```
0 3 * * * /data/backup/mysql/backup.sh >> /data/backup/mysql/backup.log 2>&1
```

```bash
# 5. 验证 crontab 是否写入
sudo crontab -l
```

> **注意**：将脚本中 `/path/to/生产管理系统/` 替换为项目实际路径。`KEEP_DAYS=7` 表示只保留最近 7 天的备份，可按需修改。

**验证备份脚本：**

```bash
# 手动执行一次，确认正常
sudo /data/backup/mysql/backup.sh

# 检查备份文件
ls -lh /data/backup/mysql/

# 检查日志
cat /data/backup/mysql/backup.log
```

**备份文件说明：**

```
/data/backup/mysql/
├── backup.sh                          # 备份脚本
├── backup.log                         # 执行日志
├── prod_mgmt_20260526_030000.sql.gz   # 自动备份（gzip 压缩）
├── prod_mgmt_20260525_030000.sql.gz
├── prod_mgmt_20260524_030000.sql.gz
└── ...                                # 超过 7 天的会被自动删除
```

#### 5.11 配置 HTTPS（可选）

如需 HTTPS，在 `docker-compose.yml` 的 frontend 服务中挂载 SSL 证书，并修改 `nginx.conf`：

1. 将证书文件放到项目目录（如 `nginx/ssl/`）

2. `docker-compose.yml` 的 frontend volumes 加一行：
   ```yaml
   - ./nginx/ssl:/etc/nginx/ssl:ro
   ```

3. `nginx.conf` 修改为监听 443：
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       ssl_certificate     /etc/nginx/ssl/fullchain.pem;
       ssl_certificate_key /etc/nginx/ssl/privkey.pem;
       # ... 其余配置不变
   }

   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$host$request_uri;
   }
   ```

4. 重建前端镜像：
   ```bash
   docker-compose up -d --build frontend
   ```

或使用免费的 Let's Encrypt 证书 + certbot 自动续期。

### 6. Ubuntu 24 生产环境部署

以下是在全新 Ubuntu 24.04 Server 上部署生产环境的完整步骤。

#### 6.1 系统更新

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential
```

#### 6.2 安装 Python 3.12

Ubuntu 24.04 自带 Python 3.12，只需安装 pip 和 venv：

```bash
# 验证 Python 版本
python3 --version

# 安装 pip 和 venv
sudo apt install -y python3-pip python3-venv python3-dev

# 安装 MySQL 编译依赖（mysqlclient 需要）
sudo apt install -y pkg-config libmysqlclient-dev
```

#### 6.3 安装 MySQL 8.0

```bash
# 安装 MySQL Server
sudo apt install -y mysql-server

# 启动并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全初始化（设置 root 密码、移除测试库等）
sudo mysql_secure_installation
```

**创建数据库和用户：**

```bash
sudo mysql -u root <<'SQL'
-- 创建生产数据库
CREATE DATABASE production_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 创建应用用户（替换 your_password 为实际密码）
CREATE USER 'prod_user'@'localhost' IDENTIFIED BY 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON production_db.* TO 'prod_user'@'localhost';
FLUSH PRIVILEGES;
SQL
```

**验证连接：**

```bash
mysql -u prod_user -p'your_password' -e "SELECT 1;"
```

#### 6.4 安装 Node.js 20

```bash
# 安装 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# 安装 Node.js
sudo apt install -y nodejs

# 验证版本
node --version
npm --version
```

#### 6.5 安装 Nginx

```bash
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 6.6 部署项目代码

```bash
# 创建部署目录
sudo mkdir -p /var/www/production-system
sudo chown $USER:$USER /var/www/production-system

# 克隆项目（替换为实际仓库地址）
git clone <your-repo-url> /var/www/production-system
cd /var/www/production-system
```

#### 6.7 后端部署

```bash
# ── 1. 创建虚拟环境 ──
python3 -m venv venv
source venv/bin/activate

# ── 2. 安装依赖 ──
pip install -r backend/requirements.txt
pip install gunicorn mysqlclient

# ── 3. 修改 Django 配置 ──
# 编辑 backend/teach_platform/settings.py，修改以下配置：

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'production_db',
#         'USER': 'prod_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }
#
# DEBUG = False
# ALLOWED_HOSTS = ['your-server-ip', 'your-domain.com']

# ── 4. 数据库迁移 ──
cd backend
../venv/bin/python manage.py makemigrations
../venv/bin/python manage.py migrate

# ── 5. 填充种子数据 ──
../venv/bin/python seed_data.py

# ── 6. 收集静态文件 ──
../venv/bin/python manage.py collectstatic --noinput

# ── 7. 创建超级用户（可选，种子数据已包含 admin） ──
# ../venv/bin/python manage.py createsuperuser
```

**测试 Gunicorn 是否正常启动：**

```bash
cd /var/www/production-system
venv/bin/gunicorn --bind 127.0.0.1:8000 teach_platform.wsgi:application --chdir backend
# 按 Ctrl+C 停止测试
```

#### 6.8 配置 Gunicorn Systemd 服务

```bash
sudo tee /etc/systemd/system/production-backend.service <<'EOF'
[Unit]
Description=Production System Backend (Gunicorn)
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/production-system/backend
ExecStart=/var/www/production-system/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /var/log/gunicorn-access.log \
    --error-logfile /var/log/gunicorn-error.log \
    teach_platform.wsgi:application
Restart=always
RestartSec=5
Environment="DJANGO_SETTINGS_MODULE=teach_platform.settings"

[Install]
WantedBy=multi-user.target
EOF

# 设置日志文件权限
sudo touch /var/log/gunicorn-access.log /var/log/gunicorn-error.log
sudo chown www-data:www-data /var/log/gunicorn-*.log

# 设置媒体目录权限
sudo chown -R www-data:www-data /var/www/production-system/backend/media

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start production-backend
sudo systemctl enable production-backend

# 验证状态
sudo systemctl status production-backend
```

#### 6.9 前端构建

```bash
cd /var/www/production-system/frontend

# 安装依赖
npm install

# 修改 API 地址（如果后端不在同一域名）
# 编辑 src/api/index.js，将 baseURL 改为实际地址，例如：
#   baseURL: 'http://your-server-ip/api/v1'
# 或使用相对路径（推荐，由 Nginx 代理）：
#   baseURL: '/api/v1'

# 生产构建
npm run build
```

构建产物在 `frontend/dist/` 目录。

#### 6.10 配置 Nginx

```bash
sudo tee /etc/nginx/sites-available/production-system <<'EOF'
server {
    listen 80;
    server_name your-server-ip your-domain.com;

    # 前端静态文件
    root /var/www/production-system/frontend/dist;
    index index.html;

    # 前端路由 — SPA 所有路径回退到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Django 静态文件
    location /static/ {
        alias /var/www/production-system/backend/staticfiles/;
        expires 30d;
    }

    # 上传的媒体文件
    location /media/ {
        alias /var/www/production-system/backend/media/;
        expires 30d;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 日志
    access_log /var/log/nginx/production-system-access.log;
    error_log /var/log/nginx/production-system-error.log;
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/production-system /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

#### 6.11 配置防火墙

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
sudo ufw status
```

#### 6.12 验证部署

```bash
# 检查后端服务
curl http://localhost:8000/api/v1/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 检查 Nginx 代理
curl http://localhost/api/v1/auth/login/ -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 检查前端页面
curl -I http://localhost/
```

浏览器访问 `http://your-server-ip`，使用 `admin` / `123456` 登录。

#### 6.13 常用运维命令

```bash
# 查看后端服务状态
sudo systemctl status production-backend

# 重启后端
sudo systemctl restart production-backend

# 查看后端日志
sudo journalctl -u production-backend -f
tail -f /var/log/gunicorn-error.log

# 查看 Nginx 日志
tail -f /var/log/nginx/production-system-error.log

# 重启 Nginx
sudo systemctl restart nginx

# 更新代码后重新部署
cd /var/www/production-system
git pull
source venv/bin/activate
cd backend && ../venv/bin/python manage.py migrate && cd ..
cd frontend && npm install && npm run build && cd ..
sudo systemctl restart production-backend
sudo systemctl reload nginx
```

#### 6.14 可选：配置 HTTPS（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书（替换为实际域名）
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## API 接口文档

### 认证接口 `/api/v1/auth/`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/auth/login/` | 用户登录，返回 JWT token | 否 |
| POST | `/auth/change-password/` | 修改密码 | 是 |
| POST | `/auth/token/refresh/` | 刷新 access_token | 否 |

**登录请求示例：**
```json
POST /api/v1/auth/login/
{
  "username": "admin",
  "password": "123456"
}
```
**响应：**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": { "id": 1, "username": "admin", "name": "系统管理员", "role": "admin" }
  }
}
```

### 系统管理 `/api/v1/auth/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/auth/users/` | 用户列表（支持 ?role=&search=&page=） |
| POST | `/auth/users/` | 创建用户 |
| PUT | `/auth/users/{id}/` | 编辑用户 |
| DELETE | `/auth/users/{id}/` | 删除用户 |
| POST | `/auth/users/{id}/reset_password/` | 重置密码为 123456 |
| POST | `/auth/users/{id}/toggle_active/` | 启用/禁用用户 |
| GET | `/auth/workshops/` | 车间列表 |
| POST | `/auth/workshops/` | 创建车间 |
| PUT | `/auth/workshops/{id}/` | 编辑车间 |
| DELETE | `/auth/workshops/{id}/` | 删除车间 |
| GET | `/auth/logs/` | 操作日志（支持 ?action=） |

### 业务管理 `/api/v1/business/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/business/customers/` | 客户列表（支持 ?search=&customer_level=） |
| POST | `/business/customers/` | 创建客户 |
| PUT | `/business/customers/{id}/` | 编辑客户 |
| DELETE | `/business/customers/{id}/` | 删除客户 |
| GET | `/business/sales-orders/` | 销售订单列表（支持 ?status=&customer=） |
| POST | `/business/sales-orders/` | 创建销售订单 |
| PUT | `/business/sales-orders/{id}/` | 编辑销售订单 |
| POST | `/business/sales-orders/{id}/approve/` | 审批订单 |
| POST | `/business/sales-orders/{id}/cancel/` | 取消订单 |
| GET | `/business/suppliers/` | 供应商列表 |
| POST | `/business/suppliers/` | 创建供应商 |
| PUT | `/business/suppliers/{id}/` | 编辑供应商 |
| DELETE | `/business/suppliers/{id}/` | 删除供应商 |
| GET | `/business/purchase-orders/` | 采购订单列表 |
| POST | `/business/purchase-orders/` | 创建采购订单 |
| POST | `/business/purchase-orders/{id}/approve/` | 审批采购订单 |
| POST | `/business/purchase-orders/{id}/receive/` | 收货确认 `{"quantity": 100}` |

### 基础数据 `/api/v1/base-data/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/base-data/materials/` | 物料列表（支持 ?material_type=&search=） |
| GET | `/base-data/materials/active/` | 启用物料（下拉用） |
| POST | `/base-data/materials/` | 创建物料 |
| PUT | `/base-data/materials/{id}/` | 编辑物料 |
| DELETE | `/base-data/materials/{id}/` | 删除物料 |
| GET | `/base-data/bom-items/` | BOM 列表 |
| POST | `/base-data/bom-items/` | 创建 BOM 明细 |
| GET | `/base-data/bom-items/{id}/tree/` | 展开 BOM 树 |
| GET | `/base-data/routes/` | 工艺路线列表 |
| POST | `/base-data/routes/` | 创建工艺路线 |
| GET | `/base-data/routes/{id}/steps/` | 查看路线工序 |
| GET | `/base-data/route-steps/` | 工序列表 |
| POST | `/base-data/route-steps/` | 添加工序 |
| GET | `/base-data/work-centers/` | 工作中心列表 |
| POST | `/base-data/work-centers/` | 创建工作中心 |
| GET | `/base-data/equipment/` | 设备列表（支持 ?status=） |
| POST | `/base-data/equipment/` | 创建设备 |

### 生产计划 `/api/v1/prod-plan/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/prod-plan/production-plans/` | 计划列表（支持 ?status=&plan_type=） |
| POST | `/prod-plan/production-plans/` | 创建计划 |
| PUT | `/prod-plan/production-plans/{id}/` | 编辑计划 |
| POST | `/prod-plan/production-plans/{id}/approve/` | 审批计划 |
| POST | `/prod-plan/production-plans/{id}/release/` | 下发计划 |
| POST | `/prod-plan/production-plans/{id}/cancel/` | 取消计划 |

### 工单管理 `/api/v1/work-order/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/work-order/work-orders/` | 工单列表（支持 ?status=&priority=&workshop=） |
| POST | `/work-order/work-orders/` | 创建工单 |
| PUT | `/work-order/work-orders/{id}/` | 编辑工单 |
| POST | `/work-order/work-orders/{id}/dispatch/` | 派发工单 |
| POST | `/work-order/work-orders/{id}/start/` | 开始生产 |
| POST | `/work-order/work-orders/{id}/complete/` | 完工 |
| POST | `/work-order/work-orders/{id}/close/` | 关闭工单 |
| POST | `/work-order/work-orders/{id}/report/` | 工序报工 `{"route_step":1,"report_quantity":10,"defect_quantity":1}` |

### 过程跟踪 `/api/v1/prod-track/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/prod-track/work-reports/` | 报工列表（支持 ?work_order=） |
| POST | `/prod-track/work-reports/` | 创建报工 |
| GET | `/prod-track/work-reports/my_reports/` | 我的报工 |

### 质量管理 `/api/v1/quality/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/quality/standards/` | 检验标准列表（支持 ?product=&is_active=） |
| POST | `/quality/standards/` | 创建检验标准 |
| PUT | `/quality/standards/{id}/` | 编辑检验标准 |
| DELETE | `/quality/standards/{id}/` | 删除检验标准 |
| GET | `/quality/records/` | 检验记录列表（支持 ?work_order=&inspection_type=&result=） |
| POST | `/quality/records/` | 创建检验记录 |

### 库存管理 `/api/v1/inventory/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/inventory/warehouses/` | 仓库列表（支持 ?warehouse_type=） |
| POST | `/inventory/warehouses/` | 创建仓库 |
| GET | `/inventory/inventories/` | 库存查询（支持 ?warehouse=&material=&search=） |
| GET | `/inventory/transactions/` | 出入库记录（支持 ?warehouse=&transaction_type=） |
| POST | `/inventory/transactions/inbound/` | 入库 `{"transaction_type":"purchase_in","material":1,"quantity":100,"warehouse":1}` |
| POST | `/inventory/transactions/outbound/` | 出库 `{"transaction_type":"material_out","material":1,"quantity":20,"warehouse":1}` |

### 报表看板 `/api/v1/dashboard/`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dashboard/overview/` | 首页看板概览 |
| GET | `/dashboard/prod_daily/` | 生产日报（当日产量/合格/不良/稼动率） |
| GET | `/dashboard/completion_rate/` | 近 30 天工单完成率趋势 |
| GET | `/dashboard/quality_trend/` | 近 30 天不良率趋势 |

### 通用说明

- 认证方式：请求头携带 `Authorization: Bearer {access_token}`
- 分页参数：`?page=1&page_size=20`（默认 page_size=20）
- 响应格式：`{ "code": 200, "data": ... }` 或分页格式 `{ "count": 100, "results": [...] }`
- 错误格式：`{ "code": 400, "message": "错误描述" }`
- 搜索/筛选/排序参数均为可选，接口支持 `?search=关键词&ordering=-created_at`

---

## 操作手册

### 典型业务流程

**1. 客户下单 → 生产交付**

```
业务员创建客户 → 创建销售订单 → 计划员审批订单
→ 计划员创建生产计划 → 审批 → 下发 → 生成工单
→ 车间主任派发工单 → 班组长开始生产 → 工人逐工序报工
→ 质检员过程/完工检验 → 完工入库 → 销售发货
```

**2. 物料采购流程**

```
计划员审批计划 → 系统计算物料需求 → 采购员创建采购订单
→ 审批 → 下单 → 供应商交货 → 库管员收货入库 → 库存更新
```

### 常用操作

#### 用户管理
1. 登录后，侧边栏 → 系统管理 → 用户管理
2. 点击"添加用户"，填写用户名、姓名、密码、角色、手机号
3. 表格中可编辑、重置密码（恢复为 123456）、切换启用状态

#### 创建销售订单
1. 侧边栏 → 业务管理 → 销售订单
2. 点击"添加"，选择客户、产品（仅显示成品）、填写数量和交期
3. 订单状态为"草稿"时，可点击"审批"提交

#### 创建工单并报工
1. 侧边栏 → 工单管理
2. 点击"添加"，选择产品、车间、工艺路线、优先级
3. 审批后点击"派发" → "开始生产"
4. 生产过程中点击"报工"，填写工序、合格数、不良数、工时

#### 查看报表
1. 首页看板：登录后默认显示，包含工单概况、月度产量、不良率
2. 生产报表：侧边栏 → 生产报表，切换"生产日报/工单完成率/质量趋势"

#### 库存操作
1. 侧边栏 → 库存管理 → 库存查询（只读）
2. 出入库记录 → 点击"入库"或"出库"，选择类型/物料/数量

---

## 数据库表说明

| 表名 | 所属 App | 说明 |
|------|----------|------|
| sys_user | accounts | 用户表 |
| sys_workshop | accounts | 车间表 |
| sys_operation_log | accounts | 操作日志表 |
| biz_customer | business | 客户表 |
| biz_sales_order | business | 销售订单表 |
| biz_supplier | business | 供应商表 |
| biz_purchase_order | business | 采购订单表 |
| base_material | base_data | 物料主数据表 |
| base_bom_item | base_data | BOM 明细表 |
| base_route | base_data | 工艺路线表 |
| base_route_step | base_data | 工艺路线工序表 |
| base_work_center | base_data | 工作中心表 |
| base_equipment | base_data | 设备台账表 |
| prod_plan | prod_plan | 生产计划表 |
| work_order | work_order | 生产工单表 |
| prod_work_report | prod_track | 报工记录表 |
| qc_standard | quality | 检验标准表 |
| qc_record | quality | 检验记录表 |
| inv_warehouse | inventory | 仓库表 |
| inv_inventory | inventory | 库存表 |
| inv_transaction | inventory | 出入库记录表 |

---

## 开发规范

- 后端遵循 Django app 模块化拆分，每 app 含 models / serializers / views / urls
- 前端遵循 Vue 3 Composition API（`<script setup>`），页面按模块分目录
- API 响应统一格式 `{ code: 200, data: ... }`
- 关键操作记录操作日志（创建、修改、删除、审批）
- 业务操作使用数据库事务保证一致性（如出入库扣减库存）
- 前端搜索与分页参数统一：`{ page, page_size, search }`
- Git 提交信息简洁描述变更原因而非变更内容
