# 阶段 0 沉淀文档 — API 契约设计

## 完成时间

2026-06-01

## 目标回顾

定死所有接口的请求/响应结构，使前后端以合同为界、可并行推进。

## 产出清单

| 文件 | 内容 |
|------|------|
| `backend/app/schemas/user.py` | `UserCreate`, `UserLogin`, `UserResponse`, `TokenResponse`, `UserRoleUpdate` |
| `backend/app/schemas/knowledge_base.py` | `KnowledgeBaseCreate`, `KnowledgeBaseResponse`, `KnowledgeBaseDetail` |
| `backend/app/schemas/document.py` | `DocumentUploadResponse`, `DocumentResponse` |
| `backend/app/schemas/chat.py` | `ChatRequest`, `ChatResponse` |
| `backend/app/schemas/stats.py` | `StatsResponse` |
| `backend/app/core/config.py` | Pydantic Settings 配置类，含初始管理员凭证 |
| `backend/app/core/seed.py` | 首个管理员自动创建脚本 |
| `backend/app/main.py` | FastAPI 应用骨架 |
| `backend/requirements.txt` | 后端依赖清单 |
| `backend/.env.example` | 环境变量模板 |
| `docs/身份机制设计.md` | 角色创建与提升流程文档 |

## 关键决策

1. **角色硬编码安全**：`UserCreate` 不暴露 `role` 字段，注册默认 `user`，防止前端伪造
2. **种子脚本**：系统启动时从环境变量创建首个管理员
3. **Token 携带角色**：JWT Payload 含 `role`，中间件注入无需查库
4. **目录结构**：与 `Agent.md` §3.2 完全对齐

## 未完成项

- 前端项目尚未初始化，类型自动生成须在阶段 B 中完成
- 后端尚未安装依赖、未启动服务

## Git 提交记录

- `feat(后端): 阶段0完成-API契约设计，定义全部Schema`
- `docs(用户): 补充身份机制设计-角色创建与提升流程`
- `docs(开发计划): 补充身份机制与用户管理接口`
