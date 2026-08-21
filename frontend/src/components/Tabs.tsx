/**
 * Enhanced Tabs Component for OpenLens
 * 
 * A customizable tabs component with various styles and features
 */

import React, { useState } from 'react';
import { Tabs as AntTabs, Typography, Space, Button, Tooltip, Badge } from 'antd';
import { PlusOutlined, CloseOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface TabItem {
  key: string;
  label: React.ReactNode;
  children?: React.ReactNode;
  disabled?: boolean;
  closable?: boolean;
  icon?: React.ReactNode;
  count?: number;
  [key: string]: any;
}

interface TabsProps {
  items: TabItem[];
  activeKey?: string;
  onChange?: (key: string) => void;
  onAdd?: () => void;
  onRemove?: (key: string) => void;
  type?: 'line' | 'card' | 'editable-card';
  size?: 'small' | 'default' | 'large';
  position?: 'top' | 'right' | 'bottom' | 'left';
  tabPosition?: 'top' | 'right' | 'bottom' | 'left';
  centered?: boolean;
  addIcon?: React.ReactNode;
  showAdd?: boolean;
  showRemove?: boolean;
  animated?: boolean;
  destroyInactiveTabPane?: boolean;
  style?: React.CSSProperties;
  className?: string;
  tabBarStyle?: React.CSSProperties;
  tabBarGutter?: number;
  tabBarExtraContent?: React.ReactNode;
}

const Tabs: React.FC<TabsProps> = ({
  items = [],
  activeKey,
  onChange,
  onAdd,
  onRemove,
  type = 'line',
  size = 'default',
  position = 'top',
  tabPosition = 'top',
  centered = false,
  addIcon = <PlusOutlined />,
  showAdd = false,
  showRemove = false,
  animated = true,
  destroyInactiveTabPane = false,
  style = {},
  className = '',
  tabBarStyle = {},
  tabBarGutter,
  tabBarExtraContent,
}) => {
  const [internalActiveKey, setInternalActiveKey] = useState(
    activeKey || (items.length > 0 ? items[0].key : '')
  );

  // Sync active key
  React.useEffect(() => {
    if (activeKey !== undefined) {
      setInternalActiveKey(activeKey);
    }
  }, [activeKey]);

  // Handle tab change
  const handleTabChange = (key: string) => {
    setInternalActiveKey(key);
    if (onChange) {
      onChange(key);
    }
  };

  // Handle tab remove
  const handleTabRemove = (key: string) => {
    if (onRemove) {
      onRemove(key);
    }
  };

  // Handle add tab
  const handleAddTab = () => {
    if (onAdd) {
      onAdd();
    }
  };

  // Render tab label
  const renderTabLabel = (item: TabItem) => {
    const content = (
      <Space>
        {item.icon}
        {item.label}
        {item.count !== undefined && (
          <Badge count={item.count} size="small" />
        )}
      </Space>
    );

    if (showRemove && item.closable) {
      return (
        <Space>
          {content}
          <Tooltip title="Close">
            <Button
              type="text"
              icon={<CloseOutlined />}
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleTabRemove(item.key);
              }}
            />
          </Tooltip>
        </Space>
      );
    }

    return content;
  };

  // Build tab bar extra content
  const buildTabBarExtraContent = () => {
    if (tabBarExtraContent) return tabBarExtraContent;

    if (showAdd) {
      return (
        <Button
          type="text"
          icon={addIcon}
          onClick={handleAddTab}
          size={size}
        />
      );
    }

    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <AntTabs
        activeKey={internalActiveKey}
        onChange={handleTabChange}
        type={type}
        size={size}
        tabPosition={tabPosition}
        centered={centered}
        animated={animated}
        destroyInactiveTabPane={destroyInactiveTabPane}
        tabBarStyle={{
          margin: 0,
          padding: '8px 0',
          border: 'none',
          background: 'transparent',
          ...tabBarStyle,
        }}
        tabBarGutter={tabBarGutter}
        tabBarExtraContent={buildTabBarExtraContent()}
        items={items.map(item => ({
          key: item.key,
          label: renderTabLabel(item),
          children: item.children,
          disabled: item.disabled,
          closable: showRemove && item.closable,
        }))}
      />
    </motion.div>
  );
};

// VerticalTabs component
interface VerticalTabsProps extends Omit<TabsProps, 'tabPosition' | 'position'> {
  width?: number | string;
}

export const VerticalTabs: React.FC<VerticalTabsProps> = ({
  width = 200,
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: 16,
      }}
    >
      <div style={{ width }}>
        <Tabs
          {...props}
          tabPosition="left"
          type="line"
          style={{
            height: '100%',
          }}
        />
      </div>
      <div style={{ flex: 1 }}>
        {props.items.find(item => item.key === (props.activeKey || props.items[0]?.key))?.children}
      </div>
    </motion.div>
  );
};

// CardTabs component (tabs with card-like appearance)
interface CardTabsProps extends TabsProps {
  cardProps?: any;
}

