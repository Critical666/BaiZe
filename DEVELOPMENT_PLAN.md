# BaiZe 开发计划

> 本文档是遵循 [AGENTS.md](./Agent.md) 中定义的开发流程与技术规范的具体开发指南。

---

## 一、项目定位

**BaiZe（白泽）**——基于 RAG 的 SaaS 知识库平台。用户创建知识库后上传文档，系统自动切块、向量化、存入 Milvus，即可通过自然语言对话从文档中检索答案。

---

## 二、整体架构

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

| 组件 | 职责 |
|------|------|
| **React 前端** | SPA 管理后台，知识库管理、聊天界面、统计面板 |
| **FastAPI 后端** | REST API，认证鉴权，CRUD，RAG 调度 |
| **Celery Worker** | 异步执行文档切块、向量化、Milvus 写入 |
| **SQLite** | 用户、知识库、文档、聊天记录的元数据存储 |
| **Milvus** | 文档向量存储，相似度检索 |

---

## 三、核心数据模型

```
User
  id: UUID
  username: str
  email: str
  password_hash: str
  role: "admin" | "user"
  created_at: datetime

KnowledgeBase
  id: UUID
  name: str
  description: str | null
  owner_id: UUID → User
  created_at: datetime
  updated_at: datetime

Document
  id: UUID
  kb_id: UUID → KnowledgeBase
  filename: str
  file_size: int
  chunk_count: int            # 切块后更新
  status: "pending" | "processing" | "done" | "failed"
  uploaded_by: UUID → User
  created_at: datetime
```

### 3.1 身份机制

| 机制 | 说明 |
|------|------|
| **角色定义** | `admin`（管理员）与 `user`（普通用户），存储在 `role` 字段 |
| **用户注册** | 所有自主注册用户默认为 `user`，注册接口不暴露 `role` 参数，由服务端硬编码，防止前端伪造 |
| **首个管理员** | 系统启动时由 `seed.py` 自动创建，凭证从环境变量 `INIT_ADMIN_*` 读取 |
| **权限提升** | 管理员通过 `PUT /users/{id}/role` 接口将其他用户提升为 `admin` |
| **Token 携带** | JWT Payload 中包含 `role` 字段，中间件读取后注入 `current_user`，避免每次查数据库 |

---

## 四、API 路由设计

### 4.1 认证

| 方法 | 路由 | 说明 |
|------|------|------|
| `POST` | `/api/v1/auth/register` | 注册 |
| `POST` | `/api/v1/auth/login` | 登录，返回 JWT Token |

### 4.2 用户管理

| 方法 | 路由 | 说明 | 权限 |
|------|------|------|------|
| `PUT` | `/api/v1/users/{id}/role` | 修改用户角色 | admin |

### 4.3 知识库

| 方法 | 路由 | 说明 | 权限 |
|------|------|------|------|
| `POST` | `/api/v1/knowledge-bases` | 创建知识库 | admin |
| `GET` | `/api/v1/knowledge-bases` | 列表（支持搜索 + 分页） | 登录即可 |
| `GET` | `/api/v1/knowledge-bases/{id}` | 详情（含文档数量） | 登录即可 |
| `DELETE` | `/api/v1/knowledge-bases/{id}` | 删除（级联删文档和向量） | admin |

### 4.4 文档

| 方法 | 路由 | 说明 | 权限 |
|------|------|------|------|
| `POST` | `/api/v1/knowledge-bases/{id}/documents` | 上传文档（异步触发处理） | 登录即可 |
| `GET` | `/api/v1/knowledge-bases/{id}/documents` | 文档列表（支持分页） | 登录即可 |

### 4.5 聊天

| 方法 | 路由 | 说明 |
|------|------|------|
| `POST` | `/api/v1/knowledge-bases/{id}/chat` | 发送消息，返回 RAG 回答 + 来源引用 |

### 4.6 统计

