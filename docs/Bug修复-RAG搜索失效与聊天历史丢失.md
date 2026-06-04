# Bug 修复记录：RAG 搜索失效 & 聊天历史丢失

> 修复日期：2026-06-04

## Bug 1：RAG 搜索始终返回"知识库中暂无相关文档"

### 现象

用户在对话中输入任何问题（如"介绍一下吴禹轩"），系统立刻返回"知识库中暂无相关文档，请先上传文档。"，即使知识库中已上传大量文档且处理状态为 `done`。

### 根因分析

**核心问题**：Milvus Lite 的 Collection Schema 使用了动态字段（`enable_dynamic_field=True`），导致 `search()` 的 `filter` 参数无法按 `kb_id` 过滤。

具体原因链：

1. `VectorStore._ensure_collection()` 使用 `MilvusClient.create_collection()` 的简化参数创建 Collection：
   ```python
   self.client.create_collection(
       collection_name=COLLECTION_NAME,
       dimension=self.dimension,
       metric_type="L2",
   )
   ```
   这种方式只声明了 `id`（INT64, PK）和 `vector`（FLOAT_VECTOR）两个正式字段。

2. 插入数据时，`kb_id`、`doc_id`、`filename`、`text` 作为额外字段随数据一起插入，Milvus 自动将它们作为**动态字段**存储（Collection schema 的 `enable_dynamic_field=True`）。

3. **Milvus Lite 的已知限制**：动态字段可以被 `query()` 读取，但**无法用于 `search()` 的 `filter` 条件**。因为动态字段没有被索引，无法参与过滤运算。

4. 因此 `search(filter='kb_id == "xxx"')` 永远匹配不到任何结果，`chunks` 始终为空列表，直接触发"知识库中暂无相关文档"的分支。

### 验证证据

```
# 不带 filter 的搜索 → 返回 5 条结果
search(data=[vec], limit=5) → 5 results ✓

# 带 kb_id filter 的搜索 → 返回 0 条结果
search(data=[vec], limit=5, filter='kb_id == "5109d463-..."') → 0 results ✗
```

### 修复方案

在 `VectorStore._ensure_collection()` 中使用显式 `CollectionSchema` 声明所有字段，设置 `enable_dynamic_field=False`：

```python
from pymilvus import CollectionSchema, DataType, FieldSchema

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
    FieldSchema(name="kb_id", dtype=DataType.VARCHAR, max_length=128),
    FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
    FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
]
schema = CollectionSchema(fields=fields, enable_dynamic_field=False)
```

**副作用**：由于 Schema 变更无法原地生效，需要删除旧 Collection 并重新处理所有 `status=done` 的文档。

### 涉及文件

| 文件 | 变更类型 |
|------|----------|
| `backend/app/services/vector_store.py` | 修复：使用显式 Schema 创建 Collection |

### 经验教训

1. **Milvus Lite 动态字段限制**：`search()` 的 `filter` 不支持动态字段，必须将过滤字段声明为正式 Schema 字段。
2. **MilvusClient 的简化 API 隐藏了 Schema 细节**：使用 `create_collection(collection_name, dimension)` 时，额外字段会被静默地当作动态字段处理，没有任何警告。
3. **搜索过滤的正确性验证**：在集成向量数据库时，应尽早验证 `filter` 参数的实际效果，而非仅检查数据是否写入。

---

## Bug 2：页面刷新后聊天记录丢失

### 现象

用户在对话页面刷新浏览器后，所有聊天记录消失，只剩欢迎消息。

### 根因分析

**核心问题**：前端 `ChatPage.tsx` 从未调用后端的 `GET /api/v1/knowledge-bases/{kb_id}/chat-history` API 加载历史记录。

具体原因：

1. 后端已完整实现聊天历史功能：
   - `ChatHistoryService.save_chat()` 保存每轮对话到 SQLite
   - `ChatHistoryService.list_by_kb()` 支持分页查询
   - `GET /knowledge-bases/{kb_id}/chat-history` API 端点已注册

2. 但前端 `ChatPage.tsx` 的消息状态仅使用组件级 `useState`：
   ```typescript
   const [messages, setMessages] = useState<Message[]>([
     createMessage('assistant', '你好！我是白泽知识库助手，请向我提问。'),
   ]);
   ```
   每次进入页面都初始化为硬编码的欢迎消息，没有任何历史加载逻辑。

3. `frontend/src/api/knowledge.ts` 中也**没有定义**获取聊天历史的 API 函数。

### 附带问题：LLM 未使用历史上下文

后端 `ChatService.chat()` 直接调用 `llm_service.generate(question, context)`，没有传入之前的对话记录。用户无法进行多轮对话（如"他""她"等代词无法指代前文）。

### 修复方案

**前端**：
1. 在 `api/knowledge.ts` 中新增 `ChatHistoryItem` 类型和 `getChatHistory()` 函数
2. 在 `ChatPage.tsx` 中通过 `useEffect` 在组件挂载时加载历史记录

**后端**：
1. `ChatService.chat()` 新增 `_load_recent_history()` 方法，加载最近 10 轮对话
2. `LLMService.generate()` 新增 `history` 参数，将历史对话注入 LLM 的 messages 列表

### 涉及文件

| 文件 | 变更类型 |
|------|----------|
| `frontend/src/api/knowledge.ts` | 新增：`getChatHistory()` API 函数和 `ChatHistoryItem` 类型 |
| `frontend/src/pages/ChatPage.tsx` | 修复：组件挂载时加载聊天历史 |
| `backend/app/services/chat_service.py` | 新增：加载历史上下文传给 LLM |
| `backend/app/services/llm_service.py` | 修复：支持多轮对话历史注入 |

### 经验教训

1. **前后端功能不对齐**：后端实现了完整的聊天历史 API，但前端未对接。应在开发流程中增加"前端是否完整消费了后端 API"的检查。
2. **RAG 系统的多轮对话支持**：聊天记录不仅是展示用途，还应作为 LLM 上下文输入，保证多轮对话的连贯性。
