/**
 * Progress Bar Component for OpenLens
 * 
 * A customizable progress bar with various styles and animations
 */

import React from 'react';
import { Progress, Typography, Space, Tooltip } from 'antd';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface ProgressBarProps {
  percent: number;
  size?: 'small' | 'default' | 'large';
  type?: 'line' | 'circle' | 'dashboard';
  status?: 'success' | 'exception' | 'normal' | 'active';
  showInfo?: boolean;
  format?: (percent: number) => string;
  strokeColor?: string | { from: string; to: string };
  strokeLinecap?: 'round' | 'butt' | 'square';
  strokeWidth?: number;
  trailColor?: string;
  width?: number | string;
  gapDegree?: number;
  gapPosition?: 'top' | 'bottom' | 'left' | 'right';
  style?: React.CSSProperties;
  animated?: boolean;
  animationDuration?: number;
  label?: string;
  tooltip?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  percent = 0,
  size = 'default',
  type = 'line',
  status,
  showInfo = true,
  format,
  strokeColor,
  strokeLinecap = 'round',
  strokeWidth,
  trailColor = '#f0f0f0',
  width,
  gapDegree,
  gapPosition,
  style = {},
  animated = true,
  animationDuration = 1,
  label,
  tooltip,
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { line: number; circle: number }> = {
      small: { line: 6, circle: 60 },
      default: { line: 8, circle: 80 },
      large: { line: 12, circle: 100 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get stroke width
  const getStrokeWidth = () => {
    if (strokeWidth !== undefined) return strokeWidth;
    return type === 'line' ? sizeStyles.line : sizeStyles.circle / 10;
  };

  // Get width
  const getWidth = () => {
    if (width !== undefined) return width;
    return type === 'line' ? '100%' : sizeStyles.circle;
  };

  // Custom format function
  const formatPercent = format || ((percent) => `${percent}%`);

  // Render based on type
  switch (type) {
    case 'circle':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
        >
          <Tooltip title={tooltip}>
            <Progress
              type="circle"
              percent={percent}
              size={getWidth() as number}
              status={status}
              showInfo={showInfo}
              format={formatPercent}
              strokeColor={strokeColor}
              strokeLinecap={strokeLinecap}
              strokeWidth={getStrokeWidth()}
              trailColor={trailColor}
              gapDegree={gapDegree}
              gapPosition={gapPosition}
            />
          </Tooltip>
          {label && (
            <Text style={{ display: 'block', marginTop: 8, textAlign: 'center' }}>
              {label}
            </Text>
          )}
        </motion.div>
      );

    case 'dashboard':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
        >
          <Tooltip title={tooltip}>
            <Progress
              type="dashboard"
              percent={percent}
              size={getWidth() as number}
              status={status}
              showInfo={showInfo}
              format={formatPercent}
              strokeColor={strokeColor}
              strokeLinecap={strokeLinecap}
              strokeWidth={getStrokeWidth()}
              trailColor={trailColor}
              gapDegree={gapDegree}
              gapPosition={gapPosition}
            />
          </Tooltip>
          {label && (
            <Text style={{ display: 'block', marginTop: 8, textAlign: 'center' }}>
              {label}
            </Text>
          )}
        </motion.div>
      );

    case 'line':
    default:
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {label && (
              <Text style={{ fontSize: 12, marginBottom: 4 }}>
                {label}
              </Text>
            )}
            <Tooltip title={tooltip}>
              <Progress
                percent={percent}
                size={getWidth()}
                status={status}
                showInfo={showInfo}
                format={formatPercent}
                strokeColor={strokeColor}
                strokeLinecap={strokeLinecap}
                strokeWidth={getStrokeWidth()}
                trailColor={trailColor}
              />
            </Tooltip>
          </Space>
        </motion.div>
      );
  }
};

// Animated Progress Bar
interface AnimatedProgressBarProps extends ProgressBarProps {
  animationType?: 'pulse' | 'stripes' | 'gradient';
}

export const AnimatedProgressBar: React.FC<AnimatedProgressBarProps> = ({
  animationType = 'gradient',
  ...props
}) => {
  const getStrokeColor = () => {
    if (props.strokeColor) return props.strokeColor;
    
    switch (animationType) {
      case 'pulse':
        return { from: '#1890ff', to: '#52c41a' };
      case 'stripes':
        return { from: '#1890ff', to: '#1890ff' };
      case 'gradient':
      default:
        return { from: '#1890ff', to: '#722ed1' };
    }
  };

  return (
    <ProgressBar
      {...props}
      strokeColor={getStrokeColor()}
      animated={true}
    />
  );
};

// Progress Ring
interface ProgressRingProps {
  percent: number;
  size?: number;
  strokeWidth?: number;
  strokeColor?: string;
  trailColor?: string;
  text?: string;
  format?: (percent: number) => string;
  style?: React.CSSProperties;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  percent = 0,
  size = 80,
  strokeWidth = 8,
  strokeColor = '#1890ff',
  trailColor = '#f0f0f0',
  text,
  format,
  style = {},
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percent / 100) * circumference;

  const formatPercent = format || ((percent) => `${percent}%`);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        width: size,
        height: size,
        position: 'relative',
        ...style,
      }}
    >
      <svg
        width={size}
        height={size}
        style={{ transform: 'rotate(-90deg)' }}
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={trailColor}
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinejoin="round"
        />
      </svg>
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}
      >
        <Text strong style={{ fontSize: size / 4 }}>
          {formatPercent(percent)}
        </Text>
        {text && (
          <Text style={{ fontSize: size / 8, display: 'block' }}>
            {text}
          </Text>
        )}
      </div>
    </motion.div>
  );
};

// Multi-color Progress Bar
interface MultiColorProgressBarProps {
  sections: { percent: number; color: string; label?: string }[];
  size?: 'small' | 'default' | 'large';
  height?: number;
  style?: React.CSSProperties;
}

export const MultiColorProgressBar: React.FC<MultiColorProgressBarProps> = ({
  sections = [],
  size = 'default',
  height,
  style = {},
}) => {
  const getHeight = () => {
    const heights: Record<string, number> = {
      small: 6,
      default: 8,
      large: 12,
    };
    return height || heights[size] || heights.default;
  };

  const totalPercent = sections.reduce((sum, section) => sum + section.percent, 0);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        width: '100%',
        height: getHeight(),
        background: '#f0f0f0',
        borderRadius: 4,
        overflow: 'hidden',
        display: 'flex',
        ...style,
      }}
    >
      {sections.map((section, index) => (
        <div
          key={index}
          style={{
            width: `${(section.percent / totalPercent) * 100}%`,
            background: section.color,
            height: '100%',
          }}
          title={section.label}
        />
      ))}
    </motion.div>
  );
};

export default ProgressBar;
