# Harness 工程：自然语言编程的重要指导

> 以一个 99% 代码由 AI 生成的 RAG 知识库项目为实践案例，探讨如何通过"围栏"而非"释放"来驾驭大模型。

> **想要本地部署白泽？** 👉 [点击跳转到部署指南](#部署指南)

---

## 写在前面

最近我完成了一个项目——**白泽**，一个基于 RAG 的 SaaS 知识库平台。用户创建知识库后上传文档，系统自动切块、向量化、存入 Milvus，即可通过自然语言对话从文档中检索答案，回答附带来源引用。

这个项目有意思的地方不在于产品本身，而在于它的**生产方式**：整个项目约 3800 行业务代码（Python 后端 2310 行，React/TypeScript 前端 1530 行），99% 由 AI 生成。我作为"人类开发者"，几乎没有手写一行业务代码。

这不是对 AI Coding 的盲目推崇。恰恰相反，这个项目的核心方法论—— **Harness 工程**——正是为了解决"让 AI 写代码"这件事中那些不可控的部分。

---

## 一、AI Coding 的困境：没有 Harness 的大模型像什么？

在接触 AI Coding 两年多的时间里，我观察到四个反复出现的核心问题：

### 1.1 上下文盲区

大模型无法读取整个项目的上下文架构。当项目超过一定规模，模型每次只能看到对话窗口中的那几段代码，它不知道 `utils/chunker.py` 里的切块逻辑和 `services/vector_store.py` 里的 Milvus 写入是如何配合的，也不知道前端的 `api/knowledge.ts` 和后端的 `schemas/knowledge_base.py` 是否对齐。

结果是：模型生成的代码往往是"局部正确"但"全局矛盾"的。

### 1.2 黑盒风险

大模型的自主任务编排会导致项目变成完全的黑盒。模型自己决定用什么技术栈、怎么组织目录、什么设计模式，你作为开发者不清楚实现细节。可能今天把 Embedding 塞在 ChatService 里，明天又做成独立模块。

看似功能都实现了，但代码质量完全不可控，出了 Bug 你连排查方向都找不到。

### 1.3 反馈缺失

大模型没有一个反馈机制，它自己其实不知道自己做出来的是个什么东西。它生成了代码，但你无法确定这段代码能不能跑、有没有隐藏的类型错误、API 接口是否前后端对齐。

它不会自己去检查类型，不会自己去 `curl` 验证接口，更不会知道 Milvus 的动态字段不支持 `search()` 的 `filter` 条件（这是我开发示例项目中，遇到的实际问题，并且通过自主反馈由AI解决了）。

### 1.4 技术栈发散

大模型没有一个架构护栏，使用技术栈很杂乱。同一个项目里，数据库操作可能混用 ORM 和原生 SQL，前端状态管理可能 React Query 和 Redux 交替出现。

没有约束的"自由"，最终只会变成混乱。

---

## 二、Harness 的核心思想：框定，而非释放

**Harness**，中文意为"马具"或"挽具"。给马套上挽具，不是为了限制马的速度，而是为了让马按照你期望的方向跑。

面对大模型能力持续增强的现实，正确的策略不是继续"微调"模型让它更聪明，而是**框定它的能力范围**——告诉它用什么技术、遵循什么规范、在什么架构内工作。模型本身已经足够聪明，缺的不是能力，而是方向。

这也是 Harness 工程可行的重要原因：**大模型能力的增强，使得我们更应该框定其能力范围，而非继续微调以加强它**。

一个足够聪明的模型 + 一个足够清晰的架构约束，远比一个更强的模型在无约束状态下自由发挥要可靠得多。

---

## 三、Harness 工程的实践方法

理论讲完了，接下来用白泽项目的完整开发过程来说明我是如何将 Harness 从理论转变为实践的。

### 3.1 第一步：写好 Agent.md——在写代码之前写好"宪法"

这是整个 Harness 工程中最关键的一步。

在写第一行业务代码之前，我花时间写了一份详细的 `Agent.md` 文件（约770行）。这不是需求文档，也不是技术方案——它是**给 AI 的一份"宪法"**，定义了 AI 在这个项目中必须遵守的一切规则。

`Agent.md` 包含以下内容：

**技术栈强制约束：**

```
前端：React 19 + TypeScript
后端：FastAPI（Python 3.12+）
向量数据库：Milvus
关系数据库：SQLite
容器化：Docker + Docker Compose
```

这不是建议，是**强制约束**。AI 没有选择其他技术栈的权力。

**代码规范——精确到命名风格：**

```
文件/文件夹：kebab-case（如 order-service.ts）
类/接口/类型：PascalCase（如 OrderEntity）
变量/函数/方法：camelCase（如 getUserById）
常量：UPPER_SNAKE_CASE（如 MAX_RETRY_COUNT）
数据库表/字段：snake_case（如 order_items, created_at）
```

甚至规定了注释语言：简体中文，但术语可用英文。

**目录结构——精确到每个文件夹的职责：**

```
backend/
├── app/
│   ├── api/        # HTTP入口层。绝不包含业务逻辑。
│   ├── schemas/    # 数据形状定义。前后端契约的唯一来源。
│   ├── models/     # 数据库映射。
│   ├── services/   # 核心业务逻辑。开发的重点区域。
│   ├── core/       # 基础设施。
│   └── utils/      # 通用工具函数。
```

每个目录都有明确的核心职责和关键点说明，并配以代码示例。

**开发流程约束：**

```
阶段 0：API 契约设计（代码一行都不写，先把 Schema 定死）
  → 阶段 A：后端基础设施（与 B 并行）
  → 阶段 B：前端骨架（与 A 并行）
  → 阶段 A2：核心 RAG 链路（与 B2 并行）
  → 阶段 B2：页面完善（与 A2 并行）
  → 阶段 3：联调收尾
```

这份文档总共约 770 行。它的作用相当于给 AI 戴上了一个精确的"马具"——AI 知道自己在用什么技术、该把代码放在哪里、该用什么命名风格、该遵循什么开发流程。

**实际效果**：在整个开发过程中，AI 从未偏离过预设的技术栈，从未在错误的目录创建文件，代码风格保持了高度一致。

### 3.2 第二步：先出方案，人工确认，框定架构

在 `Agent.md` 的基础上，我又写了一份 `DEVELOPMENT_PLAN.md`——详细的开发计划。这份计划包含：

- **整体架构图**：从用户浏览器到 Nginx 到 FastAPI 到 SQLite/Milvus 的完整数据流
- **核心数据模型**：User、KnowledgeBase、Document 三张表的精确字段定义
- **API 路由设计**：14 个接口的方法、路径、权限要求
- **核心业务流程**：文档处理流水线、RAG 对话流程的伪代码
- **分阶段开发计划**：每个阶段的目标、产出物、验证方式
- **风险点**：Milvus 版本兼容、LLM 调用延迟等已知风险

这份计划是 AI 生成后由我**人工审阅和确认**的。

这一步解决的是"黑盒风险"问题。通过在编码前框定架构，即使 99% 的代码由 AI 生成，我也清楚地知道整个系统的设计意图和实现路径。

**实际执行**：开发严格按照阶段推进。AI 在每个阶段开始前都会回顾计划，确认当前阶段的目标和约束，然后才开始编码。从未出现"跳过阶段"或"擅自修改架构"的情况。

### 3.3 第三步：为大模型配置好工具

我使用了腾讯的 CodeBuddy 作为 AI Coding 的 IDE 工具。这个工具给 AI 提供了完整的项目交互能力：

- **文件搜索与读取**：AI 可以搜索项目中的任意文件，读取完整内容
- **代码编辑**：AI 可以直接修改文件，创建新文件
- **命令执行**：AI 可以运行 `tsc --noEmit`、`curl`、`npm run build` 等命令验证自己的工作
- **Linter 集成**：AI 可以看到实时的类型错误和代码规范问题

这解决的是"反馈缺失"问题。AI 不再是"盲写"代码，它能通过工具验证自己生成的代码是否正确。

**一个典型的验证循环**：

```
AI 生成代码 → 运行 tsc --noEmit → 发现类型错误 → 修复 → 重新检查 → 通过
AI 生成 API → 运行 curl 验证 → 发现 500 错误 → 检查日志 → 修复 → 重新验证 → 200 OK
```

**实际案例**：在开发阶段 A+B 时，AI 完成了后端 14 条路由和前端 5 个页面的全部代码后，自动运行了三道验证：
- `tsc --noEmit`（前端类型检查）
- `vite build`（前端构建）
- 后端启动检查

全部通过后才报告阶段完成。

### 3.4 第四步：让 AI 自己跑测试——让 AI 了解自己写出的是什么东西

这可能是整个 Harness 工程中最容易被忽略、但实际上最关键的一环。

在白泽项目中，"测试"不只有自动化测试（虽然项目也预留了测试目录），更重要的是**每个阶段完成后的验证环节**。这些验证是由 AI 自己执行、自己评估的。

**阶段 A+B 的验证**：

```
✅ 后端启动成功，14 条路由就绪
✅ tsc --noEmit 通过
✅ vite build 构建成功
```

AI 验证的是：后端能跑起来吗？前端能编译吗？两者对得上吗？

**阶段 A2+B2 的验证**：

```
✅ 上传 test_doc.txt → 解析 → 切块=1 → Milvus Lite 存储 → status=done
✅ 提问"白泽是什么平台？" → 检索成功 → 返回原文摘要 + 来源引用 test_doc.txt
✅ Milvus Lite 持久化验证：重启后数据可检索
```

AI 验证的是：我写出的代码真的能完成"上传文档→处理→对话"这条核心链路吗？

**阶段 3 的验证**：

```
✅ EmbeddingService: sentence-transformers 模型加载 → encode_texts() 返回 (N, 384) float32
✅ LLMService: OpenAI API Key 配置后 → generate() 返回智能回答
✅ LLMService: API Key 为空时 → 自动回退关键词模板
✅ ChatHistory: 聊天记录写入 SQLite → chat_count_7d 实时查询
✅ Docker Compose 配置语法正确（docker compose config 验证）
```

AI 验证的是：每一个外部服务的接入是否正确？降级策略是否生效？

**这些验证不仅是"检查"，更是 AI 理解自身产出的过程。** 当 AI 运行 `curl` 向自己写的 API 发请求并看到返回结果时，它才真正"理解"了自己构建了什么。

### 3.5 第五步：每个阶段沉淀文档——由 AI 生成，由 AI 阅读

这是 Harness 工程的"记忆系统"。

每完成一个开发阶段，AI 会生成一份沉淀文档，记录该阶段的：

- 目标回顾
- 具体产出（精确到每个文件）
- 技术验证结果
- 关键设计决策及原因
- 已知问题和经验教训

白泽项目中，AI 生成了 8 份这样的文档：

```
docs/
├── 阶段0-API契约设计.md
├── 阶段A+B-后端基础设施与前端骨架.md
├── 阶段A2+B2-核心RAG链路与页面完善.md
├── 阶段3-联调收尾.md
├── Bug修复-RAG搜索失效与聊天历史丢失.md
├── 权限系统实现文档.md
├── 身份机制设计.md
└── 部署上线.md
```

**这些文档不是写给人类看的（虽然人类也可以看），它们首先是写给 AI 自己看的。**

当一个 Bug 出现时——比如 Milvus 搜索始终返回"暂无相关文档"——AI 会先去读之前阶段的沉淀文档，理解系统的设计意图，然后基于完整的上下文进行排查，而不是对着当前的几段代码"盲猜"。

**实际案例**：在修复 Milvus 搜索失效的 Bug 时，AI 首先读取了 `阶段A2+B2-核心RAG链路与页面完善.md`，理解了向量存储的实现方式，然后通过实验验证定位到根因：Milvus Lite 的动态字段不支持 `search()` 的 `filter` 条件。整个排查过程只用了几轮对话，因为 AI 通过文档已经掌握了完整的项目上下文。

---

## 四、实践成果

### 项目概况

| 指标 | 数据 |
|------|------|
| 开发周期 | 约 3 天（2026-06-01 至 2026-06-04） |
| 业务代码 | ~3800 行（Python 2310 行 + React/TS 1530 行） |
| 文档沉淀 | ~2600 行 Markdown |
| 人工编写代码量 | <1%（主要是 `.env` 配置） |
| 最终状态 | 已部署上线（wuyuxuan.xyz） |

### AI 自主解决的技术问题

在开发过程中，AI 自主发现并解决了多个非平凡的技术问题：

**1. FAISS → Milvus Lite 迁移**

阶段 A2 中 AI 最初使用了 FAISS 作为向量库，但在沉淀文档回顾时发现这与 `Agent.md` 和 `DEVELOPMENT_PLAN.md` 中约定的 Milvus 技术栈不符，主动迁移为 Milvus Lite。

**2. 哈希向量 float32 溢出**

AI 在实现 SHA256 哈希向量时遇到了 `np.linalg.norm` 计算溢出的问题（归一化后向量为全零或 NaN），自主定位根因并将哈希字节解释方式从 `float32` 改为 `uint32` 再映射到 `[-1, 1]` 范围。

**3. EmbeddingService 模块抽取**

在阶段 3 中，AI 发现阶段 A2 将 `_encode()` 作为 `ChatService` 的私有方法，导致 `DocumentService` 处理文档时需要 `from chat_service import ChatService; cs._encode()` 来调用 Embedding——违反了封装原则。AI 主动将其抽取为独立的 `embedding_service.py`。

**4. Milvus 动态字段 Bug**

当 RAG 搜索始终返回空结果时，AI 通过实验对比（带 filter 和不带 filter 的搜索结果），定位到 Milvus Lite 的动态字段不支持 `search()` 的 `filter` 条件，随后使用显式 `CollectionSchema` 重建 Collection。

### 架构一致性

从项目开始到部署上线，技术栈始终保持一致：

- 前端：React 19 + TypeScript + Ant Design + React Query（与 `Agent.md` 约定完全一致）
- 后端：FastAPI + SQLAlchemy + Celery（与 `Agent.md` 约定完全一致）
- 数据库：SQLite + Milvus Lite（与 `Agent.md` 约定完全一致）
- 从未引入 `Agent.md` 之外的任何第三方库

---

## 五、方法的局限性

坦率地说，Harness 工程并非银弹，它有明确的适用边界：

**适合的场景**：中等复杂度的 Web 应用、CRUD 为主的业务系统、技术栈明确的工程项目。白泽项目恰好符合这些条件——前后端分离、技术栈成熟、业务逻辑可拆分为独立的处理流水线。

**不适合的场景**：高度创新的算法研究（你不知道该框定什么方向）、超大型遗留系统改造（上下文已经庞大到文档无法覆盖）、需要深度领域知识的特殊场景（AI 缺乏必要的行业背景）。

另一个现实问题是：**写好 `Agent.md` 和 `DEVELOPMENT_PLAN.md` 本身就需要一定的架构能力**。如果你不知道该用什么技术栈、该怎么组织目录，AI 也帮不了你。Harness 的前提是你有足够的判断力来"框定方向"。

---

## 六、总结

Harness 工程的本质可以用一句话概括：

> **与其试图让 AI 更聪明，不如先让自己更清晰。**

具体来说，就是五步：

1. **写好 Agent.md**：在编码前定义好技术栈、代码规范、目录结构、开发流程——这是给 AI 的"宪法"
2. **先出方案，人工确认**：框定架构，消除黑盒——这是人类的职责
3. **配置好工具**：给 AI 验证自己产出的能力——这是 IDE 的职责
4. **让 AI 自己跑测试**：让 AI 通过验证理解自己构建了什么——这是反馈闭环
5. **每阶段沉淀文档**：由 AI 生成，由 AI 阅读——这是记忆系统

当这五步形成一个完整的循环时，AI Coding 就从"赌运气"变成了一个可预期、可复现的工程化流程。

白泽项目证明了这一点：3800 行代码、3 天开发周期、从零到部署上线——而人类开发者只做了"写规范、审方案、确认结果"这三件事。

---

> 本项目源码：[github.com/Critical666/BaiZe](https://github.com/Critical666/BaiZe)

---

## 部署指南

### 前置条件

| 条件 | 说明 |
|------|------|
| 服务器 | Linux 服务器，IP 可访问 |
| Python | 3.12+ |
| Node.js | 18+ |
| Nginx | 用于反向代理和静态资源托管（可选，也可直接访问） |
| LLM API Key | OpenAI 或兼容的 API Key（用于 AI 问答） |

### 快速开始

**1. 克隆代码**

```bash
git clone https://github.com/Critical666/BaiZe.git
cd BaiZe
```

**2. 配置后端**

```bash
cd backend
cp .env.example .env
```

编辑 `.env`，至少需要配置以下内容：

```bash
# 必填：LLM API Key（用于 AI 问答）
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1   # 可替换为兼容的 API 地址

# 必填：JWT 密钥（随机生成一个长字符串）
SECRET_KEY=your-random-secret-key

# 可选：管理员初始账户（仅首次启动时生效）
INIT_ADMIN_EMAIL=admin@example.com
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_PASSWORD=your-password

# CORS（生产环境填你的域名）
CORS_ORIGINS=https://your-domain.com
```

**3. 启动后端**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

后端启动后，访问 `http://localhost:8000/docs` 可查看 API 文档。

> 系统首次启动时会自动创建管理员账户（使用 `INIT_ADMIN_*` 配置）。

**4. 构建并启动前端**

```bash
cd frontend
npm install
npm run build
npm run preview   # 默认端口 4173
```

前端默认访问 `http://localhost:4173`。

> 如果只想在本地开发调试，可用 `npm run dev`（端口 5173），并设置 `VITE_API_BASE_URL=http://localhost:8000`。

### 生产部署（Nginx 反向代理）

将前端构建产物由 Nginx 托管，API 请求通过反向代理转发到后端：

```bash
# 构建前端
cd frontend && npm run build

# 复制到 Nginx 目录
cp -r dist/* /var/www/rag-frontend/
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/rag-frontend;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

```bash
nginx -t && systemctl reload nginx
```

### Docker Compose 部署（备选）

```bash
cp backend/.env.example backend/.env
# 编辑 .env 填入配置

docker compose up --build -d
```

> 首次构建需下载 PyTorch（CPU 版 ~532MB），耗时较长。

### 环境变量说明

| 变量 | 必填 | 说明 |
|------|------|------|
| `SECRET_KEY` | 是 | JWT 签名密钥，随机长字符串 |
| `OPENAI_API_KEY` | 是 | LLM API Key，问答功能必需 |
| `OPENAI_BASE_URL` | 否 | API 地址，默认 OpenAI |
| `CORS_ORIGINS` | 否 | 允许的前端域名，多个用逗号分隔 |
| `INIT_ADMIN_EMAIL` | 否 | 首次启动时创建的管理员邮箱 |
| `INIT_ADMIN_USERNAME` | 否 | 首次启动时创建的管理员用户名 |
| `INIT_ADMIN_PASSWORD` | 否 | 首次启动时创建的管理员密码 |
