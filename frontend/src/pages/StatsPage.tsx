import { useEffect, useState } from 'react';
import { Card, Statistic, Row, Col, Spin } from 'antd';
import { DatabaseOutlined, FileOutlined, BlockOutlined, MessageOutlined } from '@ant-design/icons';
import { getStats } from '@/api/knowledge';
import type { StatsOverview } from '@/types/api';

export default function StatsPage() {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '120px auto' }} />;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>统计概览</h2>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="知识库"
              value={stats?.knowledge_base_count || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="文档总数"
              value={stats?.document_count || 0}
              prefix={<FileOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="切块总数"
              value={stats?.chunk_count || 0}
              prefix={<BlockOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="近7天对话"
              value={stats?.chat_count_7d || 0}
              prefix={<MessageOutlined />}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
