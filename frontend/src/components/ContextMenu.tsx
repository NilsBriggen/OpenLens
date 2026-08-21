/**
 * Context Menu Component for OpenLens
 * 
 * A customizable context menu (right-click menu) with:
 * - Nested menu items
 * - Icons support
 * - Keyboard navigation
 * - Custom styling
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, Dropdown, Button, Space, Typography } from 'antd';
import { MoreOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  onClick?: () => void;
  children?: MenuItem[];
  disabled?: boolean;
  danger?: boolean;
  type?: 'group' | 'item' | 'divider';
}

interface ContextMenuProps {
  items: MenuItem[];
  children: React.ReactNode;
  onClick?: (key: string) => void;
  trigger?: 'click' | 'contextMenu' | 'hover';
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  disabled?: boolean;
}

const ContextMenu: React.FC<ContextMenuProps> = ({
  items,
  children,
  onClick,
  trigger = 'contextMenu',
  placement = 'bottomRight',
  disabled = false,
}) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const menuRef = useRef<HTMLDivElement>(null);

  // Handle context menu
  const handleContextMenu = useCallback((e: React.MouseEvent) => {
    if (disabled) return;
    e.preventDefault();
    setPosition({ x: e.clientX, y: e.clientY });
    setVisible(true);
  }, [disabled]);

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

  // Handle menu item click
  const handleMenuClick = (key: string) => {
    setVisible(false);
    if (onClick) {
      onClick(key);
    }
    
    // Find and execute the onClick handler
    const item = findItemByKey(items, key);
    if (item && item.onClick) {
      item.onClick();
    }
  };

  // Find item by key
  const findItemByKey = (items: MenuItem[], key: string): MenuItem | null => {
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
  const renderMenuItems = (items: MenuItem[]) => {
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
            popupClassName="context-menu-submenu"
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

  // Get menu styles
  const getMenuStyles = () => {
    return {
      position: 'fixed' as const,
      top: position.y,
      left: position.x,
      zIndex: 1000,
      minWidth: 200,
      boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
      borderRadius: 8,
      background: 'var(--card-bg)',
      border: '1px solid var(--border-color)',
    };
  };

  // For click trigger, use Ant Design's Dropdown
  if (trigger === 'click') {
    return (
      <Dropdown
        overlay={
          <Menu onClick={({ key }) => handleMenuClick(key)}>
            {renderMenuItems(items)}
          </Menu>
        }
        trigger={['click']}
        placement={placement}
        disabled={disabled}
      >
        {children}
      </Dropdown>
    );
  }

  // For context menu trigger
  return (
    <div
      ref={menuRef}
      onContextMenu={handleContextMenu}
      style={{ display: 'inline-block' }}
    >
      {children}
      
      <AnimatePresence>
        {visible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            style={getMenuStyles()}
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
    </div>
  );
};

// Context Menu with button trigger
interface ContextMenuButtonProps extends Omit<ContextMenuProps, 'children'> {
  buttonText?: string;
  buttonIcon?: React.ReactNode;
  buttonProps?: any;
}

export const ContextMenuButton: React.FC<ContextMenuButtonProps> = ({
  items,
  buttonText = 'Actions',
  buttonIcon = <MoreOutlined />,
  buttonProps = {},
  ...props
}) => {
  return (
    <ContextMenu items={items} trigger="click" {...props}>
      <Button icon={buttonIcon} {...buttonProps}>
        {buttonText}
      </Button>
    </ContextMenu>
  );
};

// Context Menu with custom trigger
interface ContextMenuTriggerProps extends Omit<ContextMenuProps, 'children' | 'trigger'> {
  triggerElement: React.ReactNode;
}

export const ContextMenuTrigger: React.FC<ContextMenuTriggerProps> = ({
  items,
  triggerElement,
  ...props
}) => {
  return (
    <ContextMenu items={items} trigger="click" {...props}>
      {triggerElement}
    </ContextMenu>
  );
};

export default ContextMenu;
