import React, { useState } from 'react';
import { Form, Input, Button, Checkbox, Alert, Typography, Space, Card } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, LoginOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCreateUser, isAuthenticated } from '../hooks/useApi';
import { message } from 'antd';

const { Title, Text } = Typography;

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const createUserMutation = useCreateUser();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated()) {
      navigate('/', { replace: true });
    }
  }, [navigate]);

  const onFinish = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      // Validate password match
      if (values.password !== values.confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }

      // Call the API to create user
      await createUserMutation.mutateAsync({
        username: values.username,
        password: values.password,
        email: values.email,
        full_name: values.fullName,
      });

      setSuccess(true);
      message.success('Registration successful! Please log in.');
      setTimeout(() => navigate('/login'), 2000);
      
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
      message.error(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        style={{ textAlign: 'center', maxWidth: 400, margin: '0 auto' }}
      >
        <Card>
          <Alert
            message="Registration successful! Redirecting to login..."
            type="success"
            showIcon
          />
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{ maxWidth: 400, margin: '0 auto' }}
    >
      <Card>
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

        <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
          Create an Account
        </Title>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          scrollToFirstError
          size="large"
        >
          <Form.Item
            name="fullName"
            label="Full Name"
            rules={[{ required: true, message: 'Please input your full name!' }]}
          >
            <Input
              prefix={<UserOutlined className="site-form-item-icon" />}
              placeholder="Enter your full name"
              autoComplete="name"
            />
          </Form.Item>

          <Form.Item
            name="username"
            label="Username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input
              prefix={<UserOutlined className="site-form-item-icon" />}
              placeholder="Enter your username"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' },
            ]}
          >
            <Input
              prefix={<MailOutlined className="site-form-item-icon" />}
              placeholder="Enter your email"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="Enter your password"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="Confirm Password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('The two passwords do not match!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined className="site-form-item-icon" />}
              placeholder="Confirm your password"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item 
            name="agreement" 
            valuePropName="checked" 
            rules={[{ 
              validator: (_, value) => value ? Promise.resolve() : Promise.reject('You must accept the terms!') 
            }]}
          >
            <Checkbox>
              I have read and agree to the <Link to="/terms">Terms of Service</Link>
            </Checkbox>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading || createUserMutation.isPending}
              block
              size="large"
              icon={<LoginOutlined />}
            >
              Register
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Text type="secondary">
            Already have an account? <Link to="/login">Log in</Link>
          </Text>
        </div>
      </Card>
    </motion.div>
  );
};

export default Register;
