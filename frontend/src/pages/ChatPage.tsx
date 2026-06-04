import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input, Button, Space, Tag, Spin, Typography, Popconfirm } from 'antd';
import { ArrowLeftOutlined, SendOutlined, RobotOutlined, UserOutlined, DownOutlined, UpOutlined, PlusOutlined } from '@ant-design/icons';
import { chatWithKB, getChatHistory } from '@/api/knowledge';

const { Text } = Typography;

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  id: string;
  loading?: boolean;
  /** 打字动效已显示的字符数 */
  typedCount?: number;
}

let msgIdCounter = 0;
const createMessage = (role: 'user' | 'assistant', content: string, sources?: string[], loading?: boolean): Message => ({
  id: `msg-${Date.now()}-${++msgIdCounter}`,
  role,
  content,
  sources,
  loading,
});

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [isNewChat, setIsNewChat] = useState(false);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);
  // 记录需要打字动效的消息 id
  const [typingMsgId, setTypingMsgId] = useState<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 加载聊天历史记录
  useEffect(() => {
    if (!id || historyLoaded) return;
    let cancelled = false;
    (async () => {
      try {
        const history = await getChatHistory(id);
        if (cancelled) return;
        // history 按时间倒序返回，反转为正序
        const loaded: Message[] = [];
        for (const item of [...history].reverse()) {
          loaded.push(createMessage('user', item.question));
          loaded.push(createMessage('assistant', item.answer, item.sources));
        }
        // 如果没有历史记录，显示欢迎消息
        setMessages(
          loaded.length > 0
            ? loaded
            : [createMessage('assistant', '你好！我是白泽知识库助手，请向我提问。')],
        );
        setHistoryLoaded(true);
      } catch {
        setMessages([createMessage('assistant', '你好！我是白泽知识库助手，请向我提问。')]);
        setHistoryLoaded(true);
      }
    })();
    return () => { cancelled = true; };
  }, [id, historyLoaded]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 打字动效：逐步显示字符
  const typewrite = useCallback((msgId: string, fullText: string) => {
    let count = 0;
    const timer = setInterval(() => {
      count += 2; // 每次显示 2 个字符
      if (count >= fullText.length) {
        count = fullText.length;
        clearInterval(timer);
        setTypingMsgId(null);
      }
      setMessages((prev) =>
        prev.map((m) => (m.id === msgId ? { ...m, typedCount: count } : m)),
      );
    }, 30);
    return timer;
  }, []);

  const handleNewChat = useCallback(() => {
    setMessages([createMessage('assistant', '你好！我是白泽知识库助手，请向我提问。')]);
    setIsNewChat(true);
    setTypingMsgId(null);
    setTimeout(() => inputRef.current?.focus(), 100);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || !id) return;
    const question = input;
    setInput('');
    setSending(true);

    // 添加用户消息
    const userMsg = createMessage('user', question);
    // 添加加载中的助手消息
    const loadingMsg = createMessage('assistant', '', [], true);
    setMessages((prev) => [...prev, userMsg, loadingMsg]);

    // 聚焦输入框
    setTimeout(() => inputRef.current?.focus(), 100);

    try {
      const res = await chatWithKB(id, question, isNewChat);
      // 新对话第一条消息发送后，后续不再携带 new_chat 标记
      setIsNewChat(false);
      const newMsg = createMessage('assistant', res.answer, res.sources);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = newMsg;
        return updated;
      });
      // 启动打字动效
      setTypingMsgId(newMsg.id);
      typewrite(newMsg.id, res.answer);
    } catch {
      setIsNewChat(false);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = createMessage('assistant', '抱歉，对话服务暂不可用，请稍后重试。');
        return updated;
      });
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', display: 'flex', flexDirection: 'column', height: '80vh' }}>
      {/* 头部 */}
      <Space style={{ marginBottom: 16, flexShrink: 0 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(`/kb/${id}`)}>
          返回
        </Button>
        <h2 style={{ margin: 0 }}>白泽对话</h2>
        <Popconfirm
          title="新建对话"
          description="将清空当前对话内容，开始一段新对话。确认？"
          onConfirm={handleNewChat}
          okText="确认"
          cancelText="取消"
        >
          <Button icon={<PlusOutlined />}>新建对话</Button>
        </Popconfirm>
      </Space>

      {/* 消息区域 */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          marginBottom: 16,
          padding: '16px 8px',
          background: '#fafafa',
          borderRadius: 12,
          border: '1px solid #f0f0f0',
        }}
      >
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} isTyping={typingMsgId === msg.id} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ flexShrink: 0 }}>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={handleSend}
            placeholder="输入问题，按 Enter 发送..."
            size="large"
            disabled={sending}
            style={{ borderRadius: '8px 0 0 8px' }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            size="large"
            onClick={handleSend}
            loading={sending}
            style={{ borderRadius: '0 8px 8px 0' }}
          >
            发送
          </Button>
        </Space.Compact>
      </div>
    </div>
  );
}

/** 单条消息气泡（含可折叠来源引用） */
function MessageBubble({ msg, isTyping }: { msg: Message; isTyping: boolean }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  // 打字动效：截取已显示的部分
  const displayContent = isTyping && msg.typedCount !== undefined
    ? msg.content.slice(0, msg.typedCount)
    : msg.content;

  return (
    <div
      style={{
        marginBottom: 16,
        display: 'flex',
        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
        gap: 8,
      }}
    >
      {msg.role === 'assistant' && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: '#f0f5ff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <RobotOutlined style={{ color: '#1677ff' }} />
        </div>
      )}
      <div
        style={{
          maxWidth: '70%',
          padding: '12px 16px',
          borderRadius: 12,
          background: msg.role === 'user' ? '#1677ff' : '#fff',
          color: msg.role === 'user' ? '#fff' : '#333',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
          lineHeight: 1.6,
        }}
      >
        {msg.loading ? (
          <Space size={4}>
            <Spin size="small" />
            <Text type="secondary">正在思考...</Text>
          </Space>
        ) : (
          <>
            <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{displayContent}</div>
            {!isTyping && msg.sources && msg.sources.length > 0 && (
              <div style={{ marginTop: 8, borderTop: '1px solid #f0f0f0', paddingTop: 8 }}>
                <div
                  style={{ cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 4, marginBottom: 4 }}
                  onClick={() => setSourcesOpen(!sourcesOpen)}
                >
                  <Text type="secondary" style={{ fontSize: 12 }}>来源引用（{msg.sources.length}）</Text>
                  {sourcesOpen ? <UpOutlined style={{ fontSize: 10 }} /> : <DownOutlined style={{ fontSize: 10 }} />}
                </div>
                {sourcesOpen && (
                  <div style={{ marginTop: 4 }}>
                    {msg.sources.map((s, i) => (
                      <Tag key={i} style={{ marginBottom: 4, fontSize: 11 }}>{s}</Tag>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
      {msg.role === 'user' && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: '#e6f4ff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <UserOutlined style={{ color: '#1677ff' }} />
        </div>
      )}
    </div>
  );
}
