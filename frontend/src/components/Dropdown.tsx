/**
 * Enhanced Dropdown Component for OpenLens
 * 
 * A customizable dropdown component with various styles and features
 */

import React, { useState, useRef, useEffect } from 'react';
import { Dropdown as AntDropdown, Button, Menu, Space, Typography, Tooltip, Divider } from 'antd';
import { MoreOutlined, DownOutlined, RightOutlined, CheckOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Text } = Typography;

interface DropdownItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  danger?: boolean;
  type?: 'group' | 'item' | 'divider';
  children?: DropdownItem[];
  onClick?: () => void;
  [key: string]: any;
}

interface DropdownProps {
  items: DropdownItem[];
  onSelect?: (key: string, item: DropdownItem) => void;
  trigger?: ('click' | 'hover' | 'contextMenu')[];
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  disabled?: boolean;
  loading?: boolean;
  size?: 'small' | 'default' | 'large';
  buttonText?: string;
  buttonIcon?: React.ReactNode;
  buttonProps?: any;
  menuProps?: any;
  style?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
  selectable?: boolean;
  selectedKeys?: string[];
  multiple?: boolean;
  searchable?: boolean;
  onSearch?: (value: string) => void;
  emptyText?: string;
}

const Dropdown: React.FC<DropdownProps> = ({
  items = [],
  onSelect,
  trigger = ['click'],
  placement = 'bottom',
  disabled = false,
  loading = false,
  size = 'default',
  buttonText,
  buttonIcon = <MoreOutlined />,
  buttonProps = {},
  menuProps = {},
  style = {},
  className = '',
  children,
  selectable = false,
  selectedKeys = [],
  multiple = false,
  searchable = false,
  onSearch,
  emptyText = 'No options',
}) => {
  const [searchValue, setSearchValue] = useState('');

  // Handle menu click
  const handleMenuClick = ({ key }: { key: string }) => {
    const item = findItemByKey(items, key);
    if (item && !item.disabled) {
      if (onSelect) {
        onSelect(key, item);
      }
      if (item.onClick) {
        item.onClick();
      }
    }
  };

  // Find item by key
  const findItemByKey = (items: DropdownItem[], key: string): DropdownItem | null => {
    for (const item of items) {
      if (item.key === key) return item;
      if (item.children) {
        const found = findItemByKey(item.children, key);
        if (found) return found;
      }
    }
    return null;
  };

  // Filter items based on search
  const filteredItems = searchable
    ? filterItemsBySearch(items, searchValue)
    : items;

  // Filter items recursively
  const filterItemsBySearch = (items: DropdownItem[], search: string): DropdownItem[] => {
    return items
      .map(item => {
        if (item.type === 'divider') return item;
        if (item.type === 'group') {
          const filteredChildren = filterItemsBySearch(item.children || [], search);
          return { ...item, children: filteredChildren };
        }
        
        const matches = item.label.toLowerCase().includes(search.toLowerCase());
        if (matches) return item;
        
        if (item.children) {
          const filteredChildren = filterItemsBySearch(item.children, search);
          if (filteredChildren.length > 0) {
            return { ...item, children: filteredChildren };
          }
        }
        
        return null;
      })
      .filter(Boolean) as DropdownItem[];
  };

  // Render menu items
  const renderMenuItems = (items: DropdownItem[]) => {
    return items.map((item) => {
      if (item.type === 'divider') {
        return <Menu.Divider key={item.key} />;
      }

      if (item.type === 'group') {
        return (
          <Menu.SubMenu
            key={item.key}
            title={item.label}
            icon={item.icon}
            disabled={item.disabled}
            popupClassName="dropdown-submenu"
          >
            {renderMenuItems(item.children || [])}
          </Menu.SubMenu>
        );
      }

      const isSelected = selectedKeys.includes(item.key);

      return (
        <Menu.Item
          key={item.key}
          icon={item.icon}
          disabled={item.disabled}
          danger={item.danger}
          onClick={() => handleMenuClick({ key: item.key })}
        >
          {selectable && (
            <Space>
              {isSelected && <CheckOutlined style={{ color: '#1890ff' }} />}
              {item.label}
            </Space>
          )}
          {!selectable && item.label}
        </Menu.Item>
      );
    });
  };

  // Build menu
  const menu = (
    <Menu
      onClick={handleMenuClick}
      selectedKeys={selectable ? selectedKeys : []}
      multiple={multiple}
      style={{ minWidth: 150 }}
      {...menuProps}
    >
      {searchable && (
        <Menu.Item key="search" disabled>
          <Input
            placeholder="Search..."
            value={searchValue}
            onChange={(e) => {
              setSearchValue(e.target.value);
              if (onSearch) {
                onSearch(e.target.value);
              }
            }}
            size="small"
            style={{ width: '100%', margin: 8 }}
            autoFocus
          />
        </Menu.Item>
      )}

      {filteredItems.length > 0 ? (
        renderMenuItems(filteredItems)
      ) : (
        <Menu.Item key="empty" disabled>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {emptyText}
          </Text>
        </Menu.Item>
      )}
    </Menu>
  );

  // If children provided, use them as trigger
  if (children) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={style}
        className={className}
      >
        <AntDropdown
          overlay={menu}
          trigger={trigger}
          placement={placement}
          disabled={disabled}
        >
          {children}
        </AntDropdown>
      </motion.div>
    );
  }

  // Default render with button
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
      className={className}
    >
      <AntDropdown
        overlay={menu}
        trigger={trigger}
        placement={placement}
        disabled={disabled}
      >
        <Button
          type="default"
          icon={buttonIcon}
          loading={loading}
          size={size}
          disabled={disabled}
          {...buttonProps}
        >
          {buttonText}
          {buttonText && !buttonIcon && <DownOutlined style={{ marginLeft: 4 }} />}
        </Button>
      </AntDropdown>
    </motion.div>
  );
};

