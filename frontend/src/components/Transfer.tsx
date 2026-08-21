/**
 * Transfer Component for OpenLens
 * 
 * A customizable transfer component for moving items between two lists
 */

import React, { useState } from 'react';
import { Transfer as AntTransfer, Button, Input, Space, Typography, Card, List, Checkbox, Tag } from 'antd';
import { SearchOutlined, LeftOutlined, RightOutlined, DoubleLeftOutlined, DoubleRightOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface TransferItem {
  key: string;
  title: string;
  description?: string;
  disabled?: boolean;
  tag?: string;
  [key: string]: any;
}

interface TransferProps {
  dataSource: TransferItem[];
  targetKeys?: string[];
  onChange?: (targetKeys: string[], direction: 'left' | 'right') => void;
  titles?: [string, string];
  operations?: string[];
  showSearch?: boolean;
  filterOption?: (inputValue: string, option: TransferItem) => boolean;
  listStyle?: React.CSSProperties;
  operationStyle?: React.CSSProperties;
  style?: React.CSSProperties;
  className?: string;
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  oneWay?: boolean;
  showSelectAll?: boolean;
  selectAllText?: string;
  emptyText?: string;
  itemRender?: (item: TransferItem) => React.ReactNode;
  footerRender?: (props: { direction: 'left' | 'right'; selectedKeys: string[]; items: TransferItem[] }) => React.ReactNode;
}

const Transfer: React.FC<TransferProps> = ({
  dataSource = [],
  targetKeys = [],
  onChange,
  titles = ['Source', 'Target'],
  operations = ['>', '<'],
  showSearch = true,
  filterOption,
  listStyle = {},
  operationStyle = {},
  style = {},
  className = '',
  size = 'default',
  disabled = false,
  oneWay = false,
  showSelectAll = true,
  selectAllText = 'Select All',
  emptyText = 'No data',
  itemRender,
  footerRender,
}) => {
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);
  const [searchValue, setSearchValue] = useState('');

  // Handle select change
  const handleSelectChange = (sourceSelectedKeys: string[], targetSelectedKeys: string[]) => {
    setSelectedKeys([...sourceSelectedKeys, ...targetSelectedKeys]);
  };

  // Handle transfer
  const handleTransfer = (direction: 'left' | 'right') => {
    if (disabled) return;

    const sourceKeys = direction === 'right' ? selectedKeys : targetKeys;
    const targetKeysNew = direction === 'right' ? targetKeys : selectedKeys;

    const newTargetKeys = direction === 'right'
      ? [...targetKeysNew, ...sourceKeys]
      : targetKeysNew.filter(key => !sourceKeys.includes(key));

    if (onChange) {
      onChange(newTargetKeys, direction);
    }

    setSelectedKeys([]);
  };

  // Handle select all
  const handleSelectAll = (direction: 'left' | 'right') => {
    const keys = direction === 'left'
      ? dataSource.map(item => item.key)
      : targetKeys;
    setSelectedKeys(keys);
  };

  // Filter data source
  const filteredDataSource = showSearch && searchValue
    ? dataSource.filter(item => {
        if (filterOption) {
          return filterOption(searchValue, item);
        }
        return item.title.toLowerCase().includes(searchValue.toLowerCase());
      })
    : dataSource;

  // Get source items
  const sourceItems = filteredDataSource.filter(item => !targetKeys.includes(item.key));

  // Get target items
  const targetItems = dataSource.filter(item => targetKeys.includes(item.key));

  // Get selected source keys
  const selectedSourceKeys = selectedKeys.filter(key => sourceItems.some(item => item.key === key));

  // Get selected target keys
  const selectedTargetKeys = selectedKeys.filter(key => targetItems.some(item => item.key === key));

  // Render item
  const renderItem = (item: TransferItem) => {
    if (itemRender) {
      return itemRender(item);
    }

    return (
      <List.Item
        style={{
          padding: 8,
          cursor: 'pointer',
        }}
      >
        <Space>
          <Checkbox checked={selectedKeys.includes(item.key)} />
          <Space direction="vertical">
            <Text strong>{item.title}</Text>
            {item.description && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {item.description}
              </Text>
            )}
          </Space>
          {item.tag && (
            <Tag color="blue" style={{ margin: 0 }}>
              {item.tag}
            </Tag>
          )}
        </Space>
      </List.Item>
    );
  };

  // Render list
  const renderList = (direction: 'left' | 'right', items: TransferItem[]) => {
    const isSource = direction === 'left';
    const listItems = isSource ? sourceItems : targetItems;
    const selectedKeysList = isSource ? selectedSourceKeys : selectedTargetKeys;

    return (
      <motion.div
        initial={{ opacity: 0, x: isSource ? -20 : 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card
          title={titles[isSource ? 0 : 1]}
          size="small"
          bodyStyle={{ padding: 8 }}
          style={{
            borderRadius: 8,
            ...listStyle,
          }}
          extra={
            showSelectAll && listItems.length > 0 && (
              <Button
                type="link"
                size="small"
                onClick={() => handleSelectAll(direction)}
              >
                {selectAllText}
              </Button>
            )
          }
        >
          {showSearch && isSource && (
            <Input
              placeholder="Search..."
              prefix={<SearchOutlined />}
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              size={size}
              style={{ marginBottom: 8 }}
              allowClear
            />
          )}

          <List
            dataSource={listItems}
            renderItem={(item) => renderItem(item)}
            style={{
              maxHeight: 300,
              overflowY: 'auto',
              border: '1px solid var(--border-color)',
              borderRadius: 8,
            }}
          />

          {listItems.length === 0 && (
            <Text type="secondary" style={{ textAlign: 'center', display: 'block', padding: 24 }}>
              {emptyText}
            </Text>
          )}

          {footerRender && footerRender({
            direction,
            selectedKeys: selectedKeysList,
            items: listItems,
          })}
        </Card>
      </motion.div>
    );
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { padding: number; button: number }> = {
      small: { padding: 8, button: 24 },
      default: { padding: 16, button: 32 },
      large: { padding: 24, button: 40 },
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
        display: 'flex',
        gap: 16,
        alignItems: 'center',
        ...style,
      }}
      className={className}
    >
      {renderList('left', sourceItems)}

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
          ...operationStyle,
        }}
      >
        {operations.includes('>') && !oneWay && (
          <Button
            type="primary"
            icon={<RightOutlined />}
            onClick={() => handleTransfer('right')}
            disabled={selectedKeys.length === 0 || disabled}
            size={size}
            style={{ width: sizeStyles.button, height: sizeStyles.button }}
          />
        )}

        {operations.includes('>>') && !oneWay && (
          <Button
            type="primary"
            icon={<DoubleRightOutlined />}
            onClick={() => {
              const allSourceKeys = sourceItems.map(item => item.key);
              setSelectedKeys(allSourceKeys);
              handleTransfer('right');
            }}
            disabled={sourceItems.length === 0 || disabled}
            size={size}
            style={{ width: sizeStyles.button, height: sizeStyles.button }}
          />
        )}

        {operations.includes('<') && !oneWay && (
          <Button
            type="primary"
            icon={<LeftOutlined />}
            onClick={() => handleTransfer('left')}
            disabled={selectedKeys.length === 0 || disabled}
            size={size}
            style={{ width: sizeStyles.button, height: sizeStyles.button }}
          />
        )}

        {operations.includes('<<') && !oneWay && (
          <Button
            type="primary"
            icon={<DoubleLeftOutlined />}
            onClick={() => {
              const allTargetKeys = targetItems.map(item => item.key);
              setSelectedKeys(allTargetKeys);
              handleTransfer('left');
            }}
            disabled={targetItems.length === 0 || disabled}
            size={size}
            style={{ width: sizeStyles.button, height: sizeStyles.button }}
          />
        )}

        {oneWay && operations.includes('>') && (
          <Button
            type="primary"
            icon={<RightOutlined />}
            onClick={() => handleTransfer('right')}
            disabled={selectedKeys.length === 0 || disabled}
            size={size}
            style={{ width: sizeStyles.button, height: sizeStyles.button }}
          />
        )}
      </motion.div>

      {renderList('right', targetItems)}
    </motion.div>
  );
};

