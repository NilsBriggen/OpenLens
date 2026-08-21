/**
 * Tree Component for OpenLens
 * 
 * A customizable tree component for displaying hierarchical data
 */

import React, { useState } from 'react';
import { Tree as AntTree, Input, Button, Space, Typography, Tooltip, Card, Tag } from 'antd';
import { SearchOutlined, PlusOutlined, MinusOutlined, FolderOutlined, FileOutlined, FolderOpenOutlined, FileTextOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { DataNode } from 'antd/es/tree';

const { Title, Text } = Typography;

interface TreeNode extends DataNode {
  id?: string;
  name?: string;
  type?: 'folder' | 'file' | 'root';
  icon?: React.ReactNode;
  color?: string;
  count?: number;
  children?: TreeNode[];
  [key: string]: any;
}

interface TreeProps {
  data?: TreeNode[];
  onSelect?: (selectedKeys: React.Key[], info: any) => void;
  onCheck?: (checkedKeys: React.Key[], info: any) => void;
  onExpand?: (expandedKeys: React.Key[], info: any) => void;
  selectedKeys?: React.Key[];
  checkedKeys?: React.Key[];
  expandedKeys?: React.Key[];
  defaultSelectedKeys?: React.Key[];
  defaultCheckedKeys?: React.Key[];
  defaultExpandedKeys?: React.Key[];
  checkable?: boolean;
  selectable?: boolean;
  multiple?: boolean;
  showLine?: boolean;
  showIcon?: boolean;
  defaultExpandAll?: boolean;
  autoExpandParent?: boolean;
  searchable?: boolean;
  placeholder?: string;
  onAdd?: (parentKey?: React.Key) => void;
  onRemove?: (key: React.Key) => void;
  onEdit?: (key: React.Key) => void;
  titleRender?: (node: TreeNode) => React.ReactNode;
  iconRender?: (node: TreeNode) => React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  size?: 'small' | 'default' | 'large';
  height?: number | string;
}

const Tree: React.FC<TreeProps> = ({
  data = [],
  onSelect,
  onCheck,
  onExpand,
  selectedKeys,
  checkedKeys,
  expandedKeys,
  defaultSelectedKeys,
  defaultCheckedKeys,
  defaultExpandedKeys,
  checkable = false,
  selectable = true,
  multiple = false,
  showLine = true,
  showIcon = true,
  defaultExpandAll = false,
  autoExpandParent = true,
  searchable = false,
  placeholder = 'Search...',
  onAdd,
  onRemove,
  onEdit,
  titleRender,
  iconRender,
  style = {},
  className = '',
  size = 'default',
  height,
}) => {
  const [searchValue, setSearchValue] = useState('');
  const [internalExpandedKeys, setInternalExpandedKeys] = useState<React.Key[]>(defaultExpandedKeys || []);

  // Sync expanded keys
  React.useEffect(() => {
    if (expandedKeys !== undefined) {
      setInternalExpandedKeys(expandedKeys);
    }
  }, [expandedKeys]);

  // Handle expand
  const handleExpand = (expandedKeys: React.Key[]) => {
    setInternalExpandedKeys(expandedKeys);
    if (onExpand) {
      onExpand(expandedKeys, {});
    }
  };

  // Filter tree data based on search
  const filteredData = searchable && searchValue
    ? filterTreeData(data, searchValue)
    : data;

  // Filter tree data recursively
  const filterTreeData = (nodes: TreeNode[], search: string): TreeNode[] => {
    return nodes
      .map(node => {
        const children = node.children ? filterTreeData(node.children, search) : [];
        
        if (children.length > 0) {
          return { ...node, children };
        }
        
        const matches = node.name?.toLowerCase().includes(search.toLowerCase()) ||
                       node.title?.toString().toLowerCase().includes(search.toLowerCase()) ||
                       node.key?.toString().toLowerCase().includes(search.toLowerCase());
        
        return matches ? { ...node } : null;
      })
      .filter(Boolean) as TreeNode[];
  };

  // Get icon for node
  const getIcon = (node: TreeNode) => {
    if (iconRender) {
      return iconRender(node);
    }

    if (node.icon) {
      return node.icon;
    }

    switch (node.type) {
      case 'folder':
        return node.children && node.children.length > 0 ? <FolderOpenOutlined /> : <FolderOutlined />;
      case 'file':
        return <FileTextOutlined />;
      case 'root':
        return <FolderOutlined />;
      default:
        return node.children && node.children.length > 0 ? <FolderOpenOutlined /> : <FileOutlined />;
    }
  };

  // Get title for node
  const getTitle = (node: TreeNode) => {
    if (titleRender) {
      return titleRender(node);
    }

    return (
      <Space>
        {showIcon && getIcon(node)}
        <span>{node.name || node.title}</span>
        {node.count !== undefined && (
          <Tag color="blue" style={{ margin: 0, fontSize: 10 }}>
            {node.count}
          </Tag>
        )}
      </Space>
    );
  };

  // Build tree data
  const buildTreeData = (nodes: TreeNode[]): DataNode[] => {
    return nodes.map(node => ({
      key: node.id || node.key,
      title: getTitle(node),
      children: node.children ? buildTreeData(node.children) : undefined,
      disabled: node.disabled,
      selectable: node.selectable !== undefined ? node.selectable : selectable,
      checkable: node.checkable !== undefined ? node.checkable : checkable,
      isLeaf: node.isLeaf || (!node.children || node.children.length === 0),
      ...node,
    }));
  };

  // Handle add
  const handleAdd = (parentKey?: React.Key) => {
    if (onAdd) {
      onAdd(parentKey);
    }
  };

  // Handle remove
  const handleRemove = (key: React.Key) => {
    if (onRemove) {
      onRemove(key);
    }
  };

  // Handle edit
  const handleEdit = (key: React.Key) => {
    if (onEdit) {
      onEdit(key);
    }
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { padding: number; font: number }> = {
      small: { padding: 4, font: 12 },
      default: { padding: 8, font: 14 },
      large: { padding: 12, font: 16 },
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
        height: height || 'auto',
        overflow: 'auto',
        ...style,
      }}
      className={className}
    >
      {/* Search */}
      {searchable && (
        <div style={{ padding: sizeStyles.padding, borderBottom: '1px solid var(--border-color)' }}>
          <Input
            placeholder={placeholder}
            prefix={<SearchOutlined />}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            size={size}
            allowClear
          />
        </div>
      )}

      {/* Tree */}
      <AntTree
        treeData={buildTreeData(filteredData)}
        onSelect={onSelect}
        onCheck={onCheck}
        onExpand={handleExpand}
        selectedKeys={selectedKeys}
        checkedKeys={checkedKeys}
        expandedKeys={internalExpandedKeys}
        defaultSelectedKeys={defaultSelectedKeys}
        defaultCheckedKeys={defaultCheckedKeys}
        defaultExpandedKeys={defaultExpandedKeys}
        checkable={checkable}
        selectable={selectable}
        multiple={multiple}
        showLine={showLine}
        showIcon={false}
        defaultExpandAll={defaultExpandAll}
        autoExpandParent={autoExpandParent}
        height={height}
        style={{
          padding: sizeStyles.padding,
          fontSize: sizeStyles.font,
        }}
      />
    </motion.div>
  );
};

