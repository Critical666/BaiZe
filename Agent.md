# AGENTS.md - 项目技术规范手册

本文档为该项目的总体约束，在开发本文档所在项目时，请严格遵守。

## 1. 项目背景
白泽，上古神兽，通万物之情，晓天下之状。项目取其名，意在赋予系统如白泽般的智慧——通读文档，洞悉一切知识。

## 2. 技术栈（强制约束）

### 2.1 前端
React 19 + TypeScript

> 在生成前端代码时，应该读取 `ui-ux-pro-max` skill 进行参考。

### 2.2 后端
FastAPI（Python 3.12+）

### 2.3 基础设施

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| **向量数据库** | Milvus | 文档向量存储与相似度检索 |
| **关系数据库** | SQLite | 用户、知识库等元数据存储 |
| **容器化** | Docker + Docker Compose | 开发与部署环境一致 |
| **CI/CD** | GitHub Actions / GitLab CI | 自动化测试与构建 |

## 3. 代码规范（自动检查 + 必须遵守）

### 3.1 命名规范
| 元素 | 规范 | 示例 |
|------|------|------|
| 文件/文件夹 | kebab-case | `order-service.ts` |
| 类/接口/类型 | PascalCase | `OrderEntity` |
| 变量/函数/方法 | camelCase | `getUserById`, `isActive` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 数据库表/字段 | snake_case | `order_items`, `created_at` |

### 3.2 目录结构（必须遵循）
#### 顶层目录划分
采用前后端一体的 Monorepo 结构，以 backend/ 和 frontend/ 作为顶层划分。
```
project-root/
├── backend/                     # 后端 FastAPI 应用
├── frontend/                    # 前端 React + TypeScript 应用
├── docker-compose.yml           # 一键启动服务编排
└── README.md
```

#### 后端目录(backend/)详解

```
backend/
├── app/
│   ├── api/                     # 接口层：HTTP 路由与依赖注入
│   │   ├── v1/
│   │   │   ├── endpoints/       # 具体业务路由文件
│   │   │   └── __init__.py
│   │   └── deps.py              # 依赖项（DB会话、当前用户）
│   │
│   ├── core/                    # 核心配置与基础设施
│   │   ├── config.py            # Pydantic Settings 配置类
│   │   ├── security.py          # JWT 生成、密码哈希验证
│   │   └── database.py          # SQLAlchemy 引擎与连接池
│   │
│   ├── models/                  # 数据模型层：SQLAlchemy ORM 表定义
│   │   ├── knowledge_base.py
│   │   └── user.py
│   │
│   ├── schemas/                 # Pydantic 模型：API 请求/响应结构校验
│   │   ├── knowledge_base.py    # 前后端类型契约的唯一源头
│   │   └── user.py
│   │
│   ├── services/                # 业务逻辑层：核心功能实现
│   │   ├── knowledge_base.py    # 知识库增删改查、向量库同步逻辑
│   │   └── auth.py              # 登录注册、权限校验
│   │
│   ├── utils/                   # 通用工具函数（文件解析、日志等）
│   └── main.py                  # FastAPI 应用入口
├── tests/                       # 单元测试与集成测试
├── requirements.txt             # 依赖清单
└── .env.example                 # 环境变量模板
```

| 目录 | 核心职责 | 关键点 |
|------|------|------|
| app/api | HTTP入口层。定义路由、依赖注入、状态码 | 绝不可以包含业务逻辑，仅做参数接收与响应返还。 |
| app/schemas/ | 数据形状定义。Pydantic模型定义，负责请求校验与响应过滤 | 前后端契约的唯一来源，变动必须前后端同步修改 |
| app/models/ | 数据库映射。SQLAlchemy ORM模型，定义表结构与关系 | 暂无 |
| app/services/ | 核心业务逻辑/所有复杂操作，事务处理、外部调用均在此处 | 此处是开发时的重点 |
| app/core/ | 基础设施。例如配置管理、数据库连接池以及安全组件等 | 环境变量读取、JWT 生成与验证 |

