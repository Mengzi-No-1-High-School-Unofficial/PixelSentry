# PixelSentry - 冬日绘版 Token 收集工具

一个用于自动化收集和管理洛谷冬日绘版 Access Key 的工具。

## 功能特性

- 🔐 **自动化 Token 获取**：通过 Camoufox 浏览器自动化绕过 CF 盾，完成完整的 Token 获取流程
- 🔄 **定时验证**：自动定时验证 Access Key 的有效性
- 👨‍💼 **管理面板**：提供完整的管理界面，查看和管理所有 Access Key
- 🔒 **JWT 认证**：使用 JWT Token 保护管理员接口
- 🐳 **Docker 支持**：支持 Docker 和 Docker Compose 一键部署
- ⚡ **异步高性能**：后端使用 FastAPI + SQLAlchemy 异步架构

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (异步)
- PostgreSQL
- Redis
- Camoufox + Playwright
- JWT 认证

### 前端
- Vue.js 3 (Composition API)
- TypeScript
- Vite
- TailwindCSS + DaisyUI
- Pinia
- Axios

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆仓库
```bash
git clone <repository-url>
cd PixelSentry
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库密码和 JWT 密钥
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 传统部署

#### 后端部署

1. 安装依赖
```bash
cd backend
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

3. 初始化数据库
```bash
# 确保 PostgreSQL 已启动并创建数据库
# 运行应用会自动创建表
```

4. 启动服务
```bash
python -m app.main
# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 前端部署

1. 安装依赖
```bash
cd frontend
npm install
```

2. 开发模式
```bash
npm run dev
```

3. 生产构建
```bash
npm run build
# 构建产物在 dist 目录
```

## 使用说明

### 用户端

1. 访问首页
2. 输入洛谷用户 ID 和剪贴板 ID
3. 提交后等待处理（10-30 秒）
4. 查看获取到的 Access Key

### 管理员端

1. 访问 `/admin/login`
2. 使用配置的管理员账户登录（默认：admin/admin123）
3. 查看所有 Access Key 和统计信息
4. 手动触发验证

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要接口

- `POST /api/submit` - 提交剪贴板信息
- `GET /api/submission/{id}` - 查询提交状态
- `POST /api/admin/auth/login` - 管理员登录
- `GET /api/admin/keys` - 获取所有 Access Key
- `POST /api/admin/validate/{id}` - 手动验证 Key
- `GET /api/admin/stats` - 获取统计信息

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL 连接字符串 | - |
| REDIS_URL | Redis 连接字符串 | redis://localhost:6379/0 |
| JWT_SECRET_KEY | JWT 密钥 | - |
| ADMIN_USERNAME | 管理员用户名 | admin |
| ADMIN_PASSWORD | 管理员密码 | admin123 |
| VALIDATION_INTERVAL_MINUTES | 验证间隔（分钟） | 5 |

## 开发

### 后端开发

```bash
cd backend
uv pip install -e ".[dev]"
python -m app.main
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
