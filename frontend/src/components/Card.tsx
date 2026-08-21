/**
 * Enhanced Card Component for OpenLens
 * 
 * A customizable card component with various styles and features
 */

import React from 'react';
import { Card as AntCard, Typography, Space, Button, Tooltip } from 'antd';
import { motion } from 'framer-motion';
import { MoreOutlined, EditOutlined, DeleteOutlined, EyeOutlined, ShareAltOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface CardProps {
  title?: React.ReactNode;
  extra?: React.ReactNode;
  children?: React.ReactNode;
  actions?: React.ReactNode[];
  footer?: React.ReactNode;
  cover?: React.ReactNode;
  bordered?: boolean;
  hoverable?: boolean;
  loading?: boolean;
  size?: 'default' | 'small';
  type?: 'default' | 'inner';
  headStyle?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onView?: () => void;
  onShare?: () => void;
  showActions?: boolean;
  actionIcons?: {
    edit?: boolean;
    delete?: boolean;
    view?: boolean;
    share?: boolean;
  };
  animated?: boolean;
  shadow?: boolean;
  hoverShadow?: boolean;
}

const Card: React.FC<CardProps> = ({
  title,
  extra,
  children,
  actions,
  footer,
  cover,
  bordered = true,
  hoverable = false,
  loading = false,
  size = 'default',
  type = 'default',
  headStyle = {},
  bodyStyle = {},
  style = {},
  className = '',
  onClick,
  onEdit,
  onDelete,
  onView,
  onShare,
  showActions = false,
  actionIcons = {},
  animated = true,
  shadow = false,
  hoverShadow = false,
}) => {
  // Default action icons
  const defaultActionIcons = {
    edit: true,
    delete: true,
    view: true,
    share: false,
    ...actionIcons,
  };

  // Build actions
  const buildActions = () => {
    if (actions) return actions;

    const actionButtons: React.ReactNode[] = [];

    if (showActions) {
      if (defaultActionIcons.view && onView) {
        actionButtons.push(
          <Tooltip key="view" title="View">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onView();
              }}
              size="small"
            />
          </Tooltip>
        );
      }

      if (defaultActionIcons.edit && onEdit) {
        actionButtons.push(
          <Tooltip key="edit" title="Edit">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              size="small"
            />
          </Tooltip>
        );
      }

      if (defaultActionIcons.share && onShare) {
        actionButtons.push(
          <Tooltip key="share" title="Share">
            <Button
              type="text"
              icon={<ShareAltOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onShare();
              }}
              size="small"
            />
          </Tooltip>
        );
      }

      if (defaultActionIcons.delete && onDelete) {
        actionButtons.push(
          <Tooltip key="delete" title="Delete">
            <Button
              type="text"
              icon={<DeleteOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
              size="small"
              danger
            />
          </Tooltip>
        );
      }
    }

    return actionButtons.length > 0 ? actionButtons : undefined;
  };

  // Build extra content
  const buildExtra = () => {
    if (extra) return extra;

    const actionButtons = buildActions();
    if (actionButtons && actionButtons.length > 0) {
      return (
        <Space>
          {actionButtons}
          {showActions && (
            <Button
              type="text"
              icon={<MoreOutlined />}
              size="small"
            />
          )}
        </Space>
      );
    }

    return undefined;
  };

  // Get shadow styles
  const getShadowStyles = () => {
    if (shadow) {
      return {
        boxShadow: '0 1px 2px -2px rgba(0, 0, 0, 0.08), 0 4px 5px 0 rgba(0, 0, 0, 0.08), 0 1px 5px -1px rgba(0, 0, 0, 0.08)',
      };
    }
    if (hoverShadow) {
      return {
        boxShadow: '0 1px 2px -2px rgba(0, 0, 0, 0.08), 0 4px 5px 0 rgba(0, 0, 0, 0.08), 0 1px 5px -1px rgba(0, 0, 0, 0.08)',
        transition: 'box-shadow 0.3s ease',
      };
    }
    return {};
  };

  // Get hover styles
  const getHoverStyles = () => {
    if (hoverable || hoverShadow) {
      return {
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease',
      };
    }
    return {};
  };

  return (
    <motion.div
      initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={hoverable ? { y: -4, boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)' } : {}}
      style={{
        ...getShadowStyles(),
        ...getHoverStyles(),
        ...style,
      }}
      className={className}
      onClick={onClick}
    >
      <AntCard
        title={title}
        extra={buildExtra()}
        actions={buildActions()}
        bordered={bordered}
        hoverable={hoverable}
        loading={loading}
        size={size}
        type={type}
        headStyle={{
          borderBottom: bordered ? '1px solid var(--border-color)' : 'none',
          ...headStyle,
        }}
        bodyStyle={{
          padding: size === 'small' ? 12 : 24,
          ...bodyStyle,
        }}
        cover={cover}
        style={{
          borderRadius: 12,
          background: 'var(--card-bg)',
          border: bordered ? '1px solid var(--border-color)' : 'none',
        }}
      >
        {children}
        {footer && <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>{footer}</div>}
      </AntCard>
    </motion.div>
  );
};

