# EventFlow

极简「事件记录器」微信小程序。提前创建可复用事件卡片，点击即可记录；持续型事件可开始/结束计时。

> 当前为第一阶段：可扩展、可运行的项目基础架构 + 核心后端 + 最基础的小程序页面。

## 技术栈

| 端 | 技术 |
|----|------|
| 前端 | 微信原生小程序 · TypeScript · WXML · WXSS |
| 后端 | Python · FastAPI · SQLAlchemy 2.x · Pydantic · MySQL 8 · Alembic |
| 认证 | 微信 code2Session + JWT |
| 部署 | Linux · Docker Compose · Nginx |

## 目录结构

```
event-flow/
├── docker-compose.yml
├── .env.example
├── nginx/            # Nginx 反向代理配置
├── server/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py         # 鉴权/权限依赖
│   │   ├── security.py     # JWT
│   │   ├── wechat.py       # 微信 code2Session
│   │   ├── models/         # SQLAlchemy 模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── routers/        # API 路由
│   ├── migrations/         # Alembic
│   └── tests/
└── miniprogram/      # 微信小程序
```

## 本地运行

### 1. 后端（Docker Compose）

```bash
# 复制环境变量
cp .env.example .env
# 编辑 .env，设置 MYSQL_PASSWORD、WECHAT_APP_ID、WECHAT_APP_SECRET、JWT_SECRET

# 启动 MySQL + FastAPI + Nginx（生产模式：仅暴露 Nginx 80/443，MySQL/FastAPI 走内部网络）
docker compose up -d --build

# 初始化数据库（首次）
docker compose exec server alembic upgrade head
```

> **本地开发**需要直连 MySQL(3306) / FastAPI(8000) 时，用 dev override：
> ```bash
> docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
> ```

访问：
- API 文档：<http://localhost:8000/docs>（生产仅通过 Nginx，需 dev override 才直连 8000）
- 健康检查：<http://localhost:8000/health>
- Nginx 代理：<http://localhost/docs>

### 2. 后端（本地开发，不用 Docker）

```bash
cd server
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # 编辑配置

alembic upgrade head
uvicorn app.main:app --reload
```

> 本地无真实微信 AppID 时，可在 `.env` 设置 `WECHAT_MOCK_OPENID=任意字符串`，
> 登录接口将跳过真实微信调用，直接使用该 openid。
> **注意**：`ENV=prod` 时禁止设置 Mock 登录，且会强制校验 JWT/微信配置。

### 3. 运行测试

```bash
cd server
pytest
```

### 4. 微信小程序

1. 用微信开发者工具打开 `miniprogram/` 目录。
2. 首次打开前先安装依赖（提供 TS 类型定义）：
   ```bash
   cd miniprogram
   npm install
   ```
3. `project.config.json` 中 `appid` 替换为你自己的小程序 AppID。
4. `utils/config.ts` 中 `BASE_URL` 改为你的后端地址（本地为 `http://localhost:8000`）。
5. 开发阶段需在开发者工具「详情 → 本地设置」勾选「不校验合法域名」。

## 环境变量

| 变量 | 说明 |
|------|------|
| `ENV` | 运行环境 `dev`/`prod`。`prod` 下强制校验 JWT/微信配置，禁止 Mock 登录 |
| `MYSQL_HOST` / `MYSQL_PORT` / `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` | 数据库连接 |
| `WECHAT_APP_ID` / `WECHAT_APP_SECRET` | 微信小程序凭据（**仅存环境变量，禁止入库**） |
| `JWT_SECRET` | JWT 签名密钥（生产必须 ≥16 字符） |
| `WECHAT_MOCK_OPENID` | 本地测试用，跳过真实微信调用 |

## 数据模型

- `User`：用户（openid 唯一）
- `Space`：空间（owner + invite_code）
- `SpaceMember`：空间成员（owner/admin/member）
- `Card`：事件卡片（point/duration，软删除）
- `Event`：事件记录（软删除，UTC 时间）

详见 `server/migrations/versions/0001_initial.py`。

## API 概览

| 方法 | 路径 |
|------|------|
| POST | `/api/auth/wechat` |
| GET/POST | `/api/spaces` |
| GET | `/api/spaces/{id}` |
| GET/POST | `/api/spaces/{id}/cards` |
| PATCH/DELETE | `/api/cards/{id}` |
| GET | `/api/spaces/{id}/events` |
| POST | `/api/events` |
| PATCH/DELETE | `/api/events/{id}` |

除登录外所有接口均需 `Authorization: Bearer <token>`，且校验当前用户是否属于目标空间。

## 设计约定

- 数据库统一存 UTC；API 输出的时间带 `Z` 时区标记（如 `2026-09-05T07:30:00Z`），前端 JS 可直接正确解析。
- 接口按 `day=YYYY-MM-DD`（东八区）过滤当天事件，采用「区间重叠」语义，跨天事件（如 23:00 睡到次日 07:00）也能正确命中。
- 同一用户在同一 Space 同一时间只允许一个进行中的持续事件，启动新卡片会自动结束上一个。
- Event / Card 均软删除。
- 权限：owner/admin 可管理卡片，member 只读卡片、可创建/修改自己的事件。
- 不引入 Redis / Celery / 消息队列 / 微服务。