#### 前端目录(frontend/)详解
```
frontend/
├── public/                      # 静态资源（index.html、favicon）
├── src/
│   ├── api/                     # API 接口调用（与后端路由一一对应）
│   │   ├── client.ts            # Axios 实例、请求/响应拦截器
│   │   ├── knowledge.ts         # 知识库相关 API
│   │   └── auth.ts              # 认证相关 API
│   │
│   ├── components/              # 通用可复用 UI 组件
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   └── Layout.tsx
│   │
│   ├── hooks/                   # 自定义 Hooks
│   │   ├── useCreateKB.ts
│   │   └── useAuth.ts
│   │
│   ├── pages/                   # 路由页面组件（与 URL 一一对应）
│   │   ├── HomePage.tsx
│   │   ├── LoginPage.tsx
│   │   └── KnowledgeBasePage.tsx
│   │
│   ├── utils/                   # 工具函数（日期格式化、防抖等）
│   ├── types/                   # 全局 TypeScript 类型定义
│   │   └── api.d.ts             # 由 OpenAPI 自动生成，严禁手动修改
│   ├── App.tsx                  # 根组件
│   └── main.tsx                 # 应用入口
│
├── index.html
├── package.json
├── tsconfig.json                # TypeScript 配置
├── vite.config.ts               # 构建工具配置
└── .env.local                   # 本地环境变量
```
| 目录 | 核心职责 | 关键点 |
|------|------|------|
| src/api | API调用层。封装所有后端接口调用，统一使用client.ts | 每个后端路由对应一个文件，保持前后端映射关系清晰 |
| src/components | 通用可复用 UI 组件。 | 尽量复用，避免重复造轮子 |
| src/hooks | 业务逻辑封装。自定义Hooks，封装状态管理、API调用 | api/ 驱动数据获取，pages/ 驱动 UI 更新 |
| src/pages | 路由页面组件（与 URL 一一对应） | 负责数据获取与布局编排，组合components/ 和 hooks/ |
| src/types | 全局 TypeScript 类型定义（由后端OpenAPI自动生成） | 开发中严禁手动修改此目录 |

#### 前后端交互代码示例

##### 后端代码示例

**`app/schemas/knowledge_base.py`** — 定义数据结构

```python
from pydantic import BaseModel, Field
from typing import Optional


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
```

**`app/api/v1/endpoints/knowledge.py`** — 定义路由

> 凡是在 API 层调用 Service 层逻辑的，都应通过 `Depends()` 注入。

```python
from fastapi import APIRouter, Depends
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.services.knowledge_service import KnowledgeService


router = APIRouter()


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
def create_kb(
    data: KnowledgeBaseCreate,
    service: KnowledgeService = Depends(),
):
    """创建新的知识库。"""
    return service.create(data)
```

##### 前端代码示例
**`frontend/src/api/client.ts`** — 封装 Axios 实例

> 响应拦截器自动解包 `response.data`，调用方拿到的直接是业务数据。

```typescript
import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 10000,
    headers: {'Content-Type': 'application/json'},
});

// 响应拦截器，解包 response.data，调用方直接拿到业务数据
apiClient.interceptors.response.use(
    (response) => response.data,
    (error) => Promise.reject(error.response?.data || error)
);

export default apiClient;
```


**`frontend/src/api/knowledge.ts`** — 封装 API 调用

```typescript
import apiClient from '@/api/client';
import type {KnowledgeBaseCreate, KnowledgeBaseResponse} from '@/types/api';

export const createKnowledgeBase = (data: KnowledgeBaseCreate) => {
    return apiClient.post<KnowledgeBaseResponse>('/api/v1/knowledge-bases', data);
}
```

**`frontend/src/hooks/useCreateKB.ts`** — 业务 Hook

```typescript
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {createKnowledgeBase} from '@/api/knowledge';

export const useCreateKB = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: createKnowledgeBase,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['knowledge-base'] });
        },
    });
};
```

**`frontend/src/pages/KnowledgeBasePage.tsx`** — 页面组件

```typescript
import { Button } from '@/components/Button';
import { useCreateKB } from '@/hooks/useCreateKB';

export const KnowledgeBasePage = () => {
    const {mutate, isPending} = useCreateKB();

    return (
        <Button
            isLoading={isPending}
            onClick={() => mutate({ name: '产品手册', description: 'V2.0' })}
        >
            新建知识库
        </Button>
    );
};
```

##### 关键规范

| 规范 | 说明 |
|------|------|
| **类型来源** | 前端必须使用 `@/types/api` 中的类型，严禁手写接口类型 |
| **API 封装** | 所有请求必须通过 `apiClient` 发起 |
| **状态管理** | 服务端数据使用 React Query，客户端 UI 状态使用 Zustand |
| **错误处理** | 业务错误由 API 层统一处理，组件层只需处理 `isError` 状态 |

