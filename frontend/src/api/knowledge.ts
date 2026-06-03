import type { KnowledgeBaseItem, KnowledgeBaseDetail, DocumentItem, StatsOverview } from '@/types/api';
import apiClient from './client';

export type { KnowledgeBaseItem, KnowledgeBaseDetail, DocumentItem, StatsOverview };

export const listKnowledgeBases = () => {
  return apiClient.get<unknown, KnowledgeBaseItem[]>('/api/v1/knowledge-bases');
};

export const getKnowledgeBaseDetail = (kbId: string) => {
  return apiClient.get<unknown, KnowledgeBaseDetail>(`/api/v1/knowledge-bases/${kbId}`);
};

export const createKnowledgeBase = (data: { name: string; description?: string }) => {
  return apiClient.post<unknown, KnowledgeBaseItem>('/api/v1/knowledge-bases', data);
};

export const deleteKnowledgeBase = (kbId: string) => {
  return apiClient.delete(`/api/v1/knowledge-bases/${kbId}`);
};

export const listDocuments = (kbId: string) => {
  return apiClient.get<unknown, DocumentItem[]>(`/api/v1/knowledge-bases/${kbId}/documents`);
};

export const uploadDocument = (kbId: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post(`/api/v1/knowledge-bases/${kbId}/documents`, formData);
};

export const chatWithKB = (kbId: string, question: string) => {
  return apiClient.post<unknown, { answer: string; sources: string[] }>(
    `/api/v1/knowledge-bases/${kbId}/chat`,
    { question },
  );
};

export const getStats = () => {
  return apiClient.get<unknown, StatsOverview>('/api/v1/stats');
};
