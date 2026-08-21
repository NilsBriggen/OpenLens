import React from 'react';
import { Result, Button, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{ textAlign: 'center', padding: 40 }}
    >
      <Result
        status="404"
        title="404"
        subTitle="Sorry, the page you visited does not exist."
        extra={[
          <Button
            type="primary"
            key="home"
            onClick={() => navigate('/')}
            size="large"
          >
            Back to Home
          </Button>,
          <Button
            key="contact"
            onClick={() => navigate('/settings')}
            size="large"
          >
            Settings
          </Button>,
        ]}
      />
    </motion.div>
  );
};

export default NotFound;
