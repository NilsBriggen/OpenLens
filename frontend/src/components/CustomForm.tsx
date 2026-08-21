/**
 * Custom Form Component for OpenLens
 * 
 * A flexible, reusable form component with:
 * - Dynamic field generation
 * - Validation support
 * - Custom field types
 * - Form state management
 */

import React, { useState, useEffect } from 'react';
import { Form, Input, Select, DatePicker, Switch, Button, Space, Card, Typography, Upload, message, Checkbox, InputNumber, Radio } from 'antd';
import {
  PlusOutlined,
  MinusCircleOutlined,
  UploadOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Text, Title } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { TextArea } = Input;

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'password' | 'textarea' | 'select' | 'multiselect' | 'date' | 'range' | 'number' | 'switch' | 'checkbox' | 'radio' | 'file' | 'dynamic';
  placeholder?: string;
  required?: boolean;
  options?: { value: string | number; label: string }[];
  defaultValue?: any;
  rules?: any[];
  disabled?: boolean;
  hidden?: boolean;
  children?: FormField[];
  min?: number;
  max?: number;
  step?: number;
  rows?: number;
  accept?: string;
  multiple?: boolean;
}

interface CustomFormProps {
  fields: FormField[];
  initialValues?: Record<string, any>;
  onSubmit: (values: Record<string, any>) => void;
  onCancel?: () => void;
  submitText?: string;
  cancelText?: string;
  title?: string;
  loading?: boolean;
  layout?: 'horizontal' | 'vertical' | 'inline';
  formProps?: any;
}

const CustomForm: React.FC<CustomFormProps> = ({
  fields,
  initialValues = {},
  onSubmit,
  onCancel,
  submitText = 'Submit',
  cancelText = 'Cancel',
  title,
  loading = false,
  layout = 'vertical',
  formProps = {},
}) => {
  const [form] = Form.useForm();
  const [dynamicFields, setDynamicFields] = useState<Record<string, FormField[][]>>({});

  // Initialize form
  useEffect(() => {
    form.setFieldsValue(initialValues);
  }, [form, initialValues]);

  // Handle form submission
  const handleSubmit = async (values: Record<string, any>) => {
    try {
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  // Render field based on type
  const renderField = (field: FormField, index?: number) => {
    const fieldName = field.name;
    
    // Skip hidden fields
    if (field.hidden) return null;

    switch (field.type) {
      case 'text':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Input
              placeholder={field.placeholder}
              disabled={field.disabled}
            />
          </Form.Item>
        );

      case 'password':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Input.Password
              placeholder={field.placeholder}
              disabled={field.disabled}
            />
          </Form.Item>
        );

      case 'textarea':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <TextArea
              placeholder={field.placeholder}
              disabled={field.disabled}
              rows={field.rows || 4}
            />
          </Form.Item>
        );

      case 'select':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Select
              placeholder={field.placeholder || `Select ${field.label}`}
              disabled={field.disabled}
              allowClear
              options={field.options?.map(opt => ({
                value: opt.value,
                label: opt.label,
              }))}
            />
          </Form.Item>
        );

      case 'multiselect':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Select
              mode="multiple"
              placeholder={field.placeholder || `Select ${field.label}`}
              disabled={field.disabled}
              allowClear
              options={field.options?.map(opt => ({
                value: opt.value,
                label: opt.label,
              }))}
            />
          </Form.Item>
        );

      case 'date':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <DatePicker
              placeholder={field.placeholder || `Select ${field.label}`}
              disabled={field.disabled}
              style={{ width: '100%' }}
            />
          </Form.Item>
        );

      case 'range':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <RangePicker
              placeholder={[`Start ${field.label}`, `End ${field.label}`]}
              disabled={field.disabled}
              style={{ width: '100%' }}
            />
          </Form.Item>
        );

      case 'number':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <InputNumber
              placeholder={field.placeholder}
              disabled={field.disabled}
              min={field.min}
              max={field.max}
              step={field.step}
              style={{ width: '100%' }}
            />
          </Form.Item>
        );

      case 'switch':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            valuePropName="checked"
          >
            <Switch disabled={field.disabled} />
          </Form.Item>
        );

      case 'checkbox':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            valuePropName="checked"
          >
            <Checkbox disabled={field.disabled} />
          </Form.Item>
        );

      case 'radio':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Radio.Group disabled={field.disabled} options={field.options} />
          </Form.Item>
        );

      case 'file':
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
            rules={field.rules || (field.required ? [{ required: true, message: `${field.label} is required` }] : [])}
          >
            <Upload
              beforeUpload={() => false}
              accept={field.accept}
              multiple={field.multiple}
              showUploadList={true}
            >
              <Button icon={<UploadOutlined />}>Upload</Button>
            </Upload>
          </Form.Item>
        );

      case 'dynamic':
        return renderDynamicField(field, index || 0);

      default:
        return (
          <Form.Item
            key={fieldName}
            name={fieldName}
            label={field.label}
          >
            <Input placeholder={field.placeholder} />
          </Form.Item>
        );
    }
  };

  // Render dynamic field (repeatable)
  const renderDynamicField = (field: FormField, index: number) => {
    const fieldName = field.name;
    const children = field.children || [];
    
    return (
      <Form.List name={fieldName} initialValue={initialValues[fieldName] || [{}]}>
        {(fields, { add, remove }) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card size="small" style={{ marginBottom: 16 }}>
              <Title level={5} style={{ margin: 0, marginBottom: 16 }}>
                {field.label}
              </Title>
              
              {fields.map(({ key, name, ...restField }) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ marginBottom: 16 }}
                >
                  <Row gutter={16}>
                    <Col span={22}>
                      {children.map(childField => renderField({
                        ...childField,
                        name: `${name}.${childField.name}`,
                      }))}
                    </Col>
                    <Col span={2}>
                      <Button
                        type="text"
                        icon={<MinusCircleOutlined />}
                        onClick={() => remove(name)}
                        danger
                      />
                    </Col>
                  </Row>
                </motion.div>
              ))}

              <Button
                type="dashed"
                onClick={() => add()}
                block
                icon={<PlusOutlined />}
              >
                Add {field.label}
              </Button>
            </Card>
          </motion.div>
        )}
      </Form.List>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        title={title}
        bodyStyle={{ padding: 24 }}
        style={{ borderRadius: 12 }}
      >
        <Form
          form={form}
          layout={layout}
          onFinish={handleSubmit}
          {...formProps}
        >
          {fields.map((field, index) => (
            <motion.div
              key={field.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              {renderField(field, index)}
            </motion.div>
          ))}

          <Form.Item style={{ marginTop: 24 }}>
            <Space>
              {onCancel && (
                <Button onClick={onCancel} disabled={loading}>
                  {cancelText}
                </Button>
              )}
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
              >
                {submitText}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </motion.div>
  );
};

export default CustomForm;