// DualList component (alias for Transfer)
export const DualList: React.FC<TransferProps> = (props) => {
  return <Transfer {...props} />;
};

// SimpleTransfer component (simplified transfer)
interface SimpleTransferProps {
  leftTitle?: string;
  rightTitle?: string;
  leftItems: TransferItem[];
  rightItems: TransferItem[];
  onMoveLeft?: (keys: string[]) => void;
  onMoveRight?: (keys: string[]) => void;
  onMoveAllLeft?: () => void;
  onMoveAllRight?: () => void;
  selectedLeftKeys?: string[];
  selectedRightKeys?: string[];
  onSelectLeft?: (keys: string[]) => void;
  onSelectRight?: (keys: string[]) => void;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const SimpleTransfer: React.FC<SimpleTransferProps> = ({
  leftTitle = 'Available',
  rightTitle = 'Selected',
  leftItems = [],
  rightItems = [],
  onMoveLeft,
  onMoveRight,
  onMoveAllLeft,
  onMoveAllRight,
  selectedLeftKeys = [],
  selectedRightKeys = [],
  onSelectLeft,
  onSelectRight,
  size = 'default',
  style = {},
  className = '',
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { padding: number; button: number }> = {
      small: { padding: 8, button: 24 },
      default: { padding: 16, button: 32 },
      large: { padding: 24, button: 40 },
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
        display: 'flex',
        gap: 16,
        alignItems: 'center',
        ...style,
      }}
      className={className}
    >
      {/* Left list */}
      <Card
        title={leftTitle}
        size="small"
        bodyStyle={{ padding: 8 }}
        style={{ borderRadius: 8, flex: 1 }}
      >
        <List
          dataSource={leftItems}
          renderItem={(item) => (
            <List.Item
              style={{
                padding: 8,
                cursor: 'pointer',
                background: selectedLeftKeys.includes(item.key) ? 'var(--bg-color-secondary)' : 'transparent',
              }}
              onClick={() => {
                const newKeys = selectedLeftKeys.includes(item.key)
                  ? selectedLeftKeys.filter(key => key !== item.key)
                  : [...selectedLeftKeys, item.key];
                if (onSelectLeft) {
                  onSelectLeft(newKeys);
                }
              }}
            >
              <Space>
                <Checkbox checked={selectedLeftKeys.includes(item.key)} />
                <Text>{item.title}</Text>
                {item.tag && (
                  <Tag color="blue" style={{ margin: 0 }}>
                    {item.tag}
                  </Tag>
                )}
              </Space>
            </List.Item>
          )}
          style={{
            maxHeight: 300,
            overflowY: 'auto',
            border: '1px solid var(--border-color)',
            borderRadius: 8,
          }}
        />
      </Card>

      {/* Buttons */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 8,
        }}
      >
        <Button
          type="primary"
          icon={<RightOutlined />}
          onClick={() => onMoveRight && onMoveRight(selectedLeftKeys)}
          disabled={selectedLeftKeys.length === 0}
          size={size}
          style={{ width: sizeStyles.button, height: sizeStyles.button }}
        />

