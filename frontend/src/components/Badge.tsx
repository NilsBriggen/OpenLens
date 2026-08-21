/**
 * Badge Component for OpenLens
 * 
 * A customizable badge component with various styles and positions
 */

import React from 'react';
import { Badge as AntBadge, Typography, Space, Tooltip } from 'antd';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface BadgeProps {
  count?: React.ReactNode;
  overflowCount?: number;
  showZero?: boolean;
  status?: 'success' | 'processing' | 'default' | 'error' | 'warning';
  color?: string;
  text?: string;
  title?: string;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
  dot?: boolean;
  offset?: [number, number];
  position?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight' | 'top' | 'bottom' | 'left' | 'right';
  tooltip?: string;
  type?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
  shape?: 'circle' | 'square' | 'round';
  onClick?: () => void;
}

const Badge: React.FC<BadgeProps> = ({
  count,
  overflowCount = 99,
  showZero = false,
  status,
  color,
  text,
  title,
  size = 'default',
  style = {},
  className = '',
  children,
  dot = false,
  offset,
  position,
  tooltip,
  type = 'default',
  shape = 'circle',
  onClick,
}) => {
  // Get color for type
  const getColor = () => {
    if (color) return color;
    
    const colors: Record<string, string> = {
      default: '#d9d9d9',
      primary: '#1890ff',
      success: '#52c41a',
      warning: '#faad14',
      error: '#f5222d',
      info: '#1890ff',
    };
    return colors[type] || colors.default;
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { text: number; dot: number; badge: number }> = {
      small: { text: 10, dot: 6, badge: 16 },
      default: { text: 12, dot: 8, badge: 20 },
      large: { text: 14, dot: 10, badge: 24 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get shape styles
  const getShapeStyles = () => {
    switch (shape) {
      case 'circle':
        return { borderRadius: '50%' };
      case 'round':
        return { borderRadius: 4 };
      case 'square':
      default:
        return { borderRadius: 0 };
    }
  };

  // Build badge content
  const buildBadgeContent = () => {
    // If dot only
    if (dot && !count && !text) {
      return (
        <div
          style={{
            width: sizeStyles.dot,
            height: sizeStyles.dot,
            background: getColor(),
            ...getShapeStyles(),
            // After the spread: a dot is always a circle, whatever the shape
            // helper returned (the earlier borderRadius was overwritten).
            borderRadius: '50%',
          }}
        />
      );
    }

    // If count or text
    const displayText = count !== undefined ? count : text;
    
    return (
      <div
        style={{
          padding: '0 4px',
          fontSize: sizeStyles.text,
          lineHeight: 1,
          color: type === 'default' || type === 'primary' ? '#fff' : '#fff',
          background: getColor(),
          ...getShapeStyles(),
        }}
      >
        {displayText}
      </div>
    );
  };

  // If no children, render standalone badge
  if (!children) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
        style={style}
        className={className}
        onClick={onClick}
      >
        <Tooltip title={tooltip || title}>
          <span>{buildBadgeContent()}</span>
        </Tooltip>
      </motion.div>
    );
  }

  // Render with children
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <AntBadge
        count={count}
        overflowCount={overflowCount}
        showZero={showZero}
        status={status}
        color={color}
        title={title}
        size={size === 'large' ? 'default' : size}
        offset={offset}
        style={{
          ...getShapeStyles(),
        }}
      >
        {children}
      </AntBadge>
    </motion.div>
  );
};

