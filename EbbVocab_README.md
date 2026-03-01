# 二、README.md（中文完整版）
# EbbVocab

EbbVocab 是一个支持多用户的背单词 Web 应用，基于“固定间隔艾宾浩斯记忆曲线”实现间隔重复复习。

本项目目标是：部署后可供朋友注册使用，每个用户的数据完全独立。

---

## 一、功能说明（MVP）

### 1. 多用户系统
- 注册
- 登录
- JWT 鉴权
- 用户数据完全隔离

### 2. 单词本管理
- 创建 / 删除 / 编辑 Deck
- 创建 / 编辑 / 删除 Word
- 批量导入：
  - word
  - word<TAB>definition

### 3. 复习系统（固定间隔调度）

等级与间隔：

| 等级 | 间隔 |
|------|------|
| L0 | 10分钟 |
| L1 | 1天 |
| L2 | 2天 |
| L3 | 4天 |
| L4 | 7天 |
| L5 | 15天 |
| L6 | 30天 |
| L7 | 60天 |

评分规则：

- 0（忘记）：回到 L0
- 1（困难）：下降 1 级
- 2（还行）：上升 1 级
- 3（熟练）：上升 2 级

所有 next_due_at 均由后端计算。

---

## 二、技术架构

前端：
- React + Vite + TypeScript

后端：
- FastAPI
- SQLAlchemy
- Alembic

数据库：
- 开发：SQLite
- 生产：PostgreSQL（必须）

部署：
- 前端：Vercel / Netlify
- 后端：Render / Fly.io
- 数据库：托管 Postgres

---

## 三、本地开发

### 1. 启动数据库（推荐 Docker）


docker compose up -d db
### 2. 启动后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
### 3. 启动前端
cd frontend
npm install
cp .env.example .env
npm run dev

### Windows PowerShell 推荐验收命令（Issue 1）

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# 默认使用 SQLite：DATABASE_URL=sqlite:///./ebbvocab.db
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

说明：
- Issue 1 可直接走 SQLite 验收路径，不依赖本地 Postgres。
- 若 PowerShell 中 `alembic` 或 `uvicorn` 命令找不到，优先使用 `python -m alembic` 与 `python -m uvicorn`。
- 启动后访问 `GET /health`，返回 JSON 并包含 `database` 字段。

## 四、环境变量

后端：

DATABASE_URL

SECRET_KEY

JWT_EXPIRE_MINUTES

CORS_ALLOW_ORIGINS

ENV

前端：

VITE_API_BASE_URL

## 五、部署给朋友使用（推荐方案）

推荐：

前端部署到 Vercel

后端部署到 Render

使用 Render 托管 Postgres

部署步骤：

1）创建 Render Web Service（指向 backend）
2）配置环境变量
3）执行 alembic upgrade head
4）前端部署并配置 API 地址
5）配置 CORS_ALLOW_ORIGINS

## 六、资源与成本说明

本项目数据为文本与复习记录：

即使 20 人使用

一年数据量也很小（通常 < 100MB）

免费云服务足够支持朋友测试。

## 七、安全说明

密码采用哈希存储

JWT 鉴权

严格 user_id 过滤

生产环境必须使用 Postgres

## 八、Issue 4 复习接口（/docs 操作）

先登录并获取 token：
- `POST /auth/register`
- `POST /auth/login`

在 `/docs` 右上角点击 `Authorize`，输入：
- `Bearer <access_token>`

推荐演示流程：
1. `POST /decks` 创建一个 deck
2. `POST /decks/{deck_id}/words/import`
   - `content` 示例：`apple<TAB>苹果` 换行 `banana`
3. `GET /reviews/queue?deck_id={deck_id}&limit=20`
   - 返回到期词；不足时会用新词补齐
4. `POST /reviews/{word_id}`，body 示例：`{"grade":4}`
   - 系统按 SM-2 简化规则更新 `repetition/interval/ease_factor/due_at`
   - 同时写入 `review_logs`
5. `GET /reviews/stats?deck_id={deck_id}`
   - 查看 `today_due_count`、`total_due_count`、`learned_count`、`new_count`
   - `next_7_days_due` 为未来 7 天到期聚合

## 九、Docker 一键启动与部署（Issue 10）

### 1）一键启动

在仓库根目录执行：

```powershell
docker compose up --build
```

启动后访问：
- 前端：http://localhost:8080
- 后端健康检查（容器内 API）：通过前端反代可访问 `http://localhost:8080/api/health`

说明：
- 前端由 `web` 容器（nginx）提供静态页面
- 后端由 `api` 容器（uvicorn）提供接口
- 前端通过 `/api/*` 反向代理访问后端，避免浏览器跨域问题

### 2）常用命令

```powershell
# 后台启动
docker compose up --build -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 仅重建并启动某个服务
docker compose up --build -d web
docker compose up --build -d api

# 停止并删除容器/网络
docker compose down

# 停止并删除容器/网络/数据卷（会清空 SQLite 数据）
docker compose down -v
```

### 3）环境变量说明

#### 后端（`api` 服务）
- `DATABASE_URL`：SQLite 路径（compose 默认 `sqlite:////app/data/ebbvocab.db`）
- `SECRET_KEY`：JWT 签名密钥（生产环境必须替换）
- `JWT_EXPIRE_MINUTES`：Token 过期时间（分钟）
- `ENV`：环境标识（示例：`production`）
- `CORS_ALLOW_ORIGINS`：允许跨域来源（逗号分隔）

#### 前端（`web` 服务）
- `VITE_API_BASE_URL`：前端构建时 API 基地址（compose 默认 `/api`）

### 4）验收步骤

1. 启动服务：`docker compose up --build`
2. 打开 `http://localhost:8080`，确认前端可访问
3. 在浏览器访问 `http://localhost:8080/api/health`，确认后端可用并返回 JSON
4. 在页面中注册/登录并创建单词本、添加单词，确认业务可用
5. 执行 `docker compose down` 后再 `docker compose up -d`，刷新页面确认数据仍在（SQLite volume 持久化）
