/**
 * Timeline Component for OpenLens
 * 
 * A customizable timeline component for displaying chronological events
 */

import React from 'react';
import { Timeline as AntTimeline, Typography, Space, Card, Tag, Avatar, Button } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined, WarningOutlined, PlusOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text, Paragraph } = Typography;

interface TimelineItem {
  key?: string;
  label?: React.ReactNode;
  children?: React.ReactNode;
  color?: string;
  dot?: React.ReactNode;
  position?: 'left' | 'right';
  pending?: boolean;
  pendingDot?: React.ReactNode;
  [key: string]: any;
}

interface TimelineProps {
  items: TimelineItem[];
  mode?: 'left' | 'alternate' | 'right' | 'top' | 'bottom';
  pending?: boolean;
  pendingDot?: React.ReactNode;
  reverse?: boolean;
  style?: React.CSSProperties;
  className?: string;
  itemStyle?: React.CSSProperties;
  animated?: boolean;
}

const Timeline: React.FC<TimelineProps> = ({
  items = [],
  mode = 'left',
  pending = false,
  pendingDot,
  reverse = false,
  style = {},
  className = '',
  itemStyle = {},
  animated = true,
}) => {
  // Get color for item
  const getColor = (item: TimelineItem) => {
    if (item.color) return item.color;
    if (item.status === 'success') return '#52c41a';
    if (item.status === 'error') return '#f5222d';
    if (item.status === 'warning') return '#faad14';
    if (item.status === 'processing') return '#1890ff';
    return '#d9d9d9';
  };

  // Get icon for item
  const getIcon = (item: TimelineItem) => {
    if (item.icon) return item.icon;
    if (item.status === 'success') return <CheckCircleOutlined />;
    if (item.status === 'error') return <CloseCircleOutlined />;
    if (item.status === 'warning') return <WarningOutlined />;
    return <ClockCircleOutlined />;
  };

  // Build timeline items
  const buildItems = () => {
    return items.map((item, index) => {
      const color = getColor(item);
      const icon = getIcon(item);

      return {
        key: item.key || index,
        label: item.label,
        children: (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            style={itemStyle}
          >
            {item.children}
          </motion.div>
        ),
        color,
        dot: item.dot || (
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: '50%',
              background: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 10,
              color: '#fff',
            }}
          >
            {icon}
          </div>
        ),
        position: item.position,
        pending: item.pending || pending,
        pendingDot: item.pendingDot || pendingDot,
      };
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <AntTimeline
        items={buildItems() as any}
        mode={mode === 'top' || mode === 'bottom' ? 'alternate' : mode}
        pending={pending}
        pendingDot={pendingDot}
        reverse={reverse}
      />
    </motion.div>
  );
};

// EventTimeline component (timeline with event cards)
interface EventTimelineItem {
  key?: string;
  title: string;
  timestamp: string | Date;
  description?: string;
  status?: 'success' | 'error' | 'warning' | 'info' | 'default';
  icon?: React.ReactNode;
  color?: string;
  tags?: string[];
  actions?: React.ReactNode[];
  [key: string]: any;
}

