/**
 * Empty State Component for OpenLens
 * 
 * A customizable empty state component for when there's no data to display
 */

import React from 'react';
import { Button, Typography, Space, Card } from 'antd';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  image?: React.ReactNode;
  action?: React.ReactNode;
  actionText?: string;
  onAction?: () => void;
  style?: React.CSSProperties;
  className?: string;
  card?: boolean;
  cardProps?: any;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Data',
  description = 'There is no data to display',
  icon,
  image,
  action,
  actionText,
  onAction,
  style = {},
  className = '',
  card = false,
  cardProps = {},
}) => {
  // Default icons based on common use cases
  const defaultIcons: Record<string, React.ReactNode> = {
    data: '📊',
    search: '🔍',
    users: '👥',
    settings: '⚙️',
    files: '📁',
    messages: '💬',
    notifications: '🔔',
    default: '📭',
  };

  // Get icon
  const getIcon = () => {
    if (icon) return icon;
    if (title) {
      const lowerTitle = title.toLowerCase();
      for (const [key, value] of Object.entries(defaultIcons)) {
        if (lowerTitle.includes(key)) {
          return value;
        }
      }
    }
    return defaultIcons.default;
  };

  // Build content
  const content = (
    <Space
      direction="vertical"
      align="center"
      style={{
        padding: 40,
        textAlign: 'center',
        ...style,
      }}
      className={className}
    >
      {/* Image or Icon */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        style={{ fontSize: 64, marginBottom: 16 }}
      >
        {image || getIcon()}
      </motion.div>

      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <Title level={3} style={{ margin: 0 }}>
          {title}
        </Title>
      </motion.div>

      {/* Description */}
      {description && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <Text type="secondary" style={{ fontSize: 14 }}>
            {description}
          </Text>
        </motion.div>
      )}

      {/* Action */}
      {(action || (actionText && onAction)) && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          style={{ marginTop: 24 }}
        >
          {action || (
            <Button type="primary" onClick={onAction}>
              {actionText}
            </Button>
          )}
        </motion.div>
      )}
    </Space>
  );

  // Return with card if enabled
  if (card) {
    return (
      <Card
        bodyStyle={{ padding: 0 }}
        style={{ borderRadius: 12, ...cardProps?.style }}
        {...cardProps}
      >
        {content}
      </Card>
    );
  }

  return content;
};

// NoData component (alias for EmptyState)
export const NoData: React.FC<EmptyStateProps> = (props) => {
  return (
    <EmptyState
      title="No Data"
      description="There is no data available"
      {...props}
    />
  );
};

// NoResults component
interface NoResultsProps extends Omit<EmptyStateProps, 'title' | 'description'> {
  query?: string;
}

export const NoResults: React.FC<NoResultsProps> = ({
  query,
  ...props
}) => {
  return (
    <EmptyState
      title="No Results Found"
      description={query ? `No results found for "${query}"` : 'No results found'}
      icon="🔍"
      {...props}
    />
  );
};

// ErrorState component
interface ErrorStateProps extends Omit<EmptyStateProps, 'title' | 'description' | 'icon'> {
  error?: Error | string;
  retryText?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  error,
  retryText = 'Try Again',
  onRetry,
  ...props
}) => {
  const message = error instanceof Error ? error.message : String(error);

  return (
    <EmptyState
      title="Error"
      description={message || 'An error occurred'}
      icon="⚠️"
      actionText={retryText}
      onAction={onRetry}
      {...props}
    />
  );
};

// LoadingState component
interface LoadingStateProps extends Omit<EmptyStateProps, 'title' | 'description' | 'icon'> {
  loading?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  loading = true,
  ...props
}) => {
  if (!loading) {
    return null;
  }

  return (
    <EmptyState
      title="Loading..."
      description="Please wait while we load your data"
      icon="⏳"
      {...props}
    />
  );
};

// EmptyTable component
interface EmptyTableProps extends EmptyStateProps {
  columns?: number;
}

export const EmptyTable: React.FC<EmptyTableProps> = ({
  columns = 4,
  ...props
}) => {
  return (
    <EmptyState
      title="No Data"
      description="There is no data to display in the table"
      icon="📋"
      {...props}
    />
  );
};

// EmptyList component
interface EmptyListProps extends EmptyStateProps {
  itemType?: string;
}

export const EmptyList: React.FC<EmptyListProps> = ({
  itemType = 'items',
  ...props
}) => {
  return (
    <EmptyState
      title={`No ${itemType}`}
      description={`There are no ${itemType} to display`}
      icon="📝"
      {...props}
    />
  );
};

export default EmptyState;