// Notification Badge (for notifications)
interface NotificationBadgeProps {
  count?: number;
  max?: number;
  showZero?: boolean;
  children?: React.ReactNode;
  position?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  color?: string;
  background?: string;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({
  count = 0,
  max = 99,
  showZero = false,
  children,
  position = 'topRight',
  color = '#fff',
  background = '#f5222d',
  size = 'default',
  style = {},
  className = '',
  onClick,
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { text: number; badge: number }> = {
      small: { text: 10, badge: 16 },
      default: { text: 12, badge: 20 },
      large: { text: 14, badge: 24 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get display count
  const displayCount = count > max ? `${max}+` : count;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
      className={className}
      onClick={onClick}
    >
      {children}
      
      {(count > 0 || showZero) && (
        <div
          style={{
            position: 'absolute',
            top: position.includes('top') ? -4 : 'auto',
            bottom: position.includes('bottom') ? -4 : 'auto',
            left: position.includes('left') ? -4 : 'auto',
            right: position.includes('right') ? -4 : 'auto',
            minWidth: sizeStyles.badge,
            height: sizeStyles.badge,
            padding: '0 4px',
            fontSize: sizeStyles.text,
            lineHeight: 1,
            color,
            background,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {displayCount}
        </div>
      )}
    </motion.div>
  );
};

// Status Badge (for status indicators)
interface StatusBadgeProps {
  status: 'success' | 'error' | 'warning' | 'info' | 'processing' | 'default' | string;
  text?: string;
  size?: 'small' | 'default' | 'large';
  dot?: boolean;
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status = 'default',
  text,
  size = 'default',
  dot = true,
  style = {},
  className = '',
  onClick,
}) => {
  // Get color for status
  const getColor = () => {
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
    const sizes: Record<string, { text: number; dot: number }> = {
      small: { text: 10, dot: 6 },
      default: { text: 12, dot: 8 },
      large: { text: 14, dot: 10 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

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
      className={className}
      onClick={onClick}
    >
      {dot && (
        <div
          style={{
            width: sizeStyles.dot,
            height: sizeStyles.dot,
            borderRadius: '50%',
            background: getColor(),
          }}
        />
      )}
      
      {text && (
        <Text style={{ fontSize: sizeStyles.text, color: getColor() }}>
          {text}
        </Text>
      )}
    </motion.div>
  );
};

// Count Badge (for displaying counts)
interface CountBadgeProps {
  count: number;
  max?: number;
  color?: string;
  background?: string;
  size?: 'small' | 'default' | 'large';
  shape?: 'circle' | 'square' | 'round';
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
}

export const CountBadge: React.FC<CountBadgeProps> = ({
  count,
  max,
  color = '#fff',
  background = '#1890ff',
  size = 'default',
  shape = 'circle',
  style = {},
  className = '',
  onClick,
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { text: number; badge: number }> = {
      small: { text: 10, badge: 16 },
      default: { text: 12, badge: 20 },
      large: { text: 14, badge: 24 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get shape styles
  const getShapeStyles = () => {
    switch (shape) {
      case 'circle':
        return { borderRadius: '50%' };
      case 'round':
        return { borderRadius: 4 };
      case 'square':
      default:
        return { borderRadius: 0 };
    }
  };

  // Get display count
  const displayCount = max && count > max ? `${max}+` : count;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        minWidth: sizeStyles.badge,
        height: sizeStyles.badge,
        padding: '0 4px',
        fontSize: sizeStyles.text,
        lineHeight: 1,
        color,
        background,
        ...getShapeStyles(),
        ...style,
      }}
      className={className}
      onClick={onClick}
    >
      {displayCount}
    </motion.div>
  );
};

// Pill Badge (for pill-shaped badges)
interface PillBadgeProps {
  text: string;
  color?: string;
  background?: string;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
}

export const PillBadge: React.FC<PillBadgeProps> = ({
  text,
  color = '#fff',
  background = '#1890ff',
  size = 'default',
  style = {},
  className = '',
  onClick,
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { text: number; padding: string }> = {
      small: { text: 10, padding: '2px 6px' },
      default: { text: 12, padding: '4px 8px' },
      large: { text: 14, padding: '6px 12px' },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={{
        display: 'inline-block',
        padding: sizeStyles.padding,
        fontSize: sizeStyles.text,
        lineHeight: 1,
        color,
        background,
        borderRadius: 20,
        ...style,
      }}
      className={className}
      onClick={onClick}
    >
      {text}
    </motion.div>
  );
};

export default Badge;
