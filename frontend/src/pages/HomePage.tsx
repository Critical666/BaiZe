import { useNavigate } from 'react-router-dom';
import { Card, Button, Space, Modal, Form, Input, message, Spin, Alert, Empty } from 'antd';
import { PlusOutlined, DeleteOutlined, BookOutlined, FileTextOutlined, FileAddOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { listKnowledgeBases, createKnowledgeBase, deleteKnowledgeBase } from '@/api/knowledge';
import { useAuth } from '@/hooks/useAuth';
import type { KnowledgeBaseItem } from '@/types/api';

export default function HomePage() {
  const [kbs, setKBs] = useState<KnowledgeBaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();

  const fetchKBs = async () => {
    setLoading(true);
    try {
      const data = await listKnowledgeBases();
      setKBs(data);
    } catch {
      message.error('获取知识库列表失败');
      setKBs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKBs();
  }, []);

  const handleCreate = async (values: { name: string; description?: string }) => {
    setSubmitting(true);
    try {
      await createKnowledgeBase(values);
      message.success('创建成功');
      setModalOpen(false);
      form.resetFields();
      fetchKBs();
    } catch {
      message.error('创建失败');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除后无法恢复，关联的文档和向量数据也将被清除。',
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteKnowledgeBase(id);
          message.success('已删除');
          fetchKBs();
        } catch {
          message.error('删除失败');
        }
      },
    });
  };

  return (
    <div>
      {!isAdmin && (
        <Alert
          message="你当前是普通用户，只能查看知识库和上传文档。如需创建/删除知识库，请联系管理员。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h2>知识库管理</h2>
        {isAdmin && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            新建知识库
          </Button>
        )}
      </div>

      {loading ? (
        <Spin size="large" style={{ display: 'block', margin: '120px auto' }} />
      ) : kbs.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16 }}>
          {kbs.map((kb) => (
            <Card
              key={kb.id}
              hoverable
              onClick={() => navigate(`/kb/${kb.id}`)}
              actions={
                isAdmin
                  ? [
                      <DeleteOutlined
                        key="delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(kb.id);
                        }}
                        style={{ color: '#ff4d4f' }}
                      />,
                    ]
                  : undefined
              }
            >
              <Card.Meta
                avatar={<BookOutlined style={{ fontSize: 24, color: '#1677ff' }} />}
                title={kb.name}
                description={
                  <>
                    <div style={{ color: '#999', marginBottom: 4 }}>
                      <FileTextOutlined /> 创建于 {kb.created_at?.split('T')[0]}
                    </div>
                    <div style={{ color: '#999', marginBottom: 4 }}>
                      <FileAddOutlined /> 文档数：{kb.document_count != null ? kb.document_count : '-'}
                    </div>
                    <div>{kb.description || '暂无描述'}</div>
                  </>
                }
              />
            </Card>
          ))}
        </div>
      ) : (
        <Empty
          image={<BookOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
          description={
            <span>
              <div style={{ fontSize: 16, color: '#666', marginBottom: 8 }}>
                {isAdmin ? '还没有知识库，开始创建你的第一个知识库吧' : '暂无知识库，请联系管理员创建'}
              </div>
              <div style={{ color: '#999', fontSize: 13 }}>
                知识库可以帮你管理和检索文档，通过 AI 进行智能问答
              </div>
            </span>
          }
        >
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
              新建知识库
            </Button>
          )}
        </Empty>
      )}

      <Modal
        title="新建知识库"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical">
          <Form.Item name="name" label="名称" rules={[{ required: true, max: 255 }]}>
            <Input placeholder="请输入知识库名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} placeholder="请简要介绍该知识库的内容" />
          </Form.Item>
          <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
            <Button onClick={() => setModalOpen(false)}>取消</Button>
            <Button type="primary" htmlType="submit" loading={submitting}>
              创建
            </Button>
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
