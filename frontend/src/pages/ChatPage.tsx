import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input, Button, Space } from 'antd';
import { ArrowLeftOutlined, SendOutlined } from '@ant-design/icons';
import { chatWithKB } from '@/api/knowledge';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
}

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '你好！我是知识库助手，请向我提问。' },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || !id) return;
    const question = input;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setSending(true);

    try {
      const res = await chatWithKB(id, question);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.answer, sources: res.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '抱歉，对话服务暂不可用。' },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Space style={{ marginBottom: 24 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/kb/${id}`)}>
          返回
        </Button>
        <h2 style={{ margin: 0 }}>对话</h2>
      </Space>

      <div
        style={{
          height: '60vh',
          overflowY: 'auto',
          marginBottom: 16,
          padding: 16,
          background: '#f5f5f5',
          borderRadius: 12,
        }}
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: 16,
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '12px 16px',
                borderRadius: 12,
                background: msg.role === 'user' ? '#1677ff' : '#fff',
                color: msg.role === 'user' ? '#fff' : '#333',
                boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
                  来源: {msg.sources.join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <Space.Compact style={{ width: '100%' }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={handleSend}
          placeholder="输入问题，按 Enter 发送..."
          size="large"
          disabled={sending}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          size="large"
          onClick={handleSend}
          loading={sending}
        />
      </Space.Compact>
    </div>
  );
}
