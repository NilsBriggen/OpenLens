/**
 * Loading Spinner Component for OpenLens
 * 
 * A reusable loading spinner with various styles and sizes
 */

import React from 'react';
import { Spin, Typography, Space } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  tip?: string;
  fullScreen?: boolean;
  style?: React.CSSProperties;
  spinnerStyle?: React.CSSProperties;
  children?: React.ReactNode;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip,
  fullScreen = false,
  style = {},
  spinnerStyle = {},
  children,
}) => {
  // Get size styles
  const getSize = () => {
    switch (size) {
      case 'small': return 'small';
      case 'large': return 'large';
      default: return 'default';
    }
  };

  // Full screen spinner
  if (fullScreen) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          ...style,
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={{
            background: 'var(--card-bg)',
            padding: 32,
            borderRadius: 12,
            textAlign: 'center',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
          }}
        >
          <Spin
            size={getSize()}
            tip={tip}
            style={spinnerStyle}
          />
          {children && (
            <div style={{ marginTop: 16 }}>
              {children}
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  // Inline spinner
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={style}
    >
      <Spin
        size={getSize()}
        tip={tip}
        style={spinnerStyle}
      />
      {children && (
        <div style={{ marginTop: 8 }}>
          {children}
        </div>
      )}
    </motion.div>
  );
};

// Spinner with text
interface SpinnerWithTextProps extends LoadingSpinnerProps {
  text?: string;
}

export const SpinnerWithText: React.FC<SpinnerWithTextProps> = ({
  text,
  tip,
  ...props
}) => {
  return (
    <LoadingSpinner tip={tip || text} {...props}>
      {text && !tip && <Text type="secondary">{text}</Text>}
    </LoadingSpinner>
  );
};

// Button spinner (for buttons)
interface ButtonSpinnerProps {
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
}

export const ButtonSpinner: React.FC<ButtonSpinnerProps> = ({
  size = 'small',
  style = {},
}) => {
  return (
    <LoadingOutlined
      spin
      style={{
        fontSize: size === 'small' ? 12 : size === 'large' ? 20 : 16,
        ...style,
      }}
    />
  );
};

export default LoadingSpinner;
