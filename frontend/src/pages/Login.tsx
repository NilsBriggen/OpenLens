import React, { useState } from 'react';
import { Form, Input, Button, Checkbox, Alert, Typography, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined, GithubOutlined, GoogleOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useLogin, isAuthenticated } from '../hooks/useApi';
import { message } from 'antd';

const { Title, Text, Link } = Typography;

interface LocationState {
  from?: { pathname: string };
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const loginMutation = useLogin();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated()) {
      const from = (location.state as LocationState)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [navigate, location]);

  const onFinish = async (values: { username: string; password: string; remember: boolean }) => {
    setLoading(true);
    setError(null);
    
    try {
      await loginMutation.mutateAsync({
        username: values.username,
        password: values.password,
      });
      
      // Redirect to the page the user came from, or to the dashboard
      const from = (location.state as LocationState)?.from?.pathname || '/';
      navigate(from, { replace: true });
      
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
      message.error(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider: string) => {
    message.info(`Social login with ${provider} is coming soon!`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
          closable
          onClose={() => setError(null)}
        />
      )}

      <Title
        level={2}
        style={{ textAlign: 'center', fontSize: 22, fontWeight: 600, marginBottom: 24 }}
      >
        Welcome to OpenLens
      </Title>

      <Form
        name="login"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        layout="vertical"
        size="large"
      >
        <Form.Item
          name="username"
          label="Username"
          style={{ marginBottom: 20 }}
          rules={[{ required: true, message: 'Please input your username!' }]}
        >
          <Input
            size="large"
            prefix={<UserOutlined className="site-form-item-icon" />}
            placeholder="Enter your username"
            autoComplete="username"
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          style={{ marginBottom: 20 }}
          rules={[{ required: true, message: 'Please input your password!' }]}
        >
          <Input.Password
            size="large"
            prefix={<LockOutlined className="site-form-item-icon" />}
            placeholder="Enter your password"
            autoComplete="current-password"
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 20 }}>
          <Space style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>Remember me</Checkbox>
            </Form.Item>
            <Link>Forgot password?</Link>
          </Space>
        </Form.Item>

        <Form.Item style={{ marginBottom: 20 }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading || loginMutation.isPending}
            block
            size="large"
            icon={<LoginOutlined />}
          >
            Log In
          </Button>
        </Form.Item>

        <Divider plain style={{ margin: '24px 0' }}>
          or
        </Divider>

        <div style={{ display: 'flex', gap: 12 }}>
          <Button
            icon={<GithubOutlined />}
            onClick={() => handleSocialLogin('GitHub')}
            style={{ flex: 1 }}
          >
            GitHub
          </Button>
          <Button
            icon={<GoogleOutlined />}
            onClick={() => handleSocialLogin('Google')}
            style={{ flex: 1 }}
          >
            Google
          </Button>
        </div>
      </Form>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Text type="secondary">
          Don't have an account? <Link onClick={() => navigate('/register')}>Register now</Link>
        </Text>
      </div>

      <div style={{ textAlign: 'center', marginTop: 16 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          Default credentials: admin / admin
        </Text>
      </div>
    </motion.div>
  );
};

export default Login;