// FileTree component (tree for file system)
interface FileTreeNode extends TreeNode {
  fileType?: string;
  size?: number;
  modified?: string | Date;
}

interface FileTreeProps extends Omit<TreeProps, 'data' | 'titleRender' | 'iconRender'> {
  data?: FileTreeNode[];
  showFileInfo?: boolean;
  fileInfoFormat?: 'size' | 'modified' | 'both';
}

export const FileTree: React.FC<FileTreeProps> = ({
  data = [],
  showFileInfo = false,
  fileInfoFormat = 'size',
  ...props
}) => {
  // Get file icon
  const getFileIcon = (node: FileTreeNode) => {
    const icons: Record<string, React.ReactNode> = {
      folder: node.children && node.children.length > 0 ? <FolderOpenOutlined /> : <FolderOutlined />,
      file: <FileOutlined />,
      txt: <FileTextOutlined />,
      pdf: '📄',
      doc: '📝',
      xls: '📊',
      ppt: '📑',
      img: '🖼️',
      video: '🎥',
      audio: '🎵',
      zip: '🗄️',
      default: <FileOutlined />,
    };

    return icons[node.fileType || 'default'] || icons.default;
  };

  // Get file info
  const getFileInfo = (node: FileTreeNode) => {
    if (!showFileInfo) return null;

    const parts: string[] = [];

    if (fileInfoFormat === 'size' || fileInfoFormat === 'both') {
      if (node.size) {
        parts.push(formatFileSize(node.size));
      }
    }

    if (fileInfoFormat === 'modified' || fileInfoFormat === 'both') {
      if (node.modified) {
        parts.push(new Date(node.modified).toLocaleDateString());
      }
    }

    return parts.length > 0 ? (
      <Text type="secondary" style={{ fontSize: 10 }}>
        {parts.join(' • ')}
      </Text>
    ) : null;
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Title render
  const titleRender = (node: FileTreeNode) => (
    <Space>
      {getFileIcon(node)}
      <span>{node.name || node.title}</span>
      {getFileInfo(node)}
    </Space>
  );

  return (
    <Tree
      {...props}
      data={data}
      titleRender={titleRender}
      showIcon={false}
    />
  );
};

// OrganizationTree component (tree for organizational hierarchy)
interface OrgTreeNode extends TreeNode {
  role?: string;
  department?: string;
  email?: string;
  phone?: string;
  avatar?: string;
}

interface OrganizationTreeProps extends Omit<TreeProps, 'data' | 'titleRender' | 'iconRender'> {
  data?: OrgTreeNode[];
  showRole?: boolean;
  showDepartment?: boolean;
  showContactInfo?: boolean;
}

export const OrganizationTree: React.FC<OrganizationTreeProps> = ({
  data = [],
  showRole = true,
  showDepartment = true,
  showContactInfo = false,
  ...props
}) => {
  // Title render
  const titleRender = (node: OrgTreeNode) => (
    <Space>
      {node.avatar ? (
        <img
          src={node.avatar}
          alt={node.name}
          style={{
            width: 20,
            height: 20,
            borderRadius: '50%',
            marginRight: 8,
          }}
        />
      ) : (
        <Avatar
          size={20}
          style={{
            background: node.color || '#1890ff',
            marginRight: 8,
          }}
        >
          {(node.name || node.title)?.toString().charAt(0).toUpperCase()}
        </Avatar>
      )}
      
      <Space direction="vertical">
        <span>{node.name || node.title}</span>
        
        <Space wrap>
          {showRole && node.role && (
            <Tag color="blue" style={{ margin: 0, fontSize: 10 }}>
              {node.role}
            </Tag>
          )}
          
          {showDepartment && node.department && (
            <Tag color="green" style={{ margin: 0, fontSize: 10 }}>
              {node.department}
            </Tag>
          )}
        </Space>
        
        {showContactInfo && (
          <Space wrap>
            {node.email && (
              <Text type="secondary" style={{ fontSize: 10 }}>
                {node.email}
              </Text>
            )}
            {node.phone && (
              <Text type="secondary" style={{ fontSize: 10 }}>
                {node.phone}
              </Text>
            )}
          </Space>
        )}
      </Space>
    </Space>
  );

  return (
    <Tree
      {...props}
      data={data}
      titleRender={titleRender}
      showIcon={false}
      defaultExpandAll
    />
  );
};

// CategoryTree component (tree for categories)
interface CategoryTreeNode extends TreeNode {
  categoryType?: string;
  itemCount?: number;
}

interface CategoryTreeProps extends Omit<TreeProps, 'data' | 'titleRender'> {
  data?: CategoryTreeNode[];
  showItemCount?: boolean;
}

export const CategoryTree: React.FC<CategoryTreeProps> = ({
  data = [],
  showItemCount = true,
  ...props
}) => {
  // Title render
  const titleRender = (node: CategoryTreeNode) => (
    <Space>
      {node.icon || <FolderOutlined />}
      <span>{node.name || node.title}</span>
      {showItemCount && node.itemCount !== undefined && (
        <Tag color="default" style={{ margin: 0, fontSize: 10 }}>
          {node.itemCount}
        </Tag>
      )}
    </Space>
  );

  return (
    <Tree
      {...props}
      data={data}
      titleRender={titleRender}
      showIcon={false}
      defaultExpandAll
    />
  );
};

// CheckboxTree component (tree with checkboxes)
interface CheckboxTreeProps extends Omit<TreeProps, 'checkable'> {
  onCheckAll?: (checked: boolean) => void;
  showCheckAll?: boolean;
}

export const CheckboxTree: React.FC<CheckboxTreeProps> = ({
  onCheckAll,
  showCheckAll = false,
  ...props
}) => {
  const [allChecked, setAllChecked] = useState(false);
  const [indeterminate, setIndeterminate] = useState(false);

  // Handle check all
  const handleCheckAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setAllChecked(checked);
    setIndeterminate(false);
    if (onCheckAll) {
      onCheckAll(checked);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {showCheckAll && (
        <div style={{ padding: 8, borderBottom: '1px solid var(--border-color)' }}>
          <Space>
            <input
              type="checkbox"
              checked={allChecked}
              indeterminate={indeterminate}
              onChange={handleCheckAll}
            />
            <Text>Select All</Text>
          </Space>
        </div>
      )}
      
      <Tree
        {...props}
        checkable={true}
      />
    </motion.div>
  );
};

// DragDropTree component (tree with drag and drop)
interface DragDropTreeProps extends TreeProps {
  onDrop?: (info: any) => void;
  draggable?: boolean;
}

export const DragDropTree: React.FC<DragDropTreeProps> = ({
  onDrop,
  draggable = true,
  ...props
}) => {
  return (
    <Tree
      {...props}
      draggable={draggable}
      onDrop={onDrop}
    />
  );
};

// AsyncTree component (tree with async loading)
interface AsyncTreeProps extends Omit<TreeProps, 'data' | 'loadData'> {
  loadData?: (node: TreeNode) => Promise<TreeNode[]>;
  loadingKeys?: React.Key[];
}

export const AsyncTree: React.FC<AsyncTreeProps> = ({
  loadData,
  loadingKeys = [],
  ...props
}) => {
  return (
    <Tree
      {...props}
      loadData={loadData}
      loadingKeys={loadingKeys}
    />
  );
};

// Avatar component for tree nodes
const Avatar: React.FC<{ size?: number; style?: React.CSSProperties; children?: React.ReactNode }> = ({
  size = 20,
  style = {},
  children,
}) => {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: '#1890ff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: size * 0.6,
        color: '#fff',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export default Tree;