#### `src/types/` 自动生成

FastAPI 自动暴露 `/openapi.json`，前端通过 `openapi-typescript` 将其转为 TypeScript 类型，后端 Schema 作为唯一事实来源。

**安装依赖：**

```bash
cd frontend
pnpm add -D openapi-typescript
```

**`frontend/package.json` 添加脚本：**

```json
{
  "scripts": {
    "generate-api-types": "npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts"
  }
}
```

**后端启动后执行：**

```bash
pnpm generate-api-types
```

**生成示例（`src/types/api.d.ts`）：**

```typescript
// 由 openapi-typescript 自动生成，严禁手动修改

export interface KnowledgeBaseCreate {
  name: string;
  description?: string | null;
}

export interface KnowledgeBaseResponse {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
}

export interface ChatRequest {
  question: string;
  top_k?: number;
}

export interface ChatResponse {
  answer: string;
  sources?: string[];
}
```

**前端引用方式：**

```typescript
import type { KnowledgeBaseCreate, KnowledgeBaseResponse } from '@/types/api';
```

> 每次后端 Schema 变更后，重新运行 `pnpm generate-api-types` 即可同步，严禁手动编辑此目录下的文件。

### 3.3 代码风格

#### 前端（TypeScript，基于 ESLint + Prettier）
- 缩进：2 个空格
- 行尾分号：必须
- 字符串：单引号，SQL 语句中允许双引号
- 尾随逗号：多行时必须
- 每行最大字符：100
- 接口命名：不强制加 `I` 前缀（如 `OrderRepository` 而非 `IOrderRepository`）

```typescript
// ✅ 正确示例
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { KnowledgeBaseCreate, KnowledgeBaseResponse } from '@/types/api';
import apiClient from '@/api/client';

const MAX_RETRY_COUNT = 3;

export const createKnowledgeBase = (params: KnowledgeBaseCreate) => {
  return apiClient.post<KnowledgeBaseResponse>('/api/v1/knowledge-bases', params);
};

export const useCreateKB = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createKnowledgeBase,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge-base'] });
    },
  });
};
```

#### 后端（Python，基于 Ruff / Black）
- 缩进：4 个空格
- 行尾分号：禁止
- 字符串：双引号
- 尾随逗号：多行时必须
- 每行最大字符：88
- import 顺序：标准库 → 第三方库 → 项目内模块，每组间空一行

```python
# ✅ 正确示例
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse)
def create_kb(
    data: KnowledgeBaseCreate,
    service: KnowledgeService = Depends(),
):
    try:
        return service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 3.4 注释规范

#### 前端（TypeScript，JSDoc）
- 公共 API（导出函数/类）必须有 JSDoc。
- 复杂业务逻辑必须内联注释解释"为什么"，而非"怎么做"。
- 注释语言：简体中文（便于团队沟通），但术语及对外文档可用英文。

```typescript
// ❌ 普通注释
// 创建知识库
export const createKnowledgeBase = (data: KnowledgeBaseCreate) => {
  return apiClient.post<KnowledgeBaseResponse>('/api/v1/knowledge-bases', data);
};

// ✅ JSDoc
/**
 * 创建新的知识库
 * @param data - 知识库名称与描述
 * @returns 创建成功的知识库对象
 */
export const createKnowledgeBase = (data: KnowledgeBaseCreate) => {
  return apiClient.post<KnowledgeBaseResponse>('/api/v1/knowledge-bases', data);
};
```

#### 后端（Python，Docstring）
- 公共函数/类必须有 docstring（模块级 `"""..."""`）。
- 复杂业务逻辑必须内联注释解释"为什么"，而非"怎么做"。
- 注释语言：简体中文（便于团队沟通），但术语及对外文档可用英文。

```python
# ❌ 无 docstring
def create_kb(data: KnowledgeBaseCreate, service: KnowledgeService = Depends()):
    return service.create(data)

# ✅ 有 docstring
def create_kb(data: KnowledgeBaseCreate, service: KnowledgeService = Depends()) -> KnowledgeBaseResponse:
    """
    创建新的知识库。

    Args:
        data: 知识库名称与描述信息。
        service: 知识库业务服务（由 FastAPI 依赖注入）。

    Returns:
        创建成功的知识库对象。

    Raises:
        HTTPException: 知识库名称重复时返回 409。
    """
    return service.create(data)
