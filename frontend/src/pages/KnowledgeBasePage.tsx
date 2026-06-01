import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Upload, Table, Tag, Space, message, Spin } from 'antd';
import { ArrowLeftOutlined, MessageOutlined } from '@ant-design/icons';
import { getKnowledgeBaseDetail, listDocuments, uploadDocument } from '@/api/knowledge';
import type { KnowledgeBaseDetail, DocumentItem } from '@/types/api';

const statusColor: Record<string, string> = {
  pending: 'default',
  processing: 'processing',
  done: 'green',
  failed: 'red',
};

const statusText: Record<string, string> = {
  pending: '待处理',
  processing: '处理中',
  done: '已完成',
  failed: '失败',
};

export default function KnowledgeBasePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [kb, setKb] = useState<KnowledgeBaseDetail | null>(null);
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    if (!id) return;
    try {
      const [kbData, docData] = await Promise.all([
        getKnowledgeBaseDetail(id),
        listDocuments(id),
      ]);
      setKb(kbData);
      setDocs(docData);
    } catch {
      // 后端未启动
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleUpload = async (file: File) => {
    if (!id) return;
    try {
      await uploadDocument(id, file);
      message.success('上传成功');
      fetchData();
    } catch {
      message.error('上传失败');
    }
    return false; // 阻止默认上传行为
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '120px auto' }} />;
  if (!kb) return <div>知识库不存在</div>;

  return (
    <div>
      <Space style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')}>
          返回
        </Button>
        <h2 style={{ margin: 0 }}>{kb.name}</h2>
        <Button
          type="primary"
          icon={<MessageOutlined />}
          onClick={() => navigate(`/kb/${id}/chat`)}
        >
          开始对话
        </Button>
      </Space>

      {kb.description && (
        <p style={{ color: '#666', marginBottom: 24 }}>{kb.description}</p>
      )}

      <Card title="文档管理" style={{ marginBottom: 24 }}>
        <Upload
          customRequest={({ file }) => handleUpload(file as File)}
          showUploadList={false}
          accept=".pdf,.docx,.md,.txt"
        >
          <Button type="primary">上传文档</Button>
        </Upload>
      </Card>

      <Table
        dataSource={docs}
        rowKey="id"
        pagination={false}
        columns={[
          { title: '文件名', dataIndex: 'filename', key: 'filename' },
          {
            title: '大小',
            dataIndex: 'file_size',
            key: 'file_size',
            render: (size: number) => `${(size / 1024).toFixed(1)} KB`,
          },
          { title: '切块数', dataIndex: 'chunk_count', key: 'chunk_count' },
          {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
            render: (s: string) => <Tag color={statusColor[s]}>{statusText[s]}</Tag>,
          },
          { title: '上传时间', dataIndex: 'created_at', key: 'created_at' },
        ]}
      />
    </div>
  );
}
