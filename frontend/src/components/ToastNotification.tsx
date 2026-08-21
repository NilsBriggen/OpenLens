/**
 * Toast Notification System for OpenLens
 * 
 * A flexible, customizable toast notification system with:
 * - Multiple notification types (success, error, warning, info)
 * - Auto-dismiss
 * - Custom positioning
 * - Rich content support
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Alert, Button, Space, Typography, Card } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Text } = Typography;

interface ToastNotificationProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
  closable?: boolean;
  showProgress?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const ToastNotification: React.FC<ToastNotificationProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
  position = 'top-right',
  closable = true,
  showProgress = true,
  action,
}) => {
  const [progress, setProgress] = useState(100);

  // Start auto-dismiss timer
  useEffect(() => {
    if (duration > 0) {
      const timer = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev - (100 / (duration / 100));
          if (newProgress <= 0) {
            clearInterval(timer);
            onClose(id);
          }
          return newProgress;
        });
      }, 100);

      return () => clearInterval(timer);
    }
  }, [duration, id, onClose]);

  // Get icon for notification type
  const getIcon = () => {
    switch (type) {
      case 'success': return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />;
      case 'error': return <CloseCircleOutlined style={{ color: '#f5222d', fontSize: 20 }} />;
      case 'warning': return <WarningOutlined style={{ color: '#faad14', fontSize: 20 }} />;
      case 'info': return <InfoCircleOutlined style={{ color: '#1890ff', fontSize: 20 }} />;
      default: return null;
    }
  };

  // Get color for notification type
  const getColor = () => {
    switch (type) {
      case 'success': return '#52c41a';
      case 'error': return '#f5222d';
      case 'warning': return '#faad14';
      case 'info': return '#1890ff';
      default: return '#1890ff';
    }
  };

  // Get position styles
  const getPositionStyles = () => {
    const positions: Record<string, React.CSSProperties> = {
      'top-left': { top: 24, left: 24 },
      'top-right': { top: 24, right: 24 },
      'bottom-left': { bottom: 24, left: 24 },
      'bottom-right': { bottom: 24, right: 24 },
      'top-center': { top: 24, left: '50%', transform: 'translateX(-50%)' },
      'bottom-center': { bottom: 24, left: '50%', transform: 'translateX(-50%)' },
    };
    return positions[position] || positions['top-right'];
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: position.includes('right') ? 100 : position.includes('left') ? -100 : 0, y: position.includes('top') ? -100 : 100 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      exit={{ opacity: 0, x: position.includes('right') ? 100 : position.includes('left') ? -100 : 0, y: position.includes('top') ? -100 : 100 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'fixed',
        zIndex: 1000,
        maxWidth: 400,
        width: '100%',
        ...getPositionStyles(),
      }}
    >
      <Card
        size="small"
        style={{
          borderRadius: 8,
          borderLeft: `4px solid ${getColor()}`,
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
          background: 'var(--card-bg)',
        }}
        bodyStyle={{ padding: 16 }}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Space>
              {getIcon()}
              <div>
                {title && <Text strong style={{ fontSize: 14 }}>{title}</Text>}
                <Text style={{ fontSize: 13 }}>{message}</Text>
              </div>
            </Space>
            
            {closable && (
              <Button
                type="text"
                icon={<CloseOutlined />}
                onClick={() => onClose(id)}
                size="small"
                style={{ color: '#666' }}
              />
            )}
          </div>

          {showProgress && duration > 0 && (
            <div
              style={{
                height: 4,
                background: 'rgba(0, 0, 0, 0.1)',
                borderRadius: 2,
                overflow: 'hidden',
                marginTop: 12,
              }}
            >
              <motion.div
                style={{
                  height: '100%',
                  background: getColor(),
                  borderRadius: 2,
                }}
                initial={{ width: '100%' }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.1 }}
              />
            </div>
          )}

          {action && (
            <div style={{ marginTop: 12, textAlign: 'right' }}>
              <Button
                type="link"
                size="small"
                onClick={action.onClick}
                style={{ color: getColor() }}
              >
                {action.label}
              </Button>
            </div>
          )}
        </Space>
      </Card>
    </motion.div>
  );
};

// Toast Container Component
interface ToastContainerProps {
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
  maxToasts?: number;
}

const ToastContainer: React.FC<ToastContainerProps> = ({
  position = 'top-right',
  maxToasts = 5,
}) => {
  const [toasts, setToasts] = useState<ToastNotificationProps[]>([]);

  // Add toast
  const addToast = useCallback((toast: Omit<ToastNotificationProps, 'id' | 'onClose' | 'position'>) => {
    const id = Date.now().toString();
    setToasts(prev => [
      { ...toast, id, position, onClose: (id) => removeToast(id) },
      ...prev.slice(0, maxToasts - 1),
    ]);
  }, [position, maxToasts]);

  // Remove toast
  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <>
      <AnimatePresence>
        {toasts.map(toast => (
          <ToastNotification key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    
      {/* Expose addToast function via context or ref */}
    </>
  );
};

// Toast Hook
const useToast = (position?: ToastContainerProps['position']) => {
  const [container, setContainer] = useState<JSX.Element | null>(null);

  const addToast = useCallback((toast: Omit<ToastNotificationProps, 'id' | 'onClose' | 'position'>) => {
    // Create a temporary container if it doesn't exist
    if (!container) {
      const toastId = Date.now().toString();
      const toastElement = (
        <ToastNotification
          key={toastId}
          id={toastId}
          type={toast.type}
          title={toast.title}
          message={toast.message}
          duration={toast.duration}
          onClose={() => {}}
          position={position || 'top-right'}
          closable={toast.closable}
          showProgress={toast.showProgress}
          action={toast.action}
        />
      );
      
      // Render the toast
      const div = document.createElement('div');
      div.id = `toast-${toastId}`;
      document.body.appendChild(div);
      
      // Use ReactDOM to render (this is a simplified version)
      // In a real implementation, you'd use ReactDOM.createPortal
      console.log('Toast added:', toast);
    }
  }, [container, position]);

  return { addToast };
};

// Simple toast function (imperative API)
let toastContainer: { addToast: (toast: Omit<ToastNotificationProps, 'id' | 'onClose' | 'position'>) => void } | null = null;

export const toast = {
  success: (message: string, options?: Partial<ToastNotificationProps>) => {
    if (toastContainer) {
      toastContainer.addToast({
        type: 'success',
        message,
        ...options,
      });
    }
  },
  error: (message: string, options?: Partial<ToastNotificationProps>) => {
    if (toastContainer) {
      toastContainer.addToast({
        type: 'error',
        message,
        ...options,
      });
    }
  },
  warning: (message: string, options?: Partial<ToastNotificationProps>) => {
    if (toastContainer) {
      toastContainer.addToast({
        type: 'warning',
        message,
        ...options,
      });
    }
  },
  info: (message: string, options?: Partial<ToastNotificationProps>) => {
    if (toastContainer) {
      toastContainer.addToast({
        type: 'info',
        message,
        ...options,
      });
    }
  },
  // Initialize toast container
  init: (container: { addToast: (toast: Omit<ToastNotificationProps, 'id' | 'onClose' | 'position'>) => void }) => {
    toastContainer = container;
  },
};

export { ToastContainer, useToast };
export default ToastNotification;
