import { useEffect, useState } from 'react';
import { Card, Statistic, Row, Col, message, Button, Skeleton } from 'antd';
import {
  DatabaseOutlined,
  FileOutlined,
  BlockOutlined,
  MessageOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { getStats } from '@/api/knowledge';
import type { StatsOverview } from '@/types/api';

/** 数字千分位格式化 */
const formatNumber = (n: number) => {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`;
  return n.toLocaleString();
};

export default function StatsPage() {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const data = await getStats();
      setStats(data);
    } catch {
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>统计概览</h2>
        <Button
          icon={<ReloadOutlined />}
          onClick={fetchStats}
          loading={loading}
        >
          刷新
        </Button>
      </div>

      {loading ? (
        <Row gutter={16}>
          {[1, 2, 3, 4].map((i) => (
            <Col span={6} key={i}>
              <Card>
                <Skeleton active paragraph={{ rows: 1 }} />
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="知识库"
                value={formatNumber(stats?.knowledge_base_count || 0)}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="文档总数"
                value={formatNumber(stats?.document_count || 0)}
                prefix={<FileOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="切块总数"
                value={formatNumber(stats?.chunk_count || 0)}
                prefix={<BlockOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="近7天对话"
                value={formatNumber(stats?.chat_count_7d || 0)}
                prefix={<MessageOutlined />}
              />
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}
