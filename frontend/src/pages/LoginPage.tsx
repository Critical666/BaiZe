import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Tabs, message } from 'antd';
import { login, register } from '@/api/auth';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setAuth } = useAuth();

  const handleSubmit = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      const res = await login({ email: values.email, password: values.password });
      setAuth(res.access_token, res.user);
      message.success('登录成功');
      navigate('/');
    } catch {
      message.error('登录失败，请检查邮箱和密码');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: { username: string; email: string; password: string }) => {
    setLoading(true);
    try {
      const res = await register(values);
      setAuth(res.access_token, res.user);
      message.success('注册成功');
      navigate('/');
    } catch {
      message.error('注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card style={{ width: 400 }}>
        <h1 style={{ textAlign: 'center', marginBottom: 24 }}>白泽 BaiZe</h1>
        <Tabs
          centered
          items={[
            {
              key: 'login',
              label: '登录',
              children: (
                <Form onFinish={handleSubmit} layout="vertical">
                  <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
                    <Input placeholder="邮箱" size="large" />
                  </Form.Item>
                  <Form.Item name="password" rules={[{ required: true, min: 6 }]}>
                    <Input.Password placeholder="密码" size="large" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block size="large">
                    登录
                  </Button>
                </Form>
              ),
            },
            {
              key: 'register',
              label: '注册',
              children: (
                <Form onFinish={handleRegister} layout="vertical">
                  <Form.Item name="username" rules={[{ required: true, min: 3 }]}>
                    <Input placeholder="用户名" size="large" />
                  </Form.Item>
                  <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
                    <Input placeholder="邮箱" size="large" />
                  </Form.Item>
                  <Form.Item name="password" rules={[{ required: true, min: 6 }]}>
                    <Input.Password placeholder="密码" size="large" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block size="large">
                    注册
                  </Button>
                </Form>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
