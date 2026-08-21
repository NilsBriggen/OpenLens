/**
 * Skeleton Loader Component for OpenLens
 * 
 * A customizable skeleton loading placeholder with various shapes and animations
 */

import React from 'react';
import { Skeleton, Space, Card, Typography } from 'antd';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface SkeletonLoaderProps {
  type?: 'text' | 'avatar' | 'paragraph' | 'title' | 'input' | 'button' | 'image' | 'card' | 'list' | 'table';
  size?: 'small' | 'default' | 'large';
  active?: boolean;
  loading?: boolean;
  rows?: number;
  width?: number | string | (number | string)[];
  height?: number | string;
  shape?: 'circle' | 'square' | 'round' | 'default';
  style?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  type = 'text',
  size = 'default',
  active = true,
  loading = true,
  rows = 1,
  width,
  height,
  shape = 'default',
  style = {},
  className = '',
  children,
}) => {
  // If not loading, render children
  if (!loading) {
    return <>{children}</>;
  }

  // Get size styles
  const getSize = () => {
    const sizes: Record<string, { text: number | string; avatar: number; input: number }> = {
      small: { text: 'small', avatar: 24, input: 'small' },
      default: { text: 'default', avatar: 32, input: 'default' },
      large: { text: 'large', avatar: 40, input: 'large' },
    };
    return sizes[size] || sizes.default;
  };

  const sizeInfo = getSize();

  // Get width array
  const getWidthArray = () => {
    if (Array.isArray(width)) return width;
    if (width !== undefined) return Array(rows).fill(width);
    return undefined;
  };

  // Render based on type
  switch (type) {
    case 'text':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton.Input
            active={active}
            size={sizeInfo.input as any}
            style={{ width: width || '100%', height, ...style }}
          />
        </motion.div>
      );

    case 'avatar':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton.Avatar
            active={active}
            size={sizeInfo.avatar}
            shape={shape as any}
            style={{ width: width || sizeInfo.avatar, height: height || sizeInfo.avatar, ...style }}
          />
        </motion.div>
      );

    case 'paragraph':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton
            active={active}
            paragraph={{ rows, width: getWidthArray() }}
            title={false}
          />
        </motion.div>
      );

    case 'title':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton
            active={active}
            title={{ width: width || '100%' }}
            paragraph={false}
          />
        </motion.div>
      );

    case 'input':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton.Input
            active={active}
            size={sizeInfo.input as any}
            style={{ width: width || '100%', height, ...style }}
          />
        </motion.div>
      );

    case 'button':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton.Button
            active={active}
            size={sizeInfo.input as any}
            shape={shape as any}
            style={{ width: width || 100, height, ...style }}
          />
        </motion.div>
      );

    case 'image':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton.Image
            active={active}
            style={{ width: width || '100%', height: height || 200, ...style }}
          />
        </motion.div>
      );

    case 'card':
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Card size="small">
            <Skeleton
              active={active}
              paragraph={{ rows: 3 }}
              title={{ width: '60%' }}
            />
          </Card>
        </motion.div>
      );

    case 'list':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {Array(rows).fill(0).map((_, index) => (
              <Skeleton
                key={index}
                active={active}
                avatar
                title={{ width: '40%' }}
                paragraph={{ rows: 1, width: '60%' }}
              />
            ))}
          </Space>
        </motion.div>
      );

    case 'table':
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {Array(rows).fill(0).map((_, index) => (
              <Skeleton
                key={index}
                active={active}
                paragraph={{ rows: 1 }}
                title={false}
              />
            ))}
          </Space>
        </motion.div>
      );

    default:
      return (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={style}
          className={className}
        >
          <Skeleton
            active={active}
            paragraph={{ rows, width: getWidthArray() }}
          />
        </motion.div>
      );
  }
};

// Page Skeleton Loader
interface PageSkeletonProps {
  layout?: 'dashboard' | 'list' | 'detail' | 'form' | 'custom';
  active?: boolean;
  loading?: boolean;
  children?: React.ReactNode;
}

export const PageSkeleton: React.FC<PageSkeletonProps> = ({
  layout = 'dashboard',
  active = true,
  loading = true,
  children,
}) => {
  if (!loading) {
    return <>{children}</>;
  }

  switch (layout) {
    case 'dashboard':
      return (
        <Space direction="vertical" style={{ width: '100%' }}>
          <SkeletonLoader type="title" width="30%" />
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            <Space>
              <SkeletonLoader type="card" />
              <SkeletonLoader type="card" />
              <SkeletonLoader type="card" />
              <SkeletonLoader type="card" />
            </Space>
          </Space>
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            <SkeletonLoader type="card" />
            <SkeletonLoader type="card" />
          </Space>
        </Space>
      );

    case 'list':
      return (
        <Space direction="vertical" style={{ width: '100%' }}>
          <SkeletonLoader type="title" width="40%" />
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            {Array(5).fill(0).map((_, index) => (
              <SkeletonLoader key={index} type="list" rows={1} />
            ))}
          </Space>
        </Space>
      );

    case 'detail':
      return (
        <Space direction="vertical" style={{ width: '100%' }}>
          <SkeletonLoader type="title" width="50%" />
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            <Space>
              <SkeletonLoader type="avatar" size="large" />
              <Space direction="vertical">
                <SkeletonLoader type="title" width="60%" />
                <SkeletonLoader type="text" width="40%" />
              </Space>
            </Space>
          </Space>
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            <SkeletonLoader type="paragraph" rows={3} />
          </Space>
        </Space>
      );

    case 'form':
      return (
        <Space direction="vertical" style={{ width: '100%' }}>
          <SkeletonLoader type="title" width="40%" />
          <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
            {Array(5).fill(0).map((_, index) => (
              <SkeletonLoader key={index} type="input" />
            ))}
            <Space style={{ marginTop: 16 }}>
              <SkeletonLoader type="button" />
              <SkeletonLoader type="button" />
            </Space>
          </Space>
        </Space>
      );

    case 'custom':
    default:
      return <>{children}</>;
  }
};

// Shimmer Effect Component
interface ShimmerProps {
  width?: number | string;
  height?: number | string;
  style?: React.CSSProperties;
  className?: string;
}

export const Shimmer: React.FC<ShimmerProps> = ({
  width = '100%',
  height = 20,
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      style={{
        width,
        height,
        background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s infinite',
        borderRadius: 4,
        ...style,
      }}
      className={className}
    />
  );
};

// Add CSS animation for shimmer
const ShimmerStyle = () => {
  return (
    <style>
      {`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}
    </style>
  );
};

// Add style to document head
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
  `;
  document.head.appendChild(style);
}

export default SkeletonLoader;