export const CardTabs: React.FC<CardTabsProps> = ({
  cardProps = {},
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        background: 'var(--card-bg)',
        borderRadius: 12,
        border: '1px solid var(--border-color)',
        overflow: 'hidden',
        ...props.style,
      }}
      className={props.className}
    >
      <Tabs
        {...props}
        type="card"
        style={{
          padding: 16,
        }}
      />
    </motion.div>
  );
};

// SegmentedTabs component (segmented control-like tabs)
interface SegmentedTabsProps {
  items: TabItem[];
  activeKey?: string;
  onChange?: (key: string) => void;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const SegmentedTabs: React.FC<SegmentedTabsProps> = ({
  items = [],
  activeKey,
  onChange,
  size = 'default',
  style = {},
  className = '',
}) => {
  const [internalActiveKey, setInternalActiveKey] = useState(
    activeKey || (items.length > 0 ? items[0].key : '')
  );

  // Sync active key
  React.useEffect(() => {
    if (activeKey !== undefined) {
      setInternalActiveKey(activeKey);
    }
  }, [activeKey]);

  // Handle change
  const handleChange = (key: string) => {
    setInternalActiveKey(key);
    if (onChange) {
      onChange(key);
    }
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { padding: string; font: number }> = {
      small: { padding: '4px 8px', font: 12 },
      default: { padding: '8px 16px', font: 14 },
      large: { padding: '12px 24px', font: 16 },
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
        display: 'inline-flex',
        borderRadius: 8,
        background: 'var(--bg-color-secondary)',
        padding: 4,
        border: '1px solid var(--border-color)',
        ...style,
      }}
      className={className}
    >
      {items.map((item) => {
        const isActive = internalActiveKey === item.key;
        
        return (
          <motion.button
            key={item.key}
            type="button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => !item.disabled && handleChange(item.key)}
            disabled={item.disabled}
            style={{
              padding: sizeStyles.padding,
              fontSize: sizeStyles.font,
              background: isActive ? 'var(--card-bg)' : 'transparent',
              border: 'none',
              borderRadius: 6,
              color: isActive ? 'var(--text-color)' : 'var(--text-color-secondary)',
              cursor: item.disabled ? 'not-allowed' : 'pointer',
              boxShadow: isActive ? '0 1px 2px rgba(0, 0, 0, 0.1)' : 'none',
              transition: 'all 0.3s ease',
            }}
          >
            <Space>
              {item.icon}
              {item.label}
              {item.count !== undefined && (
                <Badge count={item.count} size="small" />
              )}
            </Space>
          </motion.button>
        );
      })}
    </motion.div>
  );
};

// ScrollableTabs component (tabs with scrollable overflow)
interface ScrollableTabsProps extends TabsProps {
  scrollable?: boolean;
  scrollButtons?: boolean;
}

export const ScrollableTabs: React.FC<ScrollableTabsProps> = ({
  scrollable = true,
  scrollButtons = true,
  ...props
}) => {
  const tabsRef = React.useRef<HTMLDivElement>(null);
  const [showLeftScroll, setShowLeftScroll] = useState(false);
  const [showRightScroll, setShowRightScroll] = useState(false);

  // Check scroll position
  React.useEffect(() => {
    const checkScroll = () => {
      if (tabsRef.current) {
        const { scrollLeft, scrollWidth, clientWidth } = tabsRef.current;
        setShowLeftScroll(scrollLeft > 0);
        setShowRightScroll(scrollLeft < scrollWidth - clientWidth);
      }
    };

    checkScroll();
    const currentRef = tabsRef.current;
    currentRef?.addEventListener('scroll', checkScroll);

    return () => {
      currentRef?.removeEventListener('scroll', checkScroll);
    };
  }, []);

  // Scroll left
  const scrollLeft = () => {
    if (tabsRef.current) {
      tabsRef.current.scrollBy({ left: -100, behavior: 'smooth' });
    }
  };

  // Scroll right
  const scrollRight = () => {
    if (tabsRef.current) {
      tabsRef.current.scrollBy({ left: 100, behavior: 'smooth' });
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'relative',
        ...props.style,
      }}
      className={props.className}
    >
      {scrollButtons && showLeftScroll && (
        <Button
          type="text"
          icon={<LeftOutlined />}
          onClick={scrollLeft}
          size="small"
          style={{
            position: 'absolute',
            left: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 1,
            background: 'var(--card-bg)',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
          }}
        />
      )}

      <div
        ref={tabsRef}
        style={{
          overflowX: scrollable ? 'auto' : 'visible',
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        <Tabs
          {...props}
          tabBarStyle={{
            ...props.tabBarStyle,
            flexWrap: 'nowrap',
            whiteSpace: 'nowrap',
          }}
        />
      </div>

      {scrollButtons && showRightScroll && (
        <Button
          type="text"
          icon={<RightOutlined />}
          onClick={scrollRight}
          size="small"
          style={{
            position: 'absolute',
            right: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            zIndex: 1,
            background: 'var(--card-bg)',
            boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
          }}
        />
      )}
    </motion.div>
  );
};

export default Tabs;