interface EventTimelineProps {
  items: EventTimelineItem[];
  mode?: 'left' | 'alternate' | 'right';
  showTimestamp?: boolean;
  timestampFormat?: string;
  showStatus?: boolean;
  showTags?: boolean;
  showActions?: boolean;
  animated?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const EventTimeline: React.FC<EventTimelineProps> = ({
  items = [],
  mode = 'left',
  showTimestamp = true,
  timestampFormat = 'MMM D, YYYY h:mm A',
  showStatus = true,
  showTags = true,
  showActions = true,
  animated = true,
  style = {},
  className = '',
}) => {
  // Format timestamp
  const formatTimestamp = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Get status color
  const getStatusColor = (status?: string) => {
    const colors: Record<string, string> = {
      success: '#52c41a',
      error: '#f5222d',
      warning: '#faad14',
      info: '#1890ff',
      default: '#d9d9d9',
    };
    return colors[status || 'default'];
  };

  // Get status icon
  const getStatusIcon = (status?: string) => {
    const icons: Record<string, React.ReactNode> = {
      success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      error: <CloseCircleOutlined style={{ color: '#f5222d' }} />,
      warning: <WarningOutlined style={{ color: '#faad14' }} />,
      info: <ClockCircleOutlined style={{ color: '#1890ff' }} />,
      default: <ClockCircleOutlined style={{ color: '#d9d9d9' }} />,
    };
    return icons[status || 'default'];
  };

  // Build timeline items
  const buildItems = () => {
    return items.map((item, index) => {
      const color = getStatusColor(item.status);
      const icon = item.icon || getStatusIcon(item.status);

      return {
        key: item.key || index,
        label: showTimestamp && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatTimestamp(item.timestamp)}
          </Text>
        ),
        children: (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card
              size="small"
              style={{
                borderLeft: `4px solid ${color}`,
                borderRadius: 0,
              }}
              bodyStyle={{ padding: 16 }}
            >
              <Space direction="vertical">
                <Space>
                  {icon}
                  <Title level={5} style={{ margin: 0 }}>
                    {item.title}
                  </Title>
                  {showStatus && item.status && (
                    <Tag color={color} style={{ margin: 0 }}>
                      {item.status}
                    </Tag>
                  )}
                </Space>

                {item.description && (
                  <Paragraph style={{ margin: '8px 0 0 0', fontSize: 14 }}>
                    {item.description}
                  </Paragraph>
                )}

                {showTags && item.tags && item.tags.length > 0 && (
                  <Space wrap style={{ marginTop: 8 }}>
                    {item.tags.map((tag, tagIndex) => (
                      <Tag key={tagIndex} color="blue" style={{ margin: 0 }}>
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                )}

                {showActions && item.actions && item.actions.length > 0 && (
                  <Space style={{ marginTop: 12 }}>
                    {item.actions}
                  </Space>
                )}
              </Space>
            </Card>
          </motion.div>
        ),
        color,
        dot: (
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              color: '#fff',
            }}
          >
            {icon}
          </div>
        ),
      };
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Timeline
        items={buildItems() as any}
        mode={mode}
        animated={animated}
      />
    </motion.div>
  );
};

// ActivityTimeline component (timeline for user activities)
interface ActivityTimelineItem {
  key?: string;
  type: 'create' | 'update' | 'delete' | 'login' | 'logout' | 'view' | 'export' | string;
  title: string;
  timestamp: string | Date;
  user?: {
    name?: string;
    avatar?: string;
    color?: string;
  };
  description?: string;
  metadata?: Record<string, any>;
  [key: string]: any;
}

interface ActivityTimelineProps {
  items: ActivityTimelineItem[];
  showUser?: boolean;
  showTimestamp?: boolean;
  timestampFormat?: string;
  animated?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  items = [],
  showUser = true,
  showTimestamp = true,
  timestampFormat = 'MMM D, YYYY h:mm A',
  animated = true,
  style = {},
  className = '',
}) => {
  // Get activity type info
  const getActivityInfo = (type: string) => {
    const info: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
      create: { color: '#52c41a', icon: '+', label: 'Created' },
      update: { color: '#1890ff', icon: '✏️', label: 'Updated' },
      delete: { color: '#f5222d', icon: '🗑️', label: 'Deleted' },
      login: { color: '#52c41a', icon: '🔑', label: 'Logged in' },
      logout: { color: '#f5222d', icon: '🚪', label: 'Logged out' },
      view: { color: '#faad14', icon: '👁️', label: 'Viewed' },
      export: { color: '#722ed1', icon: '📤', label: 'Exported' },
    };
    return info[type] || { color: '#d9d9d9', icon: 'ℹ️', label: type };
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Build timeline items
  const buildItems = () => {
    return items.map((item, index) => {
      const { color, icon, label } = getActivityInfo(item.type);

      return {
        key: item.key || index,
        label: showTimestamp && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatTimestamp(item.timestamp)}
          </Text>
        ),
        children: (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card
              size="small"
              style={{
                borderLeft: `4px solid ${color}`,
                borderRadius: 0,
              }}
              bodyStyle={{ padding: 16 }}
            >
              <Space direction="vertical">
                <Space>
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      background: color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 16,
                      marginRight: 8,
                    }}
                  >
                    {icon}
                  </div>
                  
                  <Space direction="vertical">
                    <Title level={5} style={{ margin: 0 }}>
                      {label} {item.title}
                    </Title>
                    
                    {showUser && item.user && (
                      <Space>
                        {item.user.avatar ? (
                          <img
                            src={item.user.avatar}
                            alt={item.user.name}
                            style={{
                              width: 20,
                              height: 20,
                              borderRadius: '50%',
                              marginRight: 4,
                            }}
                          />
                        ) : (
                          <Avatar
                            size={20}
                            style={{
                              background: item.user.color || '#1890ff',
                              marginRight: 4,
                            }}
                          >
                            {item.user.name?.charAt(0).toUpperCase()}
                          </Avatar>
                        )}
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {item.user.name}
                        </Text>
                      </Space>
                    )}
                  </Space>
                </Space>

                {item.description && (
                  <Paragraph style={{ margin: '8px 0 0 0', fontSize: 14 }}>
                    {item.description}
                  </Paragraph>
                )}

                {item.metadata && Object.keys(item.metadata).length > 0 && (
                  <Space wrap style={{ marginTop: 8 }}>
                    {Object.entries(item.metadata).map(([key, value]) => (
                      <Tag key={key} color="blue" style={{ margin: 0, fontSize: 12 }}>
                        {key}: {String(value)}
                      </Tag>
                    ))}
                  </Space>
                )}
              </Space>
            </Card>
          </motion.div>
        ),
        color,
        dot: (
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              color: '#fff',
            }}
          >
            {icon}
          </div>
        ),
      };
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Timeline
        items={buildItems() as any}
        mode="left"
        animated={animated}
      />
    </motion.div>
  );
};

