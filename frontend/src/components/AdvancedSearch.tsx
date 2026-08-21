import React, { useState, useEffect } from 'react';
import { Input, Button, Space, Select, DatePicker, Form, Card, Row, Col, Tag, Tooltip, Typography } from 'antd';

const { Text } = Typography;
import {
  SearchOutlined,
  FilterOutlined,
  CloseOutlined,
  PlusOutlined,
  MinusOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Search } = Input;
const { RangePicker } = DatePicker;
const { Option } = Select;

interface FilterField {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'number' | 'boolean';
  options?: { value: string | number; label: string }[];
  placeholder?: string;
}

interface AdvancedSearchProps {
  placeholder?: string;
  filterFields?: FilterField[];
  onSearch: (values: Record<string, any>) => void;
  onReset: () => void;
  initialValues?: Record<string, any>;
  loading?: boolean;
  showAdvanced?: boolean;
}

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  placeholder = 'Search...',
  filterFields = [],
  onSearch,
  onReset,
  initialValues = {},
  loading = false,
  showAdvanced = true,
}) => {
  const [advancedVisible, setAdvancedVisible] = useState(false);
  const [formValues, setFormValues] = useState<Record<string, any>>(initialValues);
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});

  // Update form values
  const handleValueChange = (key: string, value: any) => {
    setFormValues(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  // Add filter
  const addFilter = (field: FilterField) => {
    setActiveFilters(prev => ({
      ...prev,
      [field.key]: field,
    }));
  };

  // Remove filter
  const removeFilter = (key: string) => {
    const newFilters = { ...activeFilters };
    delete newFilters[key];
    setActiveFilters(newFilters);
    const newValues = { ...formValues };
    delete newValues[key];
    setFormValues(newValues);
  };

  // Handle search
  const handleSearch = () => {
    onSearch(formValues);
  };

  // Handle reset
  const handleReset = () => {
    setFormValues({});
    setActiveFilters({});
    onReset();
  };

  // Render filter input based on type
  const renderFilterInput = (field: FilterField) => {
    switch (field.type) {
      case 'select':
        return (
          <Select
            value={formValues[field.key]}
            onChange={(value) => handleValueChange(field.key, value)}
            options={field.options || []}
            placeholder={field.placeholder || `Select ${field.label}`}
            allowClear
            style={{ width: '100%' }}
          />
        );
      case 'date':
        return (
          <RangePicker
            value={formValues[field.key]}
            onChange={(value) => handleValueChange(field.key, value)}
            style={{ width: '100%' }}
            placeholder={[`Start ${field.label}`, `End ${field.label}`]}
          />
        );
      case 'number':
        return (
          <Input
            type="number"
            value={formValues[field.key]}
            onChange={(e) => handleValueChange(field.key, e.target.value ? Number(e.target.value) : undefined)}
            placeholder={field.placeholder || `Enter ${field.label}`}
            style={{ width: '100%' }}
          />
        );
      case 'boolean':
        return (
          <Select
            value={formValues[field.key]}
            onChange={(value) => handleValueChange(field.key, value)}
            options={[
              { value: true, label: 'Yes' },
              { value: false, label: 'No' },
            ]}
            placeholder={field.placeholder || `Select ${field.label}`}
            allowClear
            style={{ width: '100%' }}
          />
        );
      case 'text':
      default:
        return (
          <Input
            value={formValues[field.key]}
            onChange={(e) => handleValueChange(field.key, e.target.value)}
            placeholder={field.placeholder || `Enter ${field.label}`}
            style={{ width: '100%' }}
          />
        );
    }
  };

  // Available filter fields
  const availableFields = filterFields.filter(f => !activeFilters[f.key]);

  return (
    <Card size="small" style={{ marginBottom: 24 }}>
      <Space wrap>
        {/* Main Search */}
        <Search
          placeholder={placeholder}
          value={formValues.search}
          onChange={(e) => handleValueChange('search', e.target.value)}
          onSearch={handleSearch}
          enterButton
          loading={loading}
          style={{ flex: 1, minWidth: 250 }}
        />

        {/* Advanced Toggle */}
        {showAdvanced && (
          <Button
            type={advancedVisible ? 'primary' : 'default'}
            icon={<FilterOutlined />}
            onClick={() => setAdvancedVisible(!advancedVisible)}
          >
            Advanced
          </Button>
        )}

        {/* Reset Button */}
        <Button onClick={handleReset} icon={<CloseOutlined />}>
          Reset
        </Button>
      </Space>

      {/* Advanced Filters */}
      <AnimatePresence>
        {advancedVisible && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}
          >
            {/* Active Filters */}
            {Object.keys(activeFilters).length > 0 && (
              <div style={{ marginBottom: 16 }}>
                <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
                  Active Filters:
                </Text>
                <Space wrap>
                  {Object.entries(activeFilters).map(([key, field]) => (
                    <Tag
                      key={key}
                      closable
                      onClose={() => removeFilter(key)}
                      style={{ padding: '4px 8px' }}
                    >
                      <Space>
                        {field.label}
                        {formValues[key] && (
                          <span style={{ fontWeight: 'bold' }}>
                            {typeof formValues[key] === 'object' 
                              ? JSON.stringify(formValues[key])
                              : String(formValues[key])}
                          </span>
                        )}
                      </Space>
                    </Tag>
                  ))}
                </Space>
              </div>
            )}

            {/* Filter Selection */}
            <Row gutter={16}>
              <Col span={24}>
                <Space wrap>
                  {Object.keys(activeFilters).length < filterFields.length && (
                    <Select
                      placeholder="Add filter..."
                      style={{ width: 200 }}
                      onChange={(value) => {
                        const field = filterFields.find(f => f.key === value);
                        if (field) {
                          addFilter(field);
                        }
                      }}
                      options={availableFields.map(f => ({
                        value: f.key,
                        label: f.label,
                      }))}
                      allowClear
                    />
                  )}
                </Space>
              </Col>
            </Row>

            {/* Filter Inputs */}
            {Object.keys(activeFilters).length > 0 && (
              <Row gutter={16} style={{ marginTop: 16 }}>
                {Object.entries(activeFilters).map(([key, field]) => (
                  <Col key={key} span={24} lg={12} xl={8}>
                    <Form.Item label={field.label} style={{ marginBottom: 8 }}>
                      {renderFilterInput(field)}
                    </Form.Item>
                  </Col>
                ))}
              </Row>
            )}

            {/* Search Button */}
            <Row style={{ marginTop: 16 }}>
              <Col span={24}>
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                  block
                >
                  Search
                </Button>
              </Col>
            </Row>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default AdvancedSearch;