```

### 3.5 错误处理

#### 前端（TypeScript）
- 禁止吞异常（`catch (e) { return null; }` 不允许）。
- 业务异常使用自定义 `DomainError` 类，扩展 `Error`。
- 所有异步操作必须有 `try/catch` 或 `.catch()` 处理。

```typescript
// ❌ 吞异常
export const fetchKB = async (kbId: string) => {
  try {
    return await apiClient.get(`/api/v1/knowledge-bases/${kbId}`);
  } catch (e) {
    return null;  // 错误被静默吞掉，调用方无法感知
  }
};

// ✅ 正确处理
export class DomainError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'DomainError';
  }
}

export const fetchKB = async (kbId: string) => {
  try {
    return await apiClient.get(`/api/v1/knowledge-bases/${kbId}`);
  } catch (e) {
    if (e instanceof DomainError) {
      throw e;  // 业务异常原样抛出
    }
    throw new DomainError('获取知识库失败', 'FETCH_KB_FAILED');
  }
};
```

#### 后端（Python）
- 禁止吞异常（`except: pass` 不允许）。
- 业务异常使用自定义异常类，继承 `Exception`。
- 所有可能失败的操作必须有 `try/except`。
- 对外接口通过 `HTTPException` 转换为 HTTP 状态码。

```python
# ❌ 吞异常
def get_kb(kb_id: str) -> KnowledgeBase | None:
    try:
        return service.get_detail(kb_id)
    except Exception:
        pass  # 错误被静默吞掉

# ✅ 正确处理
class KnowledgeBaseNotFound(Exception):
    """知识库不存在异常"""
    pass

def get_kb(kb_id: str) -> KnowledgeBaseDetail:
    try:
        result = service.get_detail(kb_id)
        if not result:
            raise KnowledgeBaseNotFound(f"知识库 {kb_id} 不存在")
        return result
    except KnowledgeBaseNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.6 Git 提交规范
- 类型：`feat|fix|docs|style|refactor|test|chore`
- 格式：`<type>(<scope>): <subject>`（subject 不超过 72 字符，推荐中文）
- 示例：`feat(知识库): 创建知识库时增加名称重复校验`

### 3.7 数据库迁移

- 所有数据库 Schema 变更必须通过 **Alembic** 生成迁移脚本。
- 严禁手动修改数据库表结构后不生成迁移文件。
- 迁移脚本必须提交到 Git，与对应业务代码一起 Review。

```bash
# 首次初始化
alembic init -t async alembic

# 生成迁移脚本（对比 ORM 模型与当前数据库的差异）
alembic revision --autogenerate -m "创建知识库表"

# 执行迁移
alembic upgrade head

# 回滚上一版本
alembic downgrade -1
```

**完整工作流示例：**

假设需要给知识库增加一个 `is_public` 字段。

```python
# 第一步：修改 ORM 模型
# app/models/knowledge_base.py
class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    ...
    is_public: bool = Column(Boolean, default=False)  # ← 新增
```

```bash
# 第二步：生成迁移脚本
cd backend
alembic revision --autogenerate -m "知识库增加is_public字段"

# alembic 会自动生成类似如下的迁移文件：
# backend/alembic/versions/xxxx_add_is_public.py
```

```python
# 第三步：检查自动生成的迁移文件，确认无误
def upgrade():
    op.add_column("knowledge_bases", sa.Column("is_public", sa.Boolean(), nullable=False))

def downgrade():
    op.drop_column("knowledge_bases", "is_public")
```

```bash
# 第四步：执行迁移
alembic upgrade head

# 第五步：将 ORM 模型 + 迁移脚本一起提交
git add app/models/knowledge_base.py alembic/versions/xxxx_add_is_public.py
git commit -m "feat(知识库): 新增is_public字段"
```

> 核心原则：**改模型 → 生迁移 → 检查迁移 → 执行 → 一起提交**。每一步都不能跳过。

### 3.8 API 设计规范

