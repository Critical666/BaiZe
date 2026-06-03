# BaiZe（白泽）

> 白泽，上古神兽，通万物之情，晓天下之状。基于 RAG 的 SaaS 知识库平台。

用户创建知识库后上传文档，系统自动切块、向量化、存入 Milvus，即可通过自然语言对话从文档中检索答案，回答附带来源引用。

## 架构概览

```
用户浏览器
    │
┌───▼────────────────────────────────────────────┐
│  Nginx（静态资源 + 反向代理）                      │
└───┬────────────────┬──────────────┬───────────┘
    │                │              │
┌───▼───┐      ┌────▼────┐    ┌────▼─────┐
│React  │      │ FastAPI │    │  Celery   │
│前端    │ ───► │ 后端    │ ──►│  Worker   │
└───────┘      └──┬──┬───┘    │(文档处理) │
                  │  │        └────┬──────┘
          ┌───────▼┐ └─────────┐  │
          │SQLite  │           │  │
          │(元数据)│        ┌──▼──▼──┐
          └────────┘        │ Milvus │
                            │(向量库)│
                            └────────┘
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | React 19 + TypeScript + Ant Design + React Query |
| 后端 | FastAPI (Python 3.12) + SQLAlchemy + Celery |
| 向量数据库 | Milvus (支持 Milvus Lite 轻量部署) |
| 关系数据库 | SQLite |
| 缓存/消息队列 | Redis |
| 容器化 | Docker + Docker Compose |

## 功能

- **知识库管理**：创建、删除、搜索知识库
- **文档处理**：支持 PDF、Word、Markdown、TXT 格式，自动切块 + 向量化
- **RAG 对话**：基于文档内容的智能问答，返回答案 + 来源引用
- **权限控制**：管理员 / 普通用户角色体系，JWT 认证
- **统计面板**：知识库数、文档数、切块数等实时统计

## 快速开始

### 前置条件

- [Docker](https://docs.docker.com/get-docker/) 和 Docker Compose
- Node.js 20+ (仅本地开发前端时需要)
- Python 3.12+ (仅本地开发后端时需要)

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# 必须修改：填入你的 OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# 可选：管理员账户（不修改则使用默认值）
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_EMAIL=admin@baize.com
INIT_ADMIN_PASSWORD=admin123
```

> Embedding 默认使用本地 `sentence-transformers` 模型，无需额外 API Key。

### 2. 启动服务

```bash
docker compose up --build -d
```

首次启动需要构建镜像（含依赖安装），请耐心等待。

### 3. 访问应用

- **前端**：http://localhost
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

### 4. 默认管理员账户

| 字段 | 值 |
|------|------|
| 用户名 | admin |
| 邮箱 | admin@baize.com |
| 密码 | admin123 |

> 请在生产环境中修改默认密码。

## 本地开发

如需在本地分别开发前后端（带热重载），使用开发配置：

```bash
# 启动 Redis + 后端 API（热重载）
docker compose -f docker-compose.dev.yml up --build -d
```

后端代码挂载到容器内，修改后自动重载。

前端开发需本地安装依赖后运行：

```bash
cd frontend
pnpm install
pnpm dev
```

前端开发服务器运行在 http://localhost:5173，自动代理后端 API。

## 项目结构

```
BaiZe/
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由层
│   │   ├── core/                # 配置、安全、数据库
│   │   ├── models/              # SQLAlchemy ORM 模型
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── services/            # 业务逻辑层
│   │   ├── utils/               # 工具函数
│   │   └── main.py              # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                    # React 前端
│   ├── src/
│   │   ├── api/                 # API 调用封装
│   │   ├── components/          # 通用组件
│   │   ├── hooks/               # 自定义 Hooks
│   │   ├── pages/               # 页面组件
│   │   ├── types/               # TypeScript 类型
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml           # 生产环境编排
├── docker-compose.dev.yml       # 开发环境编排
├── .env.example                 # 环境变量模板
└── DEVELOPMENT_PLAN.md          # 开发计划
```

## API 路由

| 方法 | 路由 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 注册 | 公开 |
| POST | `/api/v1/auth/login` | 登录 | 公开 |
| PUT | `/api/v1/users/{id}/role` | 修改角色 | admin |
| POST | `/api/v1/knowledge-bases` | 创建知识库 | admin |
| GET | `/api/v1/knowledge-bases` | 知识库列表 | 登录 |
| GET | `/api/v1/knowledge-bases/{id}` | 知识库详情 | 登录 |
| DELETE | `/api/v1/knowledge-bases/{id}` | 删除知识库 | admin |
| POST | `/api/v1/knowledge-bases/{id}/documents` | 上传文档 | 登录 |
| GET | `/api/v1/knowledge-bases/{id}/documents` | 文档列表 | 登录 |
| POST | `/api/v1/knowledge-bases/{id}/chat` | RAG 对话 | 登录 |
| GET | `/api/v1/stats` | 统计概览 | 登录 |

## 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | SQLite 数据库路径 | `sqlite:///./data/baize.db` |
| `SECRET_KEY` | JWT 签名密钥 | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `30` |
| `INIT_ADMIN_USERNAME` | 初始管理员用户名 | `admin` |
| `INIT_ADMIN_EMAIL` | 初始管理员邮箱 | `admin@baize.com` |
| `INIT_ADMIN_PASSWORD` | 初始管理员密码 | `admin123` |
| `OPENAI_API_KEY` | OpenAI API Key | - |
| `OPENAI_BASE_URL` | OpenAI API 地址 | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | LLM 模型 | `gpt-4o-mini` |
| `EMBEDDING_PROVIDER` | Embedding 提供方 (`local` / `openai`) | `local` |
| `EMBEDDING_MODEL` | 本地 Embedding 模型 | `paraphrase-multilingual-MiniLM-L12-v2` |
| `REDIS_URL` | Redis 连接地址 | `redis://redis:6379/0` |

## License

MIT
