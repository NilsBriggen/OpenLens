/**
 * Accordion Component for OpenLens
 * 
 * A customizable accordion component with various styles and features
 */

import React, { useState } from 'react';
import { Collapse, Typography, Space, Button, Tooltip } from 'antd';
import { RightOutlined, DownOutlined, PlusOutlined, MinusOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Text, Title } = Typography;

interface AccordionItem {
  key: string;
  title: React.ReactNode;
  children: React.ReactNode;
  extra?: React.ReactNode;
  disabled?: boolean;
  defaultActive?: boolean;
  icon?: React.ReactNode;
  [key: string]: any;
}

interface AccordionProps {
  items: AccordionItem[];
  activeKeys?: string[];
  onChange?: (keys: string[]) => void;
  accordion?: boolean;
  bordered?: boolean;
  ghost?: boolean;
  expandIcon?: (props: { isActive: boolean }) => React.ReactNode;
  expandIconPosition?: 'left' | 'right';
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  headerStyle?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  animated?: boolean;
}

const Accordion: React.FC<AccordionProps> = ({
  items = [],
  activeKeys,
  onChange,
  accordion = false,
  bordered = true,
  ghost = false,
  expandIcon,
  expandIconPosition = 'right',
  size = 'default',
  style = {},
  className = '',
  headerStyle = {},
  bodyStyle = {},
  animated = true,
}) => {
  const [internalActiveKeys, setInternalActiveKeys] = useState<string[]>(() => {
    return activeKeys || items.filter(item => item.defaultActive).map(item => item.key);
  });

  // Sync active keys
  React.useEffect(() => {
    if (activeKeys !== undefined) {
      setInternalActiveKeys(activeKeys);
    }
  }, [activeKeys]);

  // Handle change
  const handleChange = (keys: string[]) => {
    setInternalActiveKeys(keys);
    if (onChange) {
      onChange(keys);
    }
  };

  // Custom expand icon
  const customExpandIcon = (props: { isActive: boolean }) => {
    if (expandIcon) {
      return expandIcon(props);
    }

    return props.isActive ? <DownOutlined /> : <RightOutlined />;
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { title: number; padding: number }> = {
      small: { title: 14, padding: 12 },
      default: { title: 16, padding: 16 },
      large: { title: 18, padding: 24 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Collapse
        activeKey={internalActiveKeys}
        onChange={handleChange}
        accordion={accordion}
        bordered={bordered}
        ghost={ghost}
        expandIcon={customExpandIcon as any}
        expandIconPosition={expandIconPosition}
        style={{
          borderRadius: 12,
          background: ghost ? 'transparent' : 'var(--card-bg)',
          border: bordered ? '1px solid var(--border-color)' : 'none',
        }}
      >
        {items.map((item) => (
          <Collapse.Panel
            key={item.key}
            header={
              <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                <Space>
                  {item.icon && (
                    <span style={{ marginRight: 8 }}>{item.icon}</span>
                  )}
                  <Title
                    level={5}
                    style={{
                      margin: 0,
                      fontSize: sizeStyles.title,
                    }}
                  >
                    {item.title}
                  </Title>
                </Space>
                {item.extra}
              </Space>
            }
            disabled={item.disabled}
            style={{
              border: bordered ? '1px solid var(--border-color)' : 'none',
            }}
            extra={item.extra}
          >
            <div
              style={{
                padding: sizeStyles.padding,
                ...bodyStyle,
              }}
            >
              {item.children}
            </div>
          </Collapse.Panel>
        ))}
      </Collapse>
    </motion.div>
  );
};

// ExpandableSection component (single expandable section)
interface ExpandableSectionProps {
  title: React.ReactNode;
  children: React.ReactNode;
  extra?: React.ReactNode;
  defaultExpanded?: boolean;
  disabled?: boolean;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  headerStyle?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  animated?: boolean;
}

export const ExpandableSection: React.FC<ExpandableSectionProps> = ({
  title,
  children,
  extra,
  defaultExpanded = false,
  disabled = false,
  size = 'default',
  style = {},
  className = '',
  headerStyle = {},
  bodyStyle = {},
  animated = true,
}) => {
  const [expanded, setExpanded] = useState(defaultExpanded);

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { title: number; padding: number }> = {
      small: { title: 14, padding: 12 },
      default: { title: 16, padding: 16 },
      large: { title: 18, padding: 24 },
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
        border: '1px solid var(--border-color)',
        borderRadius: 12,
        background: 'var(--card-bg)',
        overflow: 'hidden',
        ...style,
      }}
      className={className}
    >
      <motion.div
        style={{
          padding: sizeStyles.padding,
          cursor: disabled ? 'not-allowed' : 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          ...headerStyle,
        }}
        onClick={() => !disabled && setExpanded(!expanded)}
        whileHover={{ background: 'rgba(0, 0, 0, 0.02)' }}
      >
        <Title
          level={5}
          style={{
            margin: 0,
            fontSize: sizeStyles.title,
          }}
        >
          {title}
        </Title>
        
        <Space>
          {extra}
          <motion.span
            animate={{ rotate: expanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <DownOutlined />
          </motion.span>
        </Space>
      </motion.div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: animated ? 0.3 : 0 }}
            style={{
              padding: sizeStyles.padding,
              borderTop: '1px solid var(--border-color)',
              ...bodyStyle,
            }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// CollapsiblePanel component (similar to ExpandableSection)
interface CollapsiblePanelProps {
  header: React.ReactNode;
  children: React.ReactNode;
  defaultCollapsed?: boolean;
  collapsible?: boolean;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
  headerStyle?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
}

export const CollapsiblePanel: React.FC<CollapsiblePanelProps> = ({
  header,
  children,
  defaultCollapsed = false,
  collapsible = true,
  size = 'default',
  style = {},
  className = '',
  headerStyle = {},
  bodyStyle = {},
}) => {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { padding: number }> = {
      small: { padding: 12 },
      default: { padding: 16 },
      large: { padding: 24 },
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
        border: '1px solid var(--border-color)',
        borderRadius: 12,
        background: 'var(--card-bg)',
        overflow: 'hidden',
        ...style,
      }}
      className={className}
    >
      <motion.div
        style={{
          padding: sizeStyles.padding,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: collapsible ? 'pointer' : 'default',
          ...headerStyle,
        }}
        onClick={() => collapsible && setCollapsed(!collapsed)}
        whileHover={collapsible ? { background: 'rgba(0, 0, 0, 0.02)' } : {}}
      >
        {header}
        
        {collapsible && (
          <motion.span
            animate={{ rotate: collapsed ? 0 : 180 }}
            transition={{ duration: 0.2 }}
          >
            <DownOutlined />
          </motion.span>
        )}
      </motion.div>

      <AnimatePresence>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            style={{
              padding: sizeStyles.padding,
              borderTop: '1px solid var(--border-color)',
              ...bodyStyle,
            }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// FAQ component (Frequently Asked Questions)
interface FAQItem {
  question: string;
  answer: React.ReactNode;
  [key: string]: any;
}

interface FAQProps {
  items: FAQItem[];
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const FAQ: React.FC<FAQProps> = ({
  items = [],
  size = 'default',
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Accordion
        items={items.map((item, index) => ({
          key: `faq-${index}`,
          title: item.question,
          children: item.answer,
        }))}
        accordion={true}
        bordered={false}
        ghost={true}
        size={size}
      />
    </motion.div>
  );
};

export default Accordion;
