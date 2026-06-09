import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Typography, Row, Col, Card, Steps, Space } from 'antd';
import {
  DatabaseOutlined,
  MessageOutlined,
  SafetyOutlined,
  CloudUploadOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/hooks/useAuth';

const { Title, Paragraph, Text } = Typography;

const features = [
  {
    icon: <DatabaseOutlined style={{ fontSize: 36, color: '#1677ff' }} />,
    title: '文档管理',
    desc: '支持 PDF、Word、Markdown、TXT 等格式，上传后自动切块、向量化，存入向量数据库。',
  },
  {
    icon: <MessageOutlined style={{ fontSize: 36, color: '#722ed1' }} />,
    title: '智能问答',
    desc: '基于文档内容的 AI 对话，回答附带来源引用，方便追溯原文。',
  },
  {
    icon: <SafetyOutlined style={{ fontSize: 36, color: '#52c41a' }} />,
    title: '安全可控',
    desc: '本地部署，数据不离开你的服务器，适合处理敏感文档与内部知识。',
  },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (isLoggedIn) {
      navigate('/home', { replace: true });
    }
  }, [isLoggedIn, navigate]);

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      {/* Hero */}
      <div
        style={{
          maxWidth: 960,
          margin: '0 auto',
          padding: '120px 24px 80px',
          textAlign: 'center',
        }}
      >
        <Title
          level={1}
          style={{ color: '#fff', fontSize: 48, marginBottom: 16, fontWeight: 700 }}
        >
          白泽 BaiZe
        </Title>
        <Paragraph
          style={{ color: 'rgba(255,255,255,0.85)', fontSize: 20, marginBottom: 40, lineHeight: 1.6 }}
        >
          本地部署的 RAG 知识库平台。上传文档，智能问答，数据完全留在本地。
        </Paragraph>
        <Space size={16}>
          <Button
            type="primary"
            size="large"
            onClick={() => navigate('/login')}
            style={{ height: 48, paddingInline: 32, fontSize: 16 }}
          >
            开始使用
          </Button>
          <Button
            size="large"
            ghost
            onClick={() => {
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            }}
            style={{ height: 48, paddingInline: 32, fontSize: 16, color: '#fff', borderColor: '#fff' }}
          >
            了解更多
          </Button>
        </Space>
      </div>

      {/* Features */}
      <div id="features" style={{ background: '#fff', padding: '80px 24px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto', textAlign: 'center' }}>
          <Title level={2} style={{ marginBottom: 48 }}>
            核心功能
          </Title>
          <Row gutter={[32, 32]}>
            {features.map((f) => (
              <Col xs={24} md={8} key={f.title}>
                <Card
                  hoverable
                  style={{ height: '100%', textAlign: 'center', borderRadius: 12 }}
                  styles={{ body: { padding: '32px 24px' } }}
                >
                  <div style={{ marginBottom: 16 }}>{f.icon}</div>
                  <Title level={4}>{f.title}</Title>
                  <Text type="secondary" style={{ fontSize: 15 }}>
                    {f.desc}
                  </Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </div>

      {/* How it works */}
      <div style={{ background: '#f7f8fa', padding: '80px 24px' }}>
        <div style={{ maxWidth: 640, margin: '0 auto', textAlign: 'center' }}>
          <Title level={2} style={{ marginBottom: 48 }}>
            三步开始
          </Title>
          <Steps
            direction="vertical"
            current={-1}
            items={[
              {
                title: '创建知识库',
                description: '为你的文档集合创建一个独立的知识库。',
                icon: <DatabaseOutlined />,
              },
              {
                title: '上传文档',
                description: '上传 PDF、Word、Markdown 等文件，系统自动处理。',
                icon: <CloudUploadOutlined />,
              },
              {
                title: '开始对话',
                description: '用自然语言提问，AI 从文档中检索并生成答案。',
                icon: <MessageOutlined />,
              },
            ]}
          />
        </div>
      </div>

      {/* Tech stack */}
      <div style={{ background: '#fff', padding: '80px 24px' }}>
        <div style={{ maxWidth: 960, margin: '0 auto', textAlign: 'center' }}>
          <Title level={2} style={{ marginBottom: 32 }}>
            技术栈
          </Title>
          <Row gutter={[24, 24]} justify="center">
            {[
              'FastAPI',
              'React',
              'Milvus',
              'Ant Design',
              'Celery',
              'SQLite',
            ].map((t) => (
              <Col key={t}>
                <Text
                  style={{
                    padding: '8px 20px',
                    borderRadius: 20,
                    background: '#f0f0f0',
                    fontSize: 15,
                  }}
                >
                  {t}
                </Text>
              </Col>
            ))}
          </Row>
        </div>
      </div>

      {/* CTA */}
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '80px 24px', textAlign: 'center' }}>
        <Title level={2} style={{ color: '#fff', marginBottom: 16 }}>
          准备好了吗？
        </Title>
        <Paragraph style={{ color: 'rgba(255,255,255,0.85)', fontSize: 18, marginBottom: 32 }}>
          几分钟即可完成本地部署，开始构建你的私有知识库。
        </Paragraph>
        <Button
          type="primary"
          size="large"
          onClick={() => navigate('/login')}
          style={{
            height: 48,
            paddingInline: 40,
            fontSize: 16,
            background: '#fff',
            color: '#667eea',
            borderColor: '#fff',
          }}
        >
          <RocketOutlined /> 立即开始
        </Button>
      </div>

      {/* Footer */}
      <div
        style={{
          background: '#1a1a2e',
          padding: '24px',
          textAlign: 'center',
        }}
      >
        <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 13 }}>
          白泽 BaiZe &mdash; 基于 RAG 的本地知识库平台
        </Text>
      </div>
    </div>
  );
}
