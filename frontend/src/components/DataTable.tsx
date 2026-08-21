import React, { useState, useEffect } from 'react';
import { Table, Input, Button, Space, Select, Tag, Tooltip, Dropdown, Menu, Typography, Card, Row, Col, DatePicker, Badge } from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  SortAscendingOutlined,
  SortDescendingOutlined,
  MoreOutlined,
  ExportOutlined,
  SyncOutlined,
  ColumnHeightOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  DeleteOutlined,
  EditOutlined,
  CopyOutlined,
  PrinterOutlined
} from '@ant-design/icons';
// antd's root export is TableColumnType; ColumnType lives in the table
// interface submodule. Importing the wrong name made this an error type and
// silently unchecked every column config in the app.
import type { TableProps, TableColumnType as ColumnType } from 'antd';
import type { FilterConfirmProps } from 'antd/es/table/interface';
import { motion } from 'framer-motion';

const { Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface DataTableProps<T> extends Omit<TableProps<T>, 'columns' | 'dataSource'> {
  columns: EnhancedColumnType<T>[];
  dataSource: T[];
  searchable?: boolean;
  filterable?: boolean;
  sortable?: boolean;
  pageSizeOptions?: number[];
  showRowActions?: boolean;
  onRowAction?: (action: string, record: T) => void;
  onBulkAction?: (action: string, selectedRows: T[]) => void;
  bulkActions?: { label: string; key: string; icon?: React.ReactNode }[];
  exportable?: boolean;
  onExport?: (data: T[]) => void;
  refreshable?: boolean;
  onRefresh?: () => void;
  columnSelector?: boolean;
  rowKey?: string | ((record: T) => string);
}

interface EnhancedColumnType<T> extends ColumnType<T> {
  searchable?: boolean;
  filterable?: boolean;
  filterOptions?: { value: string | number; label: string }[];
  filterType?: 'select' | 'search' | 'date' | 'number' | 'boolean';
  sortable?: boolean;
  renderAsTag?: boolean;
  tagColor?: (value: any) => string;
  renderAsStatus?: boolean;
  statusMap?: Record<string, { color: string; label: string }>;
  width?: number | string;
  ellipsis?: boolean;
  copyable?: boolean;
}

const DataTable = <T extends object>(
  {
    columns: rawColumns,
    dataSource,
    searchable = true,
    filterable = true,
    sortable = true,
    pageSizeOptions = [10, 20, 50, 100],
    showRowActions = true,
    onRowAction,
    onBulkAction,
    bulkActions = [],
    exportable = true,
    onExport,
    refreshable = true,
    onRefresh,
    columnSelector = true,
    rowKey = 'id',
    ...rest
  }: DataTableProps<T>
) => {
  const [searchText, setSearchText] = useState('');
  const [searchedColumn, setSearchedColumn] = useState('');
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [sortConfig, setSortConfig] = useState<{ key: string; order: 'ascend' | 'descend' } | null>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [visibleColumns, setVisibleColumns] = useState<string[]>(() => {
    return rawColumns.map(c => (c.key || c.dataIndex) as string);
  });
  const [pageSize, setPageSize] = useState(pageSizeOptions[0]);

  // Handle search
  const handleSearch = (
    selectedKeys: string[],
    confirm: (param?: FilterConfirmProps) => void,
    dataIndex: string | undefined
  ) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex || '');
  };

  // Handle reset
  const handleReset = (clearFilters: () => void) => {
    clearFilters();
    setSearchText('');
    setSearchedColumn('');
  };

  // Get column search props
  const getColumnSearchProps = (dataIndex: string | undefined): any => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters, close }: any) => (
      <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
        <Input
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
          style={{ marginBottom: 8, display: 'block' }}
        />
        <Space>
          <Button
            type="primary"
            onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
            icon={<SearchOutlined />}
            size="small"
          >
            Search
          </Button>
          <Button onClick={() => handleReset(clearFilters)} size="small">
            Reset
          </Button>
          <Button type="link" onClick={close} size="small">
            Close
          </Button>
        </Space>
      </div>
    ),
    filterIcon: (filtered: boolean) => (
      <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />
    ),
    onFilter: (value: any, record: T) => {
      if (dataIndex) {
        const recordValue = (record as any)[dataIndex];
        return String(recordValue).toLowerCase().includes(String(value).toLowerCase());
      }
      return false;
    },
  });

  // Get column filter props
  const getColumnFilterProps = (column: EnhancedColumnType<T>) => {
    if (!column.filterable) return {};

    switch (column.filterType) {
      case 'select':
        return {
          filters: column.filterOptions || [],
          onFilter: (value: any, record: T) => {
            if (column.dataIndex) {
              return (record as any)[column.dataIndex] === value;
            }
            return false;
          },
        };
      case 'boolean':
        return {
          filters: [
            { text: 'Yes', value: true },
            { text: 'No', value: false },
          ],
          onFilter: (value: any, record: T) => {
            if (column.dataIndex) {
              return (record as any)[column.dataIndex] === value;
            }
            return false;
          },
        };
      default:
        return {};
    }
  };

  // Get sorter
  const getSorter = (column: EnhancedColumnType<T>) => {
    if (!column.sortable) return undefined;
    
    return (a: T, b: T) => {
      if (column.dataIndex) {
        const aVal = (a as any)[column.dataIndex];
        const bVal = (b as any)[column.dataIndex];
        
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return aVal.localeCompare(bVal);
        }
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return aVal - bVal;
        }
        if (typeof aVal === 'boolean' && typeof bVal === 'boolean') {
          return (aVal ? 1 : 0) - (bVal ? 1 : 0);
        }
        return String(aVal).localeCompare(String(bVal));
      }
      return 0;
    };
  };

  // Enhanced columns
  const enhancedColumns = rawColumns.map(column => {
    const dataIndex = column.dataIndex as string;
    const key = column.key as string;
    
    const newColumn: EnhancedColumnType<T> = {
      ...column,
      key: key || dataIndex,
      ellipsis: column.ellipsis !== undefined ? column.ellipsis : true,
    };

    // Add search
    if (column.searchable && searchable) {
      newColumn.filterDropdown = getColumnSearchProps(dataIndex).filterDropdown;
      newColumn.filterIcon = getColumnSearchProps(dataIndex).filterIcon;
      newColumn.onFilter = getColumnSearchProps(dataIndex).onFilter;
    }

    // Add filter
    if (column.filterable && filterable) {
      Object.assign(newColumn, getColumnFilterProps(column));
    }

    // Add sorter
    if (column.sortable && sortable) {
      newColumn.sorter = getSorter(column);
    }

    // Custom renderers
    if (column.renderAsTag) {
      newColumn.render = (value: any) => {
        const color = column.tagColor ? column.tagColor(value) : '#1890ff';
        return <Tag color={color}>{value}</Tag>;
      };
    }

    if (column.renderAsStatus && column.statusMap) {
      newColumn.render = (value: any) => {
        const status = column.statusMap?.[String(value)];
        if (status) {
          return <Tag color={status.color}>{status.label}</Tag>;
        }
        return <Tag>{value}</Tag>;
      };
    }

    if (column.copyable) {
      const originalRender = newColumn.render;
      newColumn.render = (value: any, record: T, index: number) => {
        const rendered = originalRender ? originalRender(value, record, index) : value;
        return (
          <Tooltip title="Copy">
            <span
              style={{ cursor: 'pointer' }}
              onClick={(e) => {
                e.stopPropagation();
                navigator.clipboard.writeText(String(value));
              }}
            >
              {rendered}
            </span>
          </Tooltip>
        );
      };
    }

    return newColumn;
  }).filter(column => {
    const columnKey = (column.key || column.dataIndex) as string;
    return visibleColumns.includes(columnKey);
  });

  // Handle sort change
  const handleSortChange = (pagination: any, filters: any, sorter: any) => {
    if (sorter.field) {
      setSortConfig({
        key: sorter.field,
        order: sorter.order,
      });
    } else {
      setSortConfig(null);
    }
  };

  // Row selection
  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
  };

  // Bulk actions menu
  const bulkActionsMenu = (
    <Menu
      onClick={({ key }) => {
        if (onBulkAction) {
          const selectedRows = dataSource.filter((_, index) => 
            selectedRowKeys.includes(index)
          );
          onBulkAction(key, selectedRows);
        }
      }}
      items={bulkActions.map(action => ({
        key: action.key,
        label: action.label,
        icon: action.icon,
      }))}
    />
  );

  // Column selector menu
  const columnSelectorMenu = (
    <Menu
      onClick={({ key }) => {
        setVisibleColumns(prev => {
          if (prev.includes(key)) {
            return prev.filter(k => k !== key);
          }
          return [...prev, key];
        });
      }}
      items={rawColumns.map(column => {
        const columnKey = (column.key || column.dataIndex) as string;
        return {
          key: columnKey,
          label: (
            <Space>
              {visibleColumns.includes(columnKey) && <EyeOutlined style={{ color: '#52c41a' }} />}
              {column.title as React.ReactNode}
            </Space>
          ),
        };
      })}
    />
  );

  // Get filtered and sorted data
  const getProcessedData = () => {
    let processedData = [...dataSource];

    // Apply filters
    for (const [key, value] of Object.entries(filters)) {
      if (value) {
        processedData = processedData.filter(record => {
          const column = rawColumns.find(c => (c.key || c.dataIndex) === key);
          if (column?.dataIndex) {
            const recordValue = (record as any)[column.dataIndex];
            if (Array.isArray(value)) {
              return value.includes(recordValue);
            }
            return String(recordValue).toLowerCase().includes(String(value).toLowerCase());
          }
          return true;
        });
      }
    }

    // Apply search
    if (searchText && searchedColumn) {
      processedData = processedData.filter(record => {
        const column = rawColumns.find(c => (c.key || c.dataIndex) === searchedColumn);
        if (column?.dataIndex) {
          const recordValue = (record as any)[column.dataIndex];
          return String(recordValue).toLowerCase().includes(searchText.toLowerCase());
        }
        return true;
      });
    }

    // Apply sorting
    if (sortConfig) {
      const column = rawColumns.find(c => (c.key || c.dataIndex) === sortConfig.key);
      if (column?.sortable && column.dataIndex) {
        processedData.sort((a, b) => {
          const aVal = (a as any)[column.dataIndex];
          const bVal = (b as any)[column.dataIndex];
          
          if (sortConfig.order === 'ascend') {
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
          } else {
            return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
          }
        });
      }
    }

    return processedData;
  };

  const processedData = getProcessedData();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        bodyStyle={{ padding: 0 }}
        style={{ borderRadius: 12 }}
      >
        {/* Table Header */}
        <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <Space wrap>
            {searchable && (
              <Input
                placeholder="Search..."
                prefix={<SearchOutlined />}
                style={{ width: 250 }}
                onChange={(e) => {
                  setSearchText(e.target.value);
                  setSearchedColumn('');
                }}
              />
            )}
            
            {filterable && (
              <Dropdown overlay={columnSelectorMenu} trigger={['click']}>
                <Button icon={<ColumnHeightOutlined />}>Columns</Button>
              </Dropdown>
            )}
          </Space>

          <Space wrap>
            {selectedRowKeys.length > 0 && bulkActions.length > 0 && (
              <Dropdown overlay={bulkActionsMenu} trigger={['click']}>
                <Button>
                  Bulk Actions ({selectedRowKeys.length})
                </Button>
              </Dropdown>
            )}
            
            {exportable && onExport && (
              <Button icon={<ExportOutlined />} onClick={() => onExport(processedData)}>
                Export
              </Button>
            )}
            
            {refreshable && onRefresh && (
              <Button icon={<SyncOutlined />} onClick={onRefresh}>
                Refresh
              </Button>
            )}
          </Space>
        </div>

        {/* Table */}
        <Table
          columns={enhancedColumns}
          dataSource={processedData}
          rowKey={rowKey}
          pagination={{
            pageSize,
            showSizeChanger: true,
            pageSizeOptions,
            onChange: (page, newPageSize) => {
              if (newPageSize !== pageSize) {
                setPageSize(newPageSize || pageSizeOptions[0]);
              }
            },
          }}
          onChange={handleSortChange}
          rowSelection={showRowActions ? rowSelection : undefined}
          scroll={{ x: 'max-content' }}
          size="small"
          {...rest}
        />
      </Card>
    </motion.div>
  );
};

export default DataTable;