| 方法 | 路由 | 说明 |
|------|------|------|
| `GET` | `/api/v1/stats` | 统计概览（知识库数、文档数、切块数） |

---

## 五、核心业务流程

### 5.1 文档处理流水线

```
用户上传文件
    ↓
后端接收 → 写 Document 记录（status=pending）
    ↓
投递 Celery 任务
    ↓
Celery Worker：
  1. 格式解析（PDF / Word / Markdown / TXT）
  2. 文本清洗（去除空行、特殊字符）
  3. 切块（500 字 + 50 字重叠）
  4. 向量化（Embedding 模型）
  5. 写入 Milvus（带 kb_id 标签隔离）
  6. 更新 Document.status = done、chunk_count
```

### 5.2 RAG 对话流程

```
用户提问
    ↓
将问题向量化（与文档向量同模型）
    ↓
Milvus 相似度 + BM25混合检索 → Top-K 切块（限定 kb_id）
    ↓
构建 Prompt：
  System: "你是知识库助手，请基于以下文档内容回答...（此处在开发时应该根据prompt工程规范，写的更加完善）"
  Context: 检索到的 K 个文本块（标注来源）
  Question: 用户原始问题
    ↓
调用 LLM 生成回答
    ↓
返回 { answer, sources: ["文档名 P3-5", ...] }
```

### 5.3 权限模型

| 功能 | 管理员 (admin) | 普通用户 (user) |
|------|:---:|:---:|
| 注册 / 登录 | ✅ | ✅ |
| 创建知识库 | ✅ | ❌ |
| 删除知识库 | ✅ | ❌ |
| 上传文档 | ✅ | ✅（仅限被授权的知识库） |
| 聊天 | ✅ | ✅ |
| 查看统计（全量） | ✅ | ❌（仅自己的） |

---

## 六、统计面板设计