// SplitButton component
interface SplitButtonProps {
  primaryAction?: {
    text?: string;
    icon?: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    loading?: boolean;
  };
  dropdownItems?: DropdownItem[];
  onSelect?: (key: string, item: DropdownItem) => void;
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  loading?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const SplitButton: React.FC<SplitButtonProps> = ({
  primaryAction,
  dropdownItems = [],
  onSelect,
  size = 'default',
  disabled = false,
  loading = false,
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        ...style,
      }}
      className={className}
    >
      <Button
        type="primary"
        onClick={primaryAction?.onClick}
        disabled={disabled || primaryAction?.disabled}
        loading={loading || primaryAction?.loading}
        size={size}
        style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
      >
        {primaryAction?.icon}
        {primaryAction?.text}
      </Button>

      <Dropdown
        items={dropdownItems}
        onSelect={onSelect}
        trigger={['click']}
        placement="bottomRight"
        disabled={disabled || loading}
        size={size}
        buttonIcon={<DownOutlined />}
        buttonProps={{
          style: {
            borderTopLeftRadius: 0,
            borderBottomLeftRadius: 0,
            borderLeft: 'none',
          },
        }}
      />
    </motion.div>
  );
};

// ActionMenu component (dropdown with actions)
interface ActionMenuProps {
  actions: DropdownItem[];
  onSelect?: (key: string, item: DropdownItem) => void;
  trigger?: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  disabled?: boolean;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const ActionMenu: React.FC<ActionMenuProps> = ({
  actions = [],
  onSelect,
  trigger = <Button type="text" icon={<MoreOutlined />} size="small" />,
  placement = 'bottomRight',
  disabled = false,
  size = 'small',
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
      className={className}
    >
      <Dropdown
        items={actions}
        onSelect={onSelect}
        trigger={['click']}
        placement={placement}
        disabled={disabled}
        size={size}
      >
        {trigger}
      </Dropdown>
    </motion.div>
  );
};

// ContextMenu component (right-click menu)
interface ContextMenuProps {
  items: DropdownItem[];
  onSelect?: (key: string, item: DropdownItem) => void;
  children: React.ReactNode;
  disabled?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const ContextMenu: React.FC<ContextMenuProps> = ({
  items = [],
  onSelect,
  children,
  disabled = false,
  style = {},
  className = '',
}) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const menuRef = useRef<HTMLDivElement>(null);