        <Button
          type="primary"
          icon={<DoubleRightOutlined />}
          onClick={onMoveAllRight}
          disabled={leftItems.length === 0}
          size={size}
          style={{ width: sizeStyles.button, height: sizeStyles.button }}
        />

        <Button
          type="primary"
          icon={<LeftOutlined />}
          onClick={() => onMoveLeft && onMoveLeft(selectedRightKeys)}
          disabled={selectedRightKeys.length === 0}
          size={size}
          style={{ width: sizeStyles.button, height: sizeStyles.button }}
        />

        <Button
          type="primary"
          icon={<DoubleLeftOutlined />}
          onClick={onMoveAllLeft}
          disabled={rightItems.length === 0}
          size={size}
          style={{ width: sizeStyles.button, height: sizeStyles.button }}
        />
      </motion.div>

      {/* Right list */}
      <Card
        title={rightTitle}
        size="small"
        bodyStyle={{ padding: 8 }}
        style={{ borderRadius: 8, flex: 1 }}
      >
        <List
          dataSource={rightItems}
          renderItem={(item) => (
            <List.Item
              style={{
                padding: 8,
                cursor: 'pointer',
                background: selectedRightKeys.includes(item.key) ? 'var(--bg-color-secondary)' : 'transparent',
              }}
              onClick={() => {
                const newKeys = selectedRightKeys.includes(item.key)
                  ? selectedRightKeys.filter(key => key !== item.key)
                  : [...selectedRightKeys, item.key];
                if (onSelectRight) {
                  onSelectRight(newKeys);
                }
              }}
            >
              <Space>
                <Checkbox checked={selectedRightKeys.includes(item.key)} />
                <Text>{item.title}</Text>
                {item.tag && (
                  <Tag color="blue" style={{ margin: 0 }}>
                    {item.tag}
                  </Tag>
                )}
              </Space>
            </List.Item>
          )}
          style={{
            maxHeight: 300,
            overflowY: 'auto',
            border: '1px solid var(--border-color)',
            borderRadius: 8,
          }}
        />
      </Card>
    </motion.div>
  );
};

