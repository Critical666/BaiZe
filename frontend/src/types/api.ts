/** 前端 API 类型定义（阶段 A+B 手写，后续由 openapi-typescript 自动生成覆盖）。 */

export interface KnowledgeBaseItem {
  id: string;
  name: string;
  description?: string;
  document_count?: number;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBaseDetail extends KnowledgeBaseItem {
  document_count: number;
}

export interface DocumentItem {
  id: string;
  kb_id: string;
  filename: string;
  file_size: number;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface StatsOverview {
  knowledge_base_count: number;
  document_count: number;
  chunk_count: number;
  chat_count_7d: number;
}