| 规范 | 说明 | 示例 |
|------|------|------|
| **URL 前缀** | 统一使用 `/api/v1/` | `/api/v1/knowledge-bases` |
| **资源命名** | 复数名词 + kebab-case | `/knowledge-bases` 而非 `/knowledgeBase` |
| **分页参数** | `offset` + `limit`，默认 20 条 | `?offset=0&limit=20` |
| **成功响应** | `{ "data": ..., "message": "ok" }` | — |
| **错误响应** | `{ "detail": "错误描述" }` | — |
| **状态码** | 200（成功）/ 201（创建）/ 400（参数错误）/ 404（不存在）/ 409（冲突）/ 500（服务错误） | — |

```python
# ✅ 正确：统一起名、分页参数、标准响应格式
@router.get("/knowledge-bases/{kb_id}/documents")
def list_documents(
    kb_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return {"data": [...], "message": "ok"}

# ❌ 错误：单数命名、无分页、无统一格式
@router.get("/knowledge-base/{id}/document")
def get_docs(id: str):
    return documents
```

### 3.9 日志规范

- 后端统一使用 Python `logging` 模块，禁止使用 `print()` 代替日志。
- 日志级别：
  | 级别 | 使用场景 |
  |------|----------|
  | **DEBUG** | 开发调试，本地默认开启，生产关闭 |
  | **INFO** | 关键操作：文档上传、切块完成、LLM 调用、知识库创建/删除 |
  | **WARNING** | 非预期但可恢复的情况：重试成功、降级处理 |
  | **ERROR** | 异常失败：文档处理失败、LLM 调用超时、Milvus 连接失败 |
- 关键操作必须记录耗时（如 LLM 调用耗时、Milvus 查询耗时）。
- 日志格式统一包含：时间戳 + 模块名 + 日志级别 + 消息。

```python
import logging
import time

logger = logging.getLogger(__name__)


def search_chunks(kb_id: str, query_vector: list, top_k: int):
    start = time.time()
    try:
        result = milvus_client.search(kb_id, query_vector, top_k)
        elapsed = time.time() - start
        logger.info("Milvus 检索完成，kb=%s，top_k=%d，耗时=%.2fs", kb_id, top_k, elapsed)
        return result
    except Exception as e:
        logger.error("Milvus 检索失败，kb=%s，error=%s", kb_id, e)
        raise
```

## 4. 开发环境与工具链

### 4.1 环境变量
- 本地开发使用 `.env.local`，加入 `.gitignore` 禁止提交。Docker 部署通过 `env_file` 运行时注入，严禁将密钥打包进镜像。
- 所有环境变量必须校验：前端用 `zod`（`env.schema.ts`），后端用 Pydantic Settings（`app/core/config.py`）。

### 4.2 常用脚本

```bash
# 前端
pnpm dev          # 启动开发模式（热重载）
pnpm build        # 构建生产产物
pnpm lint         # 执行 ESLint 并自动修复
pnpm format       # 执行 Prettier

# 后端
ruff check .      # 代码规范检查
ruff check --fix . # 自动修复
ruff format .     # 代码格式化
mypy app/         # 类型检查
```

### 4.3 Git Hooks

项目根目录统一挂载 `husky` + `lint-staged`，同时覆盖前后端：

**`package.json`（根目录）：**

```json
{
  "lint-staged": {
    "frontend/src/**/*.{ts,tsx}": [
      "cd frontend && eslint src --ext .ts,.tsx --fix",
      "cd frontend && prettier --write",
      "cd frontend && tsc --noEmit"
    ],
    "backend/app/**/*.py": [
      "cd backend && ruff check --fix",
      "cd backend && ruff format",
      "cd backend && mypy app/"
    ]
  }
}
```

**`.husky/pre-commit`：**

```bash
npx lint-staged
```

**工作原理**：`git commit` 时，husky 拦截 → lint-staged 识别本次修改文件属于前端还是后端 → 只执行对应检查。全部通过才允许提交。

> **前端工具链**：ESLint + Prettier + tsc
> **后端工具链**：Ruff（lint + format + import 排序）+ mypy

## 5. 禁止事项（红线）
- ❌ 禁止直接 `require()`，必须使用 ES Module `import/export`。
- ❌ 禁止在 Service 层绕过 ORM 直接写原始 SQL，必须通过 SQLAlchemy Session 操作。
- ❌ 禁止修改 `node_modules` 或使用 `patch-package` 而不经团队评审。
- ❌ 禁止提交 `console.log`、`debugger` 语句到主分支。
- ❌ 禁止使用 `any` 类型（除非有 `eslint-disable-next-line @typescript-eslint/no-explicit-any` 并附带原因）。

