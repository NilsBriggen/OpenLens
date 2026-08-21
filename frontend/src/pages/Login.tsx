import React, { useState } from 'react';
import { Form, Input, Button, Checkbox, Alert, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import axios from 'axios';
import { motion } from 'framer-motion';

const { Title, Text, Link } = Typography;

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string; remember: boolean }) => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock login for development
      if (values.username === 'admin' && values.password === 'admin') {
        Cookies.set('access_token', 'mock-token', { expires: values.remember ? 30 : 1 });
        Cookies.set('refresh_token', 'mock-refresh-token', { expires: 7 });
        navigate('/');
      } else {
        setError('Invalid username or password');
      }

      // Real API call (uncomment when backend is ready)
      /*
      const response = await axios.post('http://localhost:8000/api/security/token', {
        username: values.username,
        password: values.password,
      });
      
      Cookies.set('access_token', response.data.access_token, { expires: values.remember ? 30 : 1 });
      Cookies.set('refresh_token', response.data.refresh_token, { expires: 7 });
      navigate('/');
      */
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
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
        />
      )}

      <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
        Welcome to OpenLens
      </Title>

      <Form
        name="login"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        layout="vertical"
      >
        <Form.Item
          name="username"
          label="Username"
          rules={[{ required: true, message: 'Please input your username!' }]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="Enter your username"
            size="large"
          />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[{ required: true, message: 'Please input your password!' }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="Enter your password"
            size="large"
          />
        </Form.Item>

        <Form.Item>
          <Form.Item name="remember" valuePropName="checked" noStyle>
            <Checkbox>Remember me</Checkbox>
          </Form.Item>
          <Link style={{ float: 'right' }}>
            Forgot password?
          </Link>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
            size="large"
            icon={<LoginOutlined />}
          >
            Log In
          </Button>
        </Form.Item>
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
