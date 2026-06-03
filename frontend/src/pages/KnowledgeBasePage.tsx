import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Upload, Table, Tag, Space, message, Spin, Empty } from 'antd';
import { ArrowLeftOutlined, MessageOutlined, InboxOutlined } from '@ant-design/icons';
import { getKnowledgeBaseDetail, listDocuments, uploadDocument } from '@/api/knowledge';
import type { KnowledgeBaseDetail, DocumentItem } from '@/types/api';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;

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
  const [uploading, setUploading] = useState(false);
  const [polling, setPolling] = useState(false);

  const fetchData = useCallback(async () => {
    if (!id) return;
    try {
      const [kbData, docData] = await Promise.all([
        getKnowledgeBaseDetail(id),
        listDocuments(id),
      ]);
      setKb(kbData);
      setDocs(docData);
    } catch {
      message.error('获取知识库信息失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 上传后轮询文档状态
  useEffect(() => {
    if (!polling) return;
    const timer = setInterval(async () => {
      if (!id) return;
      try {
        const docData = await listDocuments(id);
        setDocs(docData);
        const hasPending = docData.some((d) => d.status === 'pending' || d.status === 'processing');
        if (!hasPending) {
          setPolling(false);
        }
      } catch {
        setPolling(false);
      }
    }, 3000);
    return () => clearInterval(timer);
  }, [polling, id]);

  const handleUpload = async (file: File) => {
    if (!id) return;
    setUploading(true);
    try {
      await uploadDocument(id, file);
      message.success('上传成功，文档正在处理中...');
      setPolling(true);
    } catch {
      message.error('上传失败，请重试');
      setUploading(false);
      return;
    }
    setUploading(false);

    // 上传成功后立即刷新列表（独立 try/catch，不覆盖上传提示）
    try {
      const docData = await listDocuments(id);
      setDocs(docData);
    } catch {
      // 列表刷新失败由轮询兜底，不弹错误提示
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.docx,.md,.txt',
    beforeUpload: (file) => {
      // 在 beforeUpload 中直接处理上传，file 是原生 File 对象
      handleUpload(file);
      // 返回 false 阻止默认上传行为
      return false;
    },
    showUploadList: false,
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
        <Dragger {...uploadProps} style={{ padding: '16px 0' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ color: '#1677ff', fontSize: 40 }} />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint" style={{ color: '#999' }}>
            支持 PDF、Word(.docx)、Markdown、TXT 格式
          </p>
        </Dragger>
        {uploading && (
          <div style={{ marginTop: 12, textAlign: 'center' }}>
            <Spin size="small" /> <span style={{ marginLeft: 8, color: '#666' }}>正在上传...</span>
          </div>
        )}
      </Card>

      {docs.length > 0 ? (
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
      ) : (
        <Empty
          image={<InboxOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
          description={
            <span style={{ color: '#999' }}>
              暂无文档，请拖拽文件到上方上传区域或点击上传
            </span>
          }
        />
      )}
    </div>
  );
}
