# 阶段 A+B 沉淀文档 — 后端基础设施与前端骨架

## 完成时间

2026-06-01

## 目标回顾

后端：建表、JWT 认证、基础 CRUD（不集成外部服务）。
前端：Layout + 路由 + 所有页面骨架，用假/真实数据跑通完整页面跳转。
A 与 B 并行推进。

---

## 后端产出

| 模块 | 文件 | 说明 |
|------|------|------|
| ORM 模型 | `models/user.py`, `knowledge_base.py`, `document.py` | 3 张表，`Base` 统一在 `__init__.py` |
| 数据库 | `core/database.py` | SQLAlchemy 引擎 + `get_db` 依赖注入 |
| JWT 安全 | `core/security.py` | bcrypt 哈希 + JWT 签发/校验（payload 含 role） |
| 配置 | `core/config.py` | Pydantic Settings，含初始管理员凭证 |
| 依赖注入 | `api/deps.py` | `get_current_user` + 各 Service 工厂函数 |
| 认证 Service | `services/auth_service.py` | 注册（role 硬编码 user）、登录、`ensure_admin` |
| 知识库 Service | `services/knowledge_service.py` | CRUD，单据 SQLite，不碰 Milvus |
| 文档 Service | `services/document_service.py` | 仅存元数据，不做切块/向量化 |
| 聊天 Service | `services/chat_service.py` | 占位回答 |
| 统计 Service | `services/stats_service.py` | count 查询 |
| API 端点 | 5 个 endpoint 文件 | 全部 14 条路由挂载到 `/api/v1` |
| 入口 | `main.py` | lifespan 启动时自动创建初始管理员 |

### 后端目录结构

```
backend/
├── app/
│   ├── api/v1/endpoints/   (auth, knowledge, document, chat, stats)
│   ├── core/               (config, database, security)
│   ├── models/             (user, knowledge_base, document)
│   ├── schemas/            (5 个 Schema 文件)
│   ├── services/           (5 个 Service 文件)
│   ├── utils/
│   └── main.py
├── tests/
├── requirements.txt
└── .env.example
```

---

## 前端产出

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录/注册 | `/login` | 标签页切换，对接真实 API |
| 知识库列表 | `/` | 卡片网格，新建/删除弹窗 |
| 知识库详情 | `/kb/:id` | 文档列表 + 上传 + 状态标签 |
| 对话 | `/kb/:id/chat` | 聊天气泡 + 来源引用 + 空状态 |
| 统计面板 | `/stats` | 4 个统计卡片 |

### 前端目录结构

```
frontend/src/
├── api/          (client, auth, knowledge)
├── components/   (Layout)
├── pages/        (Login, Home, KnowledgeBase, Chat, Stats)
├── types/        (api.ts)
├── router.tsx
├── App.tsx
└── main.tsx
```

---

## 技术验证

- ✅ 后端启动成功，14 条路由就绪
- ✅ `tsc --noEmit` 通过
- ✅ `vite build` 构建成功

---

## 阶段 A+B 核心原则执行情况

| 原则 | 执行 |
|------|------|
| 基础 CRUD 不集成外部服务 | ✅ 聊天占位、文档存元数据 |
| Walking Skeleton | ✅ 前后端链路跑通 |
| 权限延后 | ✅ `current_user` 注入就绪，装饰器未挂 |
| 类型来源前端用 `@/types/api` | ✅ 类型独立文件，后续 openapi 覆盖 |

## Git 提交记录

- `feat(后端): 阶段0完成-API契约设计，定义全部Schema`
- `docs(用户): 补充身份机制设计-角色创建与提升流程`
- `docs(开发计划): 补充身份机制与用户管理接口`
- `docs(阶段0): 阶段0沉淀文档`