// StatCard component (for displaying statistics)
interface StatCardProps {
  title?: string;
  value?: string | number;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string | number;
  color?: string;
  background?: string;
  size?: 'small' | 'default' | 'large';
  onClick?: () => void;
  style?: React.CSSProperties;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  trendValue,
  color = '#1890ff',
  background,
  size = 'default',
  onClick,
  style = {},
  className = '',
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { title: number; value: number; icon: number }> = {
      small: { title: 12, value: 18, icon: 20 },
      default: { title: 14, value: 24, icon: 24 },
      large: { title: 16, value: 32, icon: 32 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get trend color
  const getTrendColor = () => {
    switch (trend) {
      case 'up': return '#52c41a';
      case 'down': return '#f5222d';
      case 'neutral': return '#d9d9d9';
      default: return '#d9d9d9';
    }
  };

  // Get trend icon
  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↑';
      case 'down': return '↓';
      case 'neutral': return '→';
      default: return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
      style={{
        background: background || 'var(--card-bg)',
        borderRadius: 12,
        padding: 24,
        border: '1px solid var(--border-color)',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
      className={className}
      onClick={onClick}
    >
      <Space direction="vertical" align="center">
        {icon && (
          <div
            style={{
              fontSize: sizeStyles.icon,
              color,
              marginBottom: 8,
            }}
          >
            {icon}
          </div>
        )}

        {value !== undefined && (
          <Title
            level={size === 'small' ? 5 : size === 'large' ? 2 : 3}
            style={{
              margin: 0,
              color,
              fontSize: sizeStyles.value,
            }}
          >
            {value}
          </Title>
        )}

        {title && (
          <Text
            type="secondary"
            style={{
              fontSize: sizeStyles.title,
              textAlign: 'center',
            }}
          >
            {title}
          </Text>
        )}

        {trend && trendValue !== undefined && (
          <Text
            style={{
              fontSize: sizeStyles.title * 0.8,
              color: getTrendColor(),
            }}
          >
            {getTrendIcon()} {trendValue}
          </Text>
        )}
      </Space>
    </motion.div>
  );
};

// ProfileCard component
interface ProfileCardProps {
  avatar?: string;
  name?: string;
  title?: string;
  description?: string;
  stats?: { label: string; value: string | number }[];
  actions?: React.ReactNode[];
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({
  avatar,
  name,
  title,
  description,
  stats = [],
  actions = [],
  size = 'default',
  style = {},
  className = '',
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { avatar: number; name: number; title: number }> = {
      small: { avatar: 40, name: 14, title: 12 },
      default: { avatar: 64, name: 16, title: 14 },
      large: { avatar: 80, name: 18, title: 16 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        background: 'var(--card-bg)',
        borderRadius: 12,
        padding: 24,
        border: '1px solid var(--border-color)',
        textAlign: 'center',
        ...style,
      }}
      className={className}
    >
      <Space direction="vertical" align="center">
        {avatar && (
          <img
            src={avatar}
            alt={name}
            style={{
              width: sizeStyles.avatar,
              height: sizeStyles.avatar,
              borderRadius: '50%',
              objectFit: 'cover',
              marginBottom: 16,
            }}
          />
        )}

        {name && (
          <Title
            level={size === 'small' ? 5 : size === 'large' ? 2 : 3}
            style={{
              margin: 0,
              fontSize: sizeStyles.name,
            }}
          >
            {name}
          </Title>
        )}

        {title && (
          <Text
            type="secondary"
            style={{
              fontSize: sizeStyles.title,
              marginBottom: 16,
            }}
          >
            {title}
          </Text>
        )}

        {description && (
          <Paragraph
            style={{
              fontSize: sizeStyles.title * 0.9,
              marginBottom: 16,
            }}
            ellipsis={{ rows: 2 }}
          >
            {description}
          </Paragraph>
        )}

        {stats.length > 0 && (
          <Space style={{ marginBottom: 16 }}>
            {stats.map((stat, index) => (
              <Space key={index} direction="vertical" align="center">
                <Title
                  level={5}
                  style={{
                    margin: 0,
                    fontSize: sizeStyles.title,
                  }}
                >
                  {stat.value}
                </Title>
                <Text type="secondary" style={{ fontSize: sizeStyles.title * 0.8 }}>
                  {stat.label}
                </Text>
              </Space>
            ))}
          </Space>
        )}

        {actions.length > 0 && (
          <Space>{actions}</Space>
        )}
      </Space>
    </motion.div>
  );
};

// FeatureCard component
interface FeatureCardProps {
  icon?: React.ReactNode;
  title?: string;
  description?: string;
  link?: string;
  linkText?: string;
  onClick?: () => void;
  style?: React.CSSProperties;
  className?: string;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  link,
  linkText = 'Learn More',
  onClick,
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4, boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)' }}
      style={{
        background: 'var(--card-bg)',
        borderRadius: 12,
        padding: 24,
        border: '1px solid var(--border-color)',
        cursor: onClick || link ? 'pointer' : 'default',
        ...style,
      }}
      className={className}
      onClick={onClick}
    >
      <Space direction="vertical">
        {icon && (
          <div
            style={{
              fontSize: 24,
              color: '#1890ff',
              marginBottom: 16,
            }}
          >
            {icon}
          </div>
        )}

        {title && (
          <Title level={4} style={{ margin: 0, marginBottom: 8 }}>
            {title}
          </Title>
        )}

        {description && (
          <Text type="secondary" style={{ fontSize: 14 }}>
            {description}
          </Text>
        )}

        {(onClick || link) && (
          <Text
            style={{
              color: '#1890ff',
              fontSize: 14,
              marginTop: 16,
              display: 'inline-block',
            }}
          >
            {linkText}
          </Text>
        )}
      </Space>
    </motion.div>
  );
};

export default Card;