// RoleTransfer component (transfer for role assignments)
interface RoleTransferItem extends TransferItem {
  role?: string;
  permissions?: string[];
}

interface RoleTransferProps extends Omit<TransferProps, 'dataSource' | 'itemRender'> {
  dataSource: RoleTransferItem[];
  showRole?: boolean;
  showPermissions?: boolean;
}

export const RoleTransfer: React.FC<RoleTransferProps> = ({
  dataSource = [],
  showRole = true,
  showPermissions = false,
  ...props
}) => {
  // Item render
  const itemRender = (item: RoleTransferItem) => (
    <List.Item
      style={{
        padding: 8,
        cursor: 'pointer',
      }}
    >
      <Space>
        <Checkbox />
        <Space direction="vertical">
          <Text strong>{item.title}</Text>
          
          <Space wrap>
            {showRole && item.role && (
              <Tag color="blue" style={{ margin: 0 }}>
                {item.role}
              </Tag>
            )}
            
            {showPermissions && item.permissions && item.permissions.length > 0 && (
              <Tag color="green" style={{ margin: 0 }}>
                {item.permissions.length} permissions
              </Tag>
            )}
          </Space>
        </Space>
      </Space>
    </List.Item>
  );

  return (
    <Transfer
      {...props}
      dataSource={dataSource}
      itemRender={itemRender}
    />
  );
};

// UserTransfer component (transfer for user assignments)
interface UserTransferItem extends TransferItem {
  email?: string;
  avatar?: string;
  role?: string;
}

interface UserTransferProps extends Omit<TransferProps, 'dataSource' | 'itemRender'> {
  dataSource: UserTransferItem[];
  showAvatar?: boolean;
  showEmail?: boolean;
  showRole?: boolean;
}

export const UserTransfer: React.FC<UserTransferProps> = ({
  dataSource = [],
  showAvatar = true,
  showEmail = true,
  showRole = true,
  ...props
}) => {
  // Item render
  const itemRender = (item: UserTransferItem) => (
    <List.Item
      style={{
        padding: 8,
        cursor: 'pointer',
      }}
    >
      <Space>
        <Checkbox />
        
        {showAvatar && (item.avatar ? (
          <img
            src={item.avatar}
            alt={item.title}
            style={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              marginRight: 8,
            }}
          />
        ) : (
          <div
            style={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              background: '#1890ff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: 12,
              marginRight: 8,
            }}
          >
            {item.title.charAt(0).toUpperCase()}
          </div>
        ))}
        
        <Space direction="vertical">
          <Text strong>{item.title}</Text>
          
          <Space wrap>
            {showEmail && item.email && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {item.email}
              </Text>
            )}
            
            {showRole && item.role && (
              <Tag color="blue" style={{ margin: 0 }}>
                {item.role}
              </Tag>
            )}
          </Space>
        </Space>
      </Space>
    </List.Item>
  );

  return (
    <Transfer
      {...props}
      dataSource={dataSource}
      itemRender={itemRender}
    />
  );
};

export default Transfer;