  // Handle context menu
  const handleContextMenu = (e: React.MouseEvent) => {
    if (disabled) return;
    e.preventDefault();
    setPosition({ x: e.clientX, y: e.clientY });
    setVisible(true);
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setVisible(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle menu click
  const handleMenuClick = (key: string) => {
    setVisible(false);
    const item = findItemByKey(items, key);
    if (item && !item.disabled) {
      if (onSelect) {
        onSelect(key, item);
      }
      if (item.onClick) {
        item.onClick();
      }
    }
  };

  // Find item by key
  const findItemByKey = (items: DropdownItem[], key: string): DropdownItem | null => {
    for (const item of items) {
      if (item.key === key) return item;
      if (item.children) {
        const found = findItemByKey(item.children, key);
        if (found) return found;
      }
    }
    return null;
  };

  // Render menu items
  const renderMenuItems = (items: DropdownItem[]) => {
    return items.map((item) => {
      if (item.type === 'divider') {
        return <Menu.Divider key={item.key} />;
      }

      if (item.type === 'group') {
        return (
          <Menu.SubMenu
            key={item.key}
            title={item.label}
            icon={item.icon}
            disabled={item.disabled}
          >
            {renderMenuItems(item.children || [])}
          </Menu.SubMenu>
        );
      }

      return (
        <Menu.Item
          key={item.key}
          icon={item.icon}
          disabled={item.disabled}
          danger={item.danger}
          onClick={() => handleMenuClick(item.key)}
        >
          {item.label}
        </Menu.Item>
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      ref={menuRef}
      onContextMenu={handleContextMenu}
      style={style}
      className={className}
    >
      {children}

      <AnimatePresence>
        {visible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'fixed',
              top: position.y,
              left: position.x,
              zIndex: 1000,
              minWidth: 150,
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
              borderRadius: 8,
              background: 'var(--card-bg)',
              border: '1px solid var(--border-color)',
            }}
            onContextMenu={(e) => e.preventDefault()}
          >
            <Menu
              onClick={({ key }) => handleMenuClick(key)}
              style={{ border: 'none' }}
            >
              {renderMenuItems(items)}
            </Menu>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

// SelectDropdown component (dropdown with select functionality)
interface SelectDropdownProps {
  options: DropdownItem[];
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  placeholder?: string;
  multiple?: boolean;
  disabled?: boolean;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const SelectDropdown: React.FC<SelectDropdownProps> = ({
  options = [],
  value,
  onChange,
  placeholder = 'Select...',
  multiple = false,
  disabled = false,
  size = 'default',
  style = {},
  className = '',
}) => {
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  // Sync selected keys with value
  useEffect(() => {
    if (value) {
      setSelectedKeys(multiple ? (Array.isArray(value) ? value : [value]) : [value]);
    }
  }, [value, multiple]);

  // Handle select
  const handleSelect = (key: string) => {
    if (disabled) return;

    if (multiple) {
      const newKeys = selectedKeys.includes(key)
        ? selectedKeys.filter(k => k !== key)
        : [...selectedKeys, key];
      setSelectedKeys(newKeys);
      if (onChange) {
        onChange(newKeys);
      }
    } else {
      setSelectedKeys([key]);
      if (onChange) {
        onChange(key);
      }
    }
  };

  // Get selected labels
  const getSelectedLabels = () => {
    if (!value) return placeholder;

    if (multiple && Array.isArray(value)) {
      const labels = value.map(v => {
        const option = options.find(o => o.key === v);
        return option ? option.label : v;
      });
      return labels.join(', ');
    }

    const option = options.find(o => o.key === value);
    return option ? option.label : value;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Dropdown
        items={options}
        onSelect={(key) => handleSelect(key)}
        trigger={['click']}
        placement="bottom"
        disabled={disabled}
        size={size}
        selectable={true}
        selectedKeys={selectedKeys}
        multiple={multiple}
        buttonText={getSelectedLabels()}
        buttonIcon={multiple ? undefined : <DownOutlined />}
        buttonProps={{
          style: {
            width: '100%',
            justifyContent: 'space-between',
          },
        }}
      />
    </motion.div>
  );
};

export default Dropdown;
