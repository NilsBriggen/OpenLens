/**
 * Error Boundary Component for OpenLens
 * 
 * Catches JavaScript errors in child components and displays a fallback UI
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Card, Button, Typography, Space, Alert } from 'antd';
import { WarningOutlined, ReloadOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      hasError: true,
      error,
      errorInfo,
    });

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log error to error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback
      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          style={{ padding: 24 }}
        >
          <Card
            title={
              <Space>
                <WarningOutlined style={{ color: '#faad14', fontSize: 20 }} />
                <Title level={4} style={{ margin: 0, color: '#faad14' }}>
                  Something went wrong
                </Title>
              </Space>
            }
            style={{ borderColor: '#faad14', borderRadius: 12 }}
          >
            <Alert
              message="An error occurred"
              description={this.state.error?.message || 'An unexpected error occurred'}
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Space>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={this.handleReset}
              >
                Try Again
              </Button>
              <Button onClick={() => window.location.reload()}>
                Reload Page
              </Button>
            </Space>

            {process.env.NODE_ENV === 'development' && (
              <div style={{ marginTop: 16, padding: 16, background: '#f0f0f0', borderRadius: 8 }}>
                <Text type="secondary" style={{ fontSize: 12, fontFamily: 'monospace' }}>
                  <pre>{this.state.error?.stack}</pre>
                </Text>
              </div>
            )}
          </Card>
        </motion.div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for error boundaries
const withErrorBoundary = (
  Component: React.ComponentType<any>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) => {
  return (props: any) => (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Component {...props} />
    </ErrorBoundary>
  );
};

// Hook for error handling
export const useErrorHandler = (
  onError?: (error: Error) => void
) => {
  const [error, setError] = React.useState<Error | null>(null);

  const handleError = React.useCallback(
    (error: Error) => {
      setError(error);
      if (onError) {
        onError(error);
      }
    },
    [onError]
  );

  const clearError = React.useCallback(() => {
    setError(null);
  }, []);

  return { error, handleError, clearError };
};

export { withErrorBoundary, useErrorHandler };
export default ErrorBoundary;