```
┌────────────────────────────────────────────────────┐
│  统计概览                                            │
├──────────┬──────────┬──────────┬───────────────────┤
│ 知识库   │ 文档总数  │ 切块总数  │ 近7天对话次数      │
│   12    │   156   │  4,320  │      892         │
├──────────┴──────────┴──────────┴───────────────────┤
│                                                     │
│  每个知识库的文档分布（饼图）                          │
│  近7天对话次数趋势（折线图）                           │
│  热门提问 TOP 10                                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 七、分阶段开发计划

### 阶段 0：API 契约设计

**目标**：定死所有接口的请求/响应结构。

**产出**：

```python
# backend/app/schemas/ 下新建
#   user.py        — UserCreate, UserLogin, UserResponse, TokenResponse
#   knowledge_base.py — KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseDetail
#   document.py    — DocumentUploadResponse, DocumentResponse
#   chat.py        — ChatRequest, ChatResponse
#   stats.py       — StatsResponse
```

**验证**：前端运行 `pnpm generate-api-types`，`tsc --noEmit` 通过。

---

### 阶段 A + B（并行）

#### A：后端基础设施

| 任务 | 文件 | 说明 |
|------|------|------|
| 建表迁移 | `backend/app/models/` + Alembic | `User`、`KnowledgeBase`、`Document` 三张表 |
| JWT 认证 | `backend/app/core/security.py` | Token 签发/校验 |
| 注册登录 | `backend/app/api/v1/endpoints/auth.py` | 返回 JWT，权限装饰器暂不生效 |
| 知识库 CRUD | `backend/app/api/v1/endpoints/knowledge.py` | 只读写 SQLite，不管 Milvus |
| 文档上传 | `backend/app/api/v1/endpoints/document.py` | 只存文件名，不切块不向量化 |
| 聊天占位 | `backend/app/api/v1/endpoints/chat.py` | 直接返回 `"RAG 模块待实现"` |
| 统计 CRUD | `backend/app/api/v1/endpoints/stats.py` | 从 SQLite 查 count，不涉及向量数据 |

#### B：前端骨架

| 任务 | 文件 | 说明 |
|------|------|------|
| Layout | `frontend/src/components/Layout.tsx` | Header + Sidebar + 内容区 |
| 路由 | `frontend/src/router.tsx` | `/login` `/` `/kb/:id` `/stats` |
| 登录页 | `frontend/src/pages/LoginPage.tsx` | 表单 + 假登录 |
| 知识库列表 | `frontend/src/pages/HomePage.tsx` | 3 条假数据，可跳转 |
| 知识库详情 | `frontend/src/pages/KnowledgeBasePage.tsx` | 假文档列表 |
| 聊天页 | `frontend/src/pages/ChatPage.tsx` | 假对话 |
| 统计页 | `frontend/src/pages/StatsPage.tsx` | 4 个假数字 |

**阶段 A + B 交付物**：前端用假数据能完成登录 → 浏览知识库 → 打开详情 → 进入聊天 → 查看统计的完整页面跳转。

---

### 阶段 A2 + B2（并行）

#### A2：核心 RAG 链路

| 任务 | 说明 |
|------|------|
| Celery 配置 | 连接 Redis/RabbitMQ，注册异步任务 |
| 文档解析 | PDF（PyPDF2）、Word（python-docx）、Markdown、TXT |
| 文本切块 | 500 字固定长度 + 50 字重叠 |
| Embedding | 挂载 Embedding 模型，文本转向量 |
| Milvus 集成 | 连接、创建 Collection、写入向量、相似度检索 |
| RAG 对话 | 检索 + Prompt 构建 + LLM 调用 |
| 日志记录 | LLM 调用耗时、Milvus 查询耗时、切块耗时 |

#### B2：页面完善

| 任务 | 说明 |
|------|------|
| 登录对接 | 假数据换真实 JWT 登录流程 |
| 创建知识库弹窗 | 表单 → 调 API → 刷新列表 |
| 文档上传组件 | 拖拽上传 + 进度条 + 状态标签 |
| 聊天界面 | 对话气泡 + 来源引用 + 打字动效 |
| 统计面板 | 真实数据替换假数字 |

**阶段 A2 + B2 交付物**：手动完成"创建知识库 → 上传 PDF → 等待处理完成 → 聊天提问 → 得到带来源引用的回答"全流程。

---

### 阶段 3：联调收尾

| 任务 | 说明 |
|------|------|
| 权限生效 | `@require_admin` 装饰器挂载，普通用户无法创建/删除知识库 |
| 前端切真 API | 所有假数据下线，`apiClient` 对接到真实路由 |
| 知识库隔离 | 验证用户 A 无法访问用户 B 的知识库文档 |
| Docker 编排 | `docker-compose.yml`：FastAPI + Celery + Milvus + Redis + Nginx |
| 一键启动 | `docker compose up` → 浏览器打开 → 完整产品体验 |

---

## 八、风险点

| 风险 | 影响 | 应对 |
|------|------|------|
| Milvus 版本兼容 | 阶段 A2 卡住 | 使用 Docker 固定 Milvus 版本，不追最新版 |
| LLM 调用延迟 | 聊天响应慢 | 先做非流式，后加 SSE 流式输出 |
| 大文件切块耗时长 | 用户体验差 | Celery 异步 + 前端轮询状态 |
| Celery 任务丢失 | 文档上传后"卡住" | 日志记录 + 前端展示失败状态并支持重试 |
| 向量模型选择 | 检索效果差 | 先用 OpenAI text-embedding-3-small，效果好则不变 |

---

## 九、验收标准

- [ ] 管理员能创建/删除知识库
- [ ] 普通用户不能创建/删除知识库
- [ ] 上传 PDF/Word/Markdown/TXT 后自动切块向量化
- [ ] 聊天返回带来源引用的回答
- [ ] 知识库之间文档完全隔离
- [ ] 统计面板显示实时数据
- [ ] `docker compose up` 一键启动全系统
