/**
 * Status Badge Component for OpenLens
 * 
 * A customizable status badge with various styles and states
 */

import React from 'react';
import { Badge, Tag, Tooltip, Space, Typography } from 'antd';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface StatusBadgeProps {
  status: 'success' | 'error' | 'warning' | 'info' | 'processing' | 'default' | string;
  text?: string;
  size?: 'small' | 'default' | 'large';
  type?: 'badge' | 'tag' | 'dot' | 'text';
  showText?: boolean;
  tooltip?: string;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  count?: number;
  overflowCount?: number;
  color?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status = 'default',
  text,
  size = 'default',
  type = 'badge',
  showText = true,
  tooltip,
  icon,
  style = {},
  className = '',
  count,
  overflowCount = 99,
  color,
}) => {
  // Get color for status
  const getColor = () => {
    if (color) return color;
    
    const colors: Record<string, string> = {
      success: '#52c41a',
      error: '#f5222d',
      warning: '#faad14',
      info: '#1890ff',
      processing: '#1890ff',
      default: '#d9d9d9',
    };
    return colors[status] || colors.default;
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { text: React.CSSProperties; dot: React.CSSProperties }> = {
      small: { text: { fontSize: 10 }, dot: { width: 6, height: 6 } },
      default: { text: { fontSize: 12 }, dot: { width: 8, height: 8 } },
      large: { text: { fontSize: 14 }, dot: { width: 10, height: 10 } },
    };
    return sizes[size] || sizes.default;
  };

  // Render based on type
  switch (type) {
    case 'badge':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Badge
            status={status as any}
            text={showText ? text : undefined}
            color={getColor()}
            size={size === 'large' ? 'default' : size}
            style={style}
            className={className}
            count={count}
            overflowCount={overflowCount}
          />
        </motion.div>
      );

    case 'tag':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Tooltip title={tooltip}>
            <Tag
              color={getColor()}
              style={{ ...getSizeStyles().text, ...style }}
              className={className}
            >
              <Space>
                {icon}
                {showText && (text || status)}
              </Space>
            </Tag>
          </Tooltip>
        </motion.div>
      );

    case 'dot':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
          style={{ display: 'inline-flex', alignItems: 'center', gap: 8, ...style }}
          className={className}
        >
          <div
            style={{
              width: getSizeStyles().dot.width,
              height: getSizeStyles().dot.height,
              borderRadius: '50%',
              background: getColor(),
            }}
          />
          {showText && (
            <Text style={{ fontSize: getSizeStyles().text.fontSize }}>
              {text || status}
            </Text>
          )}
        </motion.div>
      );

    case 'text':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Text
            type={status as any}
            style={{ color: getColor(), ...getSizeStyles().text, ...style }}
            className={className}
          >
            {showText ? text || status : ''}
          </Text>
        </motion.div>
      );

    default:
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Badge
            status={status as any}
            text={showText ? text : undefined}
            color={getColor()}
            size={size === 'large' ? 'default' : size}
            style={style}
            className={className}
          />
        </motion.div>
      );
  }
};

// Status Indicator Component
interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'busy' | 'away' | 'invisible' | string;
  size?: 'small' | 'default' | 'large';
  showLabel?: boolean;
  labelPosition?: 'top' | 'bottom' | 'left' | 'right';
  style?: React.CSSProperties;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status = 'online',
  size = 'default',
  showLabel = false,
  labelPosition = 'right',
  style = {},
}) => {
  // Get status color and label
  const getStatusInfo = () => {
    const statusMap: Record<string, { color: string; label: string }> = {
      online: { color: '#52c41a', label: 'Online' },
      offline: { color: '#f5222d', label: 'Offline' },
      busy: { color: '#faad14', label: 'Busy' },
      away: { color: '#faad14', label: 'Away' },
      invisible: { color: '#d9d9d9', label: 'Invisible' },
    };
    return statusMap[status] || statusMap.online;
  };

  const { color, label } = getStatusInfo();

  // Get size
  const getSize = () => {
    const sizes: Record<string, { indicator: number; label: number }> = {
      small: { indicator: 8, label: 10 },
      default: { indicator: 12, label: 12 },
      large: { indicator: 16, label: 14 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeInfo = getSize();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        ...style,
      }}
    >
      <div
        style={{
          width: sizeInfo.indicator,
          height: sizeInfo.indicator,
          borderRadius: '50%',
          background: color,
          boxShadow: `0 0 0 2px var(--card-bg), 0 0 0 4px ${color}`,
        }}
      />
      {showLabel && (
        <Text style={{ fontSize: sizeInfo.label }}>
          {label}
        </Text>
      )}
    </motion.div>
  );
};

// Progress Status Badge
interface ProgressStatusBadgeProps {
  progress: number;
  status?: 'success' | 'error' | 'warning' | 'info' | 'processing';
  size?: 'small' | 'default' | 'large';
  showText?: boolean;
  text?: string;
  style?: React.CSSProperties;
}

export const ProgressStatusBadge: React.FC<ProgressStatusBadgeProps> = ({
  progress = 0,
  status,
  size = 'default',
  showText = true,
  text,
  style = {},
}) => {
  const getColor = () => {
    if (status) {
      const colors: Record<string, string> = {
        success: '#52c41a',
        error: '#f5222d',
        warning: '#faad14',
        info: '#1890ff',
        processing: '#1890ff',
      };
      return colors[status] || '#1890ff';
    }
    
    if (progress >= 100) return '#52c41a';
    if (progress >= 75) return '#52c41a';
    if (progress >= 50) return '#faad14';
    if (progress >= 25) return '#fa8c16';
    return '#f5222d';
  };

  const color = getColor();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
    >
      <Space>
        <div
          style={{
            width: 30,
            height: 30,
            borderRadius: '50%',
            background: 'conic-gradient(' + color + ' 0deg, ' + color + ' ' + (progress * 3.6) + 'deg, #d9d9d9 ' + (progress * 3.6) + 'deg, #d9d9d9 360deg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Text style={{ fontSize: 12, color: '#fff', fontWeight: 'bold' }}>
            {progress}%
          </Text>
        </div>
        {showText && (
          <Text style={{ fontSize: 12 }}>
            {text || `${progress}% complete`}
          </Text>
        )}
      </Space>
    </motion.div>
  );
};

export default StatusBadge;