## 6. 开发流程（API-First + 垂直切片 + Walking Skeleton）

本项目采用 **API-First** 驱动、**垂直切片** 递进、**Walking Skeleton** 验证的三合一开发流程。

### 6.1 为什么用这套流程？

传统横向切分（先做完后端再做前端）会导致前端长期空等，风险爆发在联调阶段。这套流程让前后端以"合同"为界、并行推进，把核心链路的不确定性尽早暴露。

### 6.2 四个阶段

```
阶段 0：API 契约设计
  │  Schema 即合同。后端写出所有接口的 Pydantic 模型，
  │  前端通过 openapi-typescript 同步类型，两端对齐后不再变动。
  │
  ├─── 阶段 A（后端基础设施）
  │     • 数据库建表 + Alembic 迁移
  │     • 认证鉴权骨架（Token 签发/校验，权限装饰器后续挂载）
  │     • 基础 CRUD（纯数据，先不集成外部服务）
  │       ┌─ 阶段 A 只做：
  │       │  创建知识库 → 只写入 SQLite，不管 Milvus
  │       │  上传文档   → 只记录文件名和状态到 SQLite，不做切块/向量化
  │       │  聊天       → 返回占位字符串，不调 LLM
  │       └─ 阶段 A2 再补：
  │          上传文档   → 加 Celery 异步切块 + Milvus 写入
  │          聊天       → 加向量检索 + LLM 生成
  │
  └─── 阶段 B（前端骨架，与 A 并行）
        • 搭建 Layout + 路由
        • 基于自动生成的类型，用假数据跑通所有页面跳转
        • 引入 ui-ux 相关 skill 产出设计草案
           │
           ├──────────────────────────────┐
           ▼                              ▼
 阶段 A2（核心业务链路）           阶段 B2（页面完善，与 A2 并行）
   • 集成外部服务（如 Milvus/LLM）        • 知识库管理页
   • 实现业务闭环（端到端能跑通）           • 核心功能页面
   • 日志记录关键耗时与异常                • 统计面板
           │                              │
           └──────────┬───────────────────┘
                      ▼
              阶段 3：联调 + 收尾
                • 前端切到真实 API，下线假数据
                • 权限校验完整生效
                • Docker Compose 一键启动
```

### 6.3 核心原则

| 原则 | 含义 | 执行方式 |
|------|------|----------|
| **API-First** | 代码一行都不写，先把 Schema 定死 | 后端写 Pydantic → 导出 OpenAPI → 前端生成类型 |
| **Contract-Driven** | Schema 即合同，两端以合同互不越界 | 变更 Schema 时两端同步修改，编译器兜底 |
| **Vertical Slice** | 按功能纵向切分，不做横向分层 | 每个功能两端一起打通，而非"后端全写完再给前端" |
| **Walking Skeleton** | 先搭建能从头跑到尾的最简骨架 | 核心链路跑通即为里程碑，之后再补肌肉 |
| **Incremental** | 每次交付的是可用的增量 | 每个阶段结束都能 Demo，不是最后一刻才见光 |
| **权限延后** | 认证框架先搭好，鉴权逻辑最后挂载 | Token 签发/校验先写，`@require_admin` 装饰器后期加 |

### 6.4 每个阶段的交付物

| 阶段 | 必须产出 | 验证方式 |
|------|----------|----------|
| 0 | 完整的 Schema 定义（所有接口的请求/响应） | 前端生成类型，`tsc --noEmit` 通过 |
| A + B | 后端基础 CRUD + 前端可点击的页面骨架 | 前端用假数据能完成所有页面跳转 |
| A2 + B2 | 核心业务链路打通 | 手动走完一个完整业务流程（如上传→处理→查询） |
| 3 | 全功能可用 + 一键启动 | `docker compose up` 后能体验完整产品 |

### 6.5 禁止的反模式

- ❌ **B**ig **D**esign **U**p **F**ront：试图一开始就设计出完美架构，写了一周还没跑通一个接口。
- ❌ 横向切分：后端全部做完再移交前端，前端空等、联调爆炸。
- ❌ 虚假的并行：Schema 没定就各自开工，联调时发现字段对不上。