// GitTimeline component (timeline for git commits)
interface GitCommit {
  key?: string;
  hash: string;
  message: string;
  author: {
    name: string;
    email?: string;
    avatar?: string;
  };
  timestamp: string | Date;
  tags?: string[];
  [key: string]: any;
}

interface GitTimelineProps {
  commits: GitCommit[];
  showHash?: boolean;
  hashLength?: number;
  showAuthor?: boolean;
  showTimestamp?: boolean;
  animated?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const GitTimeline: React.FC<GitTimelineProps> = ({
  commits = [],
  showHash = true,
  hashLength = 7,
  showAuthor = true,
  showTimestamp = true,
  animated = true,
  style = {},
  className = '',
}) => {
  // Format timestamp
  const formatTimestamp = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Build timeline items
  const buildItems = () => {
    return commits.map((commit, index) => {
      return {
        key: commit.key || commit.hash,
        label: showTimestamp && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatTimestamp(commit.timestamp)}
          </Text>
        ),
        children: (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card
              size="small"
              style={{
                borderLeft: `4px solid #1890ff`,
                borderRadius: 0,
              }}
              bodyStyle={{ padding: 16 }}
            >
              <Space direction="vertical">
                <Space>
                  {showAuthor && commit.author && (
                    <Space>
                      {commit.author.avatar ? (
                        <img
                          src={commit.author.avatar}
                          alt={commit.author.name}
                          style={{
                            width: 24,
                            height: 24,
                            borderRadius: '50%',
                            marginRight: 8,
                          }}
                        />
                      ) : (
                        <Avatar
                          size={24}
                          style={{
                            background: '#1890ff',
                            marginRight: 8,
                          }}
                        >
                          {commit.author.name.charAt(0).toUpperCase()}
                        </Avatar>
                      )}
                      <Space direction="vertical">
                        <Title level={5} style={{ margin: 0 }}>
                          {commit.author.name}
                        </Title>
                        {showHash && (
                          <Text code style={{ fontSize: 12 }}>
                            {commit.hash.substring(0, hashLength)}
                          </Text>
                        )}
                      </Space>
                    </Space>
                  )}

                  {!showAuthor && showHash && (
                    <Text code style={{ fontSize: 14 }}>
                      {commit.hash.substring(0, hashLength)}
                    </Text>
                  )}
                </Space>

                <Paragraph style={{ margin: '8px 0 0 0', fontSize: 14 }}>
                  {commit.message}
                </Paragraph>

                {commit.tags && commit.tags.length > 0 && (
                  <Space wrap style={{ marginTop: 8 }}>
                    {commit.tags.map((tag, tagIndex) => (
                      <Tag key={tagIndex} color="blue" style={{ margin: 0 }}>
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                )}
              </Space>
            </Card>
          </motion.div>
        ),
        color: '#1890ff',
        dot: (
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: '#1890ff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              color: '#fff',
            }}
          >
            <span style={{ fontWeight: 'bold' }}>G</span>
          </div>
        ),
      };
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Timeline
        items={buildItems() as any}
        mode="left"
        animated={animated}
      />
    </motion.div>
  );
};

// HistoryTimeline component (generic history timeline)
interface HistoryItem {
  key?: string;
  title: string;
  timestamp: string | Date;
  description?: string;
  type?: string;
  icon?: React.ReactNode;
  color?: string;
  [key: string]: any;
}

interface HistoryTimelineProps {
  items: HistoryItem[];
  title?: string;
  emptyText?: string;
  showTimestamp?: boolean;
  timestampFormat?: string;
  animated?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const HistoryTimeline: React.FC<HistoryTimelineProps> = ({
  items = [],
  title,
  emptyText = 'No history available',
  showTimestamp = true,
  timestampFormat = 'MMM D, YYYY h:mm A',
  animated = true,
  style = {},
  className = '',
}) => {
  // Format timestamp
  const formatTimestamp = (timestamp: string | Date) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  // Build timeline items
  const buildItems = () => {
    return items.map((item, index) => {
      const color = item.color || '#1890ff';
      const icon = item.icon || <ClockCircleOutlined />;

      return {
        key: item.key || index,
        label: showTimestamp && (
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatTimestamp(item.timestamp)}
          </Text>
        ),
        children: (
          <motion.div
            initial={animated ? { opacity: 0, y: 20 } : { opacity: 1, y: 0 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
          >
            <Card
              size="small"
              style={{
                borderLeft: `4px solid ${color}`,
                borderRadius: 0,
              }}
              bodyStyle={{ padding: 16 }}
            >
              <Space direction="vertical">
                <Space>
                  <div
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      background: color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: 12,
                      color: '#fff',
                      marginRight: 8,
                    }}
                  >
                    {icon}
                  </div>
                  <Title level={5} style={{ margin: 0 }}>
                    {item.title}
                  </Title>
                  {item.type && (
                    <Tag color={color} style={{ margin: 0 }}>
                      {item.type}
                    </Tag>
                  )}
                </Space>

                {item.description && (
                  <Paragraph style={{ margin: '8px 0 0 0', fontSize: 14 }}>
                    {item.description}
                  </Paragraph>
                )}
              </Space>
            </Card>
          </motion.div>
        ),
        color,
        dot: (
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 12,
              color: '#fff',
            }}
          >
            {icon}
          </div>
        ),
      };
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      {title && (
        <Title level={4} style={{ marginBottom: 16 }}>
          {title}
        </Title>
      )}

      {items.length === 0 ? (
        <Text type="secondary" style={{ textAlign: 'center', display: 'block', padding: 24 }}>
          {emptyText}
        </Text>
      ) : (
        <Timeline
          items={buildItems() as any}
          mode="left"
          animated={animated}
        />
      )}
    </motion.div>
  );
};

export default Timeline;
