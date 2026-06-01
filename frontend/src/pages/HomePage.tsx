import { useNavigate } from 'react-router-dom';
import { Card, Button, Space, Modal, Form, Input, message, Spin } from 'antd';
import { PlusOutlined, DeleteOutlined, BookOutlined } from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { listKnowledgeBases, createKnowledgeBase, deleteKnowledgeBase } from '@/api/knowledge';
import type { KnowledgeBaseItem } from '@/types/api';

export default function HomePage() {
  const [kbs, setKBs] = useState<KnowledgeBaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const fetchKBs = async () => {
    setLoading(true);
    try {
      const data = await listKnowledgeBases();
      setKBs(data);
    } catch {
      // 后端未启动，用假数据
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
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h2>知识库管理</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          新建知识库
        </Button>
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
              actions={[
                <DeleteOutlined
                  key="delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(kb.id);
                  }}
                  style={{ color: '#ff4d4f' }}
                />,
              ]}
            >
              <Card.Meta
                avatar={<BookOutlined style={{ fontSize: 24, color: '#1677ff' }} />}
                title={kb.name}
                description={kb.description || '暂无描述'}
              />
            </Card>
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 80, color: '#999' }}>
          <BookOutlined style={{ fontSize: 48, marginBottom: 16 }} />
          <p>暂无知识库，点击上方按钮创建第一个</p>
        </div>
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
