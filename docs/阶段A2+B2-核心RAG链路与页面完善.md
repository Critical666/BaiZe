# 阶段 A2+B2 沉淀文档 — 核心 RAG 链路与页面完善

## 完成时间

2026-06-01

## 目标回顾

A2：实现文档解析→切块→向量化→检索→问答的完整 RAG 链路。
B2：前端页面完善，同步与后端对接。

---

## A2 后端产出

| 模块 | 文件 | 说明 |
|------|------|------|
| 文档解析 | `utils/parser.py` | 支持 PDF、Word、Markdown、TXT |
| 文本切块 | `utils/chunker.py` | 500 字符 + 50 重叠滑动窗口 |
| 向量存储 | `services/vector_store.py` | FAISS 开发模式，接口可切换 Milvus |
| RAG 聊天 | `services/chat_service.py` | 哈希向量 + FAISS 检索 + 模板回答 |
| Celery 任务 | `core/celery_app.py` | 异步文档处理（框架就绪，待 Redis） |
| 日志配置 | `main.py` | 全局 logging，时间戳 + 级别 + 模块 |

### RAG 处理流水线

```
上传文档 → _process_inline()
├─ parser.parse_document()  → PDF/Word/Markdown → 纯文本
├─ chunker.chunk_text()     → 500字+50重叠 → 文本块列表
├─ ChatService._encode()    → SHA256哈希→384维向量
├─ vector_store.insert()    → FAISS IndexFlatL2
└─ 更新 Document.status=done, chunk_count=N
```

### RAG 对话流程

```
提问 → ChatService.chat()
├─ _encode(question)    → 问题向量
├─ vector_store.search()  → FAISS Top-K 检索
├─ 构建 Prompt              → 拼接检索文本块 + 来源
├─ _generate_answer()      → 关键词提取 + 模板
└─ 返回 { answer, sources }
```

### 开发模式降级策略

| 外部服务 | 不可用时的降级 |
|----------|--------------|
| Celery/Redis | 内联同步处理（_process_inline） |
| Embedding 模型 | SHA256 哈希向量 |
| FAISS | 关键词匹配 |
| LLM API | 关键词提取 + 模板回答 |

---

## B2 前端

前端页面在阶段 A+B 已完成 —— 登录、创建知识库、文档上传、聊天、统计均已对接真实 API。
部分修正：文档端点改为 `async` 以正确读取文件内容。

---

## 技术验证

```
✅ 上传 test_doc.txt → 解析 → 切块=1 → FAISS 存储 → status=done
✅ 提问"如何重置密码？" → 检索成功 → 返回原文摘要 → 来源 test_doc.txt
✅ tsc --noEmit 通过
```

---

## 阶段交付物对照

> "创建知识库 → 上传文档 → 等待处理完成 → 聊天提问 → 得到带来源引用的回答"

✅ 全流程跑通。

## Git 提交记录

- `feat(全栈): 阶段A+B完成-后端基础CRUD与前端页面骨架`
- `chore: 添加.gitignore，清理误提交的缓存文件`
- `chore: 继续清理__pycache__缓存`
- `docs(前端): TypeScript路径别名配置问题与修复`
