# PixelSentry 开发指南

## 本地开发环境设置

### 方式一：使用 Docker Compose（推荐）

这是最简单的方式，所有服务都在容器中运行。

```bash
cd /home/xyber-nova/Github/PixelSentry

# 配置环境变量
cp .env.example .env

# 启动所有服务（后台运行）
sudo docker-compose up -d

# 查看日志
sudo docker-compose logs -f

# 停止所有服务
sudo docker-compose down
```

访问：
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

### 方式二：混合开发（数据库在 Docker，代码在本地）

这种方式适合需要频繁修改代码的开发场景。

#### 1. 启动数据库服务

```bash
cd /home/xyber-nova/Github/PixelSentry

# 只启动 PostgreSQL 和 Redis
sudo docker-compose up -d postgres redis

# 查看数据库是否启动成功
sudo docker-compose ps
```

#### 2. 后端开发

```bash
cd backend

# 配置环境变量
cp .env.example .env

# 编辑 .env，确保数据库连接正确
# DATABASE_URL=postgresql+asyncpg://pixelsentry:changeme@localhost:5432/pixelsentry
# REDIS_URL=redis://localhost:6379/0

# 同步依赖
uv sync

# 安装 Playwright 浏览器
uv run playwright install chromium

# 启动后端服务（开发模式，自动重载）
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：
- API：http://localhost:8000
- API 文档：http://localhost:8000/docs

#### 3. 前端开发

打开新终端：

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（自动重载）
npm run dev
```

访问：http://localhost:3000

---

### 方式三：完全本地开发（不使用 Docker）

需要手动安装 PostgreSQL 和 Redis。

#### 1. 安装数据库

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 安装 Redis
sudo apt install redis-server

# 启动服务
sudo systemctl start postgresql
sudo systemctl start redis-server
```

#### 2. 创建数据库

```bash
sudo -u postgres psql

# 在 PostgreSQL 命令行中执行：
CREATE DATABASE pixelsentry;
CREATE USER pixelsentry WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pixelsentry TO pixelsentry;
\q
```

#### 3. 配置并启动后端

```bash
cd backend
cp .env.example .env

# 编辑 .env，设置数据库密码
# DATABASE_URL=postgresql+asyncpg://pixelsentry:your_password@localhost:5432/pixelsentry

uv sync
uv run playwright install chromium
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

---

## 开发工作流

### 后端开发

1. **修改代码**：编辑 `backend/app/` 下的文件
2. **自动重载**：使用 `--reload` 参数，代码修改后自动重启
3. **查看日志**：终端会显示请求日志和错误信息
4. **测试 API**：访问 http://localhost:8000/docs 使用 Swagger UI 测试

### 前端开发

1. **修改代码**：编辑 `frontend/src/` 下的文件
2. **热重载**：Vite 会自动刷新浏览器
3. **查看效果**：浏览器自动更新
4. **调试**：使用浏览器开发者工具

---

## 常用命令

### 后端

```bash
# 安装新依赖
uv add <package-name>

# 运行测试
uv run pytest

# 代码格式化
uv run black app/
uv run ruff check app/

# 数据库迁移（如果使用 Alembic）
uv run alembic upgrade head
```

### 前端

```bash
# 安装新依赖
npm install <package-name>

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### Docker

```bash
# 重新构建并启动
sudo docker-compose up --build

# 只重新构建某个服务
sudo docker-compose build backend

# 查看日志
sudo docker-compose logs -f backend
sudo docker-compose logs -f frontend

# 进入容器
sudo docker-compose exec backend bash
sudo docker-compose exec postgres psql -U pixelsentry

# 清理所有容器和卷
sudo docker-compose down -v
```

---

## 故障排查

### 后端无法连接数据库

```bash
# 检查 PostgreSQL 是否运行
sudo docker-compose ps postgres
# 或
sudo systemctl status postgresql

# 检查端口是否被占用
sudo netstat -tulpn | grep 5432

# 测试数据库连接
psql -h localhost -U pixelsentry -d pixelsentry
```

### 前端无法连接后端

1. 确保后端在 http://localhost:8000 运行
2. 检查 `frontend/vite.config.ts` 中的代理配置
3. 查看浏览器控制台的网络请求

### Camoufox 浏览器问题

```bash
# 重新安装 Playwright 浏览器
cd backend
uv run playwright install chromium
uv run playwright install-deps chromium
```

---

## 推荐的开发设置

### 后端（混合模式）

```bash
# 终端 1：启动数据库
sudo docker-compose up postgres redis

# 终端 2：启动后端
cd backend
uv run uvicorn app.main:app --reload
```

### 前端

```bash
# 终端 3：启动前端
cd frontend
npm run dev
```

这样可以：
- ✅ 快速重启后端（不需要重建 Docker 镜像）
- ✅ 前端热重载
- ✅ 数据库持久化
- ✅ 方便调试

---

## 环境变量说明

### 后端 `.env`

```bash
# 数据库（Docker）
DATABASE_URL=postgresql+asyncpg://pixelsentry:changeme@localhost:5432/pixelsentry

# 数据库（本地）
# DATABASE_URL=postgresql+asyncpg://pixelsentry:your_password@localhost:5432/pixelsentry

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT 密钥（开发环境可以使用简单的值）
JWT_SECRET_KEY=dev-secret-key

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# 调试模式
DEBUG=True

# CORS（允许前端访问）
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Camoufox
CAMOUFOX_HEADLESS=False  # 开发时设为 False 可以看到浏览器
```

### 前端 `.env`

```bash
# API 地址（开发时使用代理，不需要设置）
# VITE_API_URL=http://localhost:8000
```

---

## 默认账户

- **管理员用户名**: `admin`
- **管理员密码**: `admin123`

首次启动后端时会自动创建管理员账户。
