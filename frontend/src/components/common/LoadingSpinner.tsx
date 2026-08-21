import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  size?: 'small' | 'default' | 'large';
  tip?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  fullScreen = false,
  size = 'large',
  tip = 'Loading...',
}) => {
  const spinnerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    ...(fullScreen ? {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 1000,
      background: 'rgba(255, 255, 255, 0.8)',
    } : {}),
  };

  return (
    <div style={spinnerStyle}>
      <Spin
        indicator={<LoadingOutlined style={{ fontSize: size === 'small' ? 16 : size === 'large' ? 48 : 24 }} spin />}
        size={size}
        tip={tip}
      />
    </div>
  );
};

export default LoadingSpinner;
