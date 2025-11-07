# Prophet Web 应用启动指南

本文档说明如何启动 Prophet Web 应用的前端和后端服务。

## 前置要求

- Python 3.8+
- Node.js 16+
- Redis (用于 Celery 任务队列)
- nmap (系统命令，用于网络扫描)

## 后端启动

### 1. 安装 Python 依赖

```bash
# 进入项目根目录
cd /path/to/prophet

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
# 如果使用requirements_web.txt（仅Web应用依赖）
pip install -r requirements_web.txt

# 或者使用requirements.txt（包含所有依赖，包括核心prophet依赖）
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

创建 `.env` 文件或设置环境变量：

```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here
export ENCRYPTION_KEY=your-encryption-key-here  # 生产环境必须设置
export DATABASE_URL=sqlite:///prophet_web.db
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. 初始化数据库

```bash
# 运行Flask应用会自动创建数据库表
python app.py
```

或者使用 Flask shell：

```bash
flask shell
>>> from app import create_app
>>> from db import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### 4. 启动 Redis

```bash
# Linux/Mac
redis-server

# 或使用Docker
docker run -d -p 6379:6379 redis:latest
```

### 5. 启动 Flask 应用

```bash
python app.py
```

或者使用 Flask 开发服务器：

```bash
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

后端服务将在 `http://localhost:5000` 启动。

### 6. 启动 Celery Worker（用于异步任务）

在新的终端窗口中：

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac

# 启动Celery worker (使用 celery_worker.py 确保 Flask app 上下文)
celery -A celery_worker.celery worker --loglevel=info
```

或者使用 Flower 监控 Celery 任务（可选）：

```bash
pip install flower
celery -A celery_worker.celery flower
```

## 前端启动

### 1. 安装 Node.js 依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

前端服务将在 `http://localhost:3000` 启动。

### 3. 构建生产版本

```bash
npm run build
```

构建产物在 `frontend/dist` 目录。

## 完整启动流程

### 终端 1: Redis

```bash
redis-server
```

### 终端 2: Flask 后端

```bash
cd /path/to/prophet
source venv/bin/activate
python app.py
```

### 终端 3: Celery Worker

```bash
cd /path/to/prophet
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

### 终端 4: 前端

```bash
cd /path/to/prophet/frontend
npm run dev
```

## 访问应用

- 前端: http://localhost:3000
- 后端 API: http://localhost:5000/api/v1
- 健康检查: http://localhost:5000/api/v1/health

## 首次使用

1. 访问 http://localhost:3000
2. 点击"注册"创建账户
3. 登录后即可使用各项功能

## 常见问题

### 1. 数据库文件不存在

运行 `python app.py` 会自动创建数据库文件 `prophet_web.db`。

### 2. Redis 连接失败

确保 Redis 服务正在运行：

```bash
redis-cli ping
# 应该返回 PONG
```

### 3. Celery 任务不执行

确保：

- Redis 服务正在运行
- Celery worker 已启动
- 后端应用已启动

### 4. 前端无法连接后端

检查 `frontend/vite.config.ts` 中的代理配置，确保后端运行在 `http://localhost:5000`。

### 5. 端口被占用

修改端口：

- 后端: 在 `app.py` 中修改 `app.run(port=5000)`
- 前端: 在 `frontend/vite.config.ts` 中修改 `server.port`

## 生产环境部署

### 后端

使用 Gunicorn：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

### 前端

```bash
cd frontend
npm run build
# 将 dist 目录部署到Nginx或其他Web服务器
```

### 使用 Supervisor 管理进程

创建 `/etc/supervisor/conf.d/prophet.conf`:

```ini
[program:prophet-web]
command=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
directory=/path/to/prophet
user=www-data
autostart=true
autorestart=true

[program:prophet-celery]
command=/path/to/venv/bin/celery -A celery_worker.celery worker --loglevel=info
directory=/path/to/prophet
user=www-data
autostart=true
autorestart=true
```

## 开发模式

### 后端热重载

使用 Flask 开发模式（已启用）：

```bash
export FLASK_ENV=development
python app.py
```

### 前端热重载

Vite 默认支持热重载，修改代码后自动刷新。

## 日志

- 后端日志: `prophet_web.log`
- Celery 日志: 在终端输出或配置日志文件

## 下一步

- 查看 API 文档: 访问 `/api/v1/health` 测试连接
- 创建第一个扫描任务
- 添加虚拟化平台
- 导入设备列表
