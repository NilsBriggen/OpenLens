/**
 * Tag Input Component for OpenLens
 * 
 * A customizable tag input component that allows users to add, remove, and edit tags
 */

import React, { useState, useRef, useEffect } from 'react';
import { Input, Tag, Tooltip, Space, Button, Typography } from 'antd';
import { PlusOutlined, CloseOutlined, EditOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Text } = Typography;

interface TagItem {
  id?: string;
  label: string;
  value: string;
  color?: string;
  closable?: boolean;
  editable?: boolean;
  [key: string]: any;
}

interface TagInputProps {
  value?: TagItem[];
  onChange?: (tags: TagItem[]) => void;
  placeholder?: string;
  allowDuplicates?: boolean;
  allowEdit?: boolean;
  allowAdd?: boolean;
  allowRemove?: boolean;
  maxTags?: number;
  maxLength?: number;
  separator?: string | string[];
  color?: string;
  colors?: string[];
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  readOnly?: boolean;
  style?: React.CSSProperties;
  className?: string;
  inputProps?: any;
  tagProps?: any;
}

const TagInput: React.FC<TagInputProps> = ({
  value = [],
  onChange,
  placeholder = 'Add a tag',
  allowDuplicates = false,
  allowEdit = false,
  allowAdd = true,
  allowRemove = true,
  maxTags,
  maxLength,
  separator = [',', 'Enter'],
  color,
  colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#fa8c16'],
  size = 'default',
  disabled = false,
  readOnly = false,
  style = {},
  className = '',
  inputProps = {},
  tagProps = {},
}) => {
  const [inputValue, setInputValue] = useState('');
  const [editingTag, setEditingTag] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const inputRef = useRef<any>(null);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  // Handle input key down
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled || readOnly) return;

    // Check if separator key was pressed
    const separators = Array.isArray(separator) ? separator : [separator];
    const isSeparator = separators.some(s => {
      if (s === 'Enter') return e.key === 'Enter';
      if (s === ',') return e.key === ',';
      if (s === 'Tab') return e.key === 'Tab';
      return e.key === s;
    });

    if (isSeparator && inputValue.trim()) {
      e.preventDefault();
      handleAddTag(inputValue.trim());
    }

    // Handle backspace to remove last tag
    if (e.key === 'Backspace' && inputValue === '' && value.length > 0 && allowRemove) {
      handleRemoveTag(value[value.length - 1].id || value[value.length - 1].value);
    }
  };

  // Handle add tag
  const handleAddTag = (tagValue: string) => {
    if (!allowAdd || disabled || readOnly) return;

    // Check max tags
    if (maxTags && value.length >= maxTags) return;

    // Check max length
    if (maxLength && tagValue.length > maxLength) return;

    // Check for duplicates
    if (!allowDuplicates) {
      const exists = value.some(tag => tag.value === tagValue);
      if (exists) {
        setInputValue('');
        return;
      }
    }

    // Create new tag
    const newTag: TagItem = {
      id: `tag-${Date.now()}`,
      label: tagValue,
      value: tagValue,
      color: color || colors[value.length % colors.length],
      closable: allowRemove,
      editable: allowEdit,
    };

    // Update tags
    const newTags = [...value, newTag];
    if (onChange) {
      onChange(newTags);
    }

    setInputValue('');
  };

  // Handle remove tag
  const handleRemoveTag = (tagId: string) => {
    if (!allowRemove || disabled || readOnly) return;

    const newTags = value.filter(tag => tag.id !== tagId && tag.value !== tagId);
    if (onChange) {
      onChange(newTags);
    }
  };

  // Handle edit tag
  const handleEditTag = (tag: TagItem) => {
    if (!allowEdit || disabled || readOnly) return;

    setEditingTag(tag.id || tag.value);
    setEditValue(tag.label);
  };

  // Handle save edit
  const handleSaveEdit = (tagId: string) => {
    if (!allowEdit || disabled || readOnly) return;

    const newTags = value.map(tag => {
      if (tag.id === tagId || tag.value === tagId) {
        return {
          ...tag,
          label: editValue,
          value: editValue,
        };
      }
      return tag;
    });

    if (onChange) {
      onChange(newTags);
    }

    setEditingTag(null);
    setEditValue('');
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditingTag(null);
    setEditValue('');
  };

  // Focus input on edit
  useEffect(() => {
    if (editingTag && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editingTag]);

  // Get tag color
  const getTagColor = (tag: TagItem, index: number): string => {
    return tag.color || color || colors[index % colors.length];
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        border: '1px solid var(--border-color)',
        borderRadius: 8,
        padding: 8,
        background: 'var(--bg-color-secondary)',
        minHeight: 40,
        ...style,
      }}
      className={className}
    >
      <Space wrap>
        <AnimatePresence>
          {value.map((tag, index) => (
            <motion.div
              key={tag.id || tag.value}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.2 }}
            >
              {editingTag === (tag.id || tag.value) ? (
                <Input
                  ref={inputRef}
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onPressEnter={() => handleSaveEdit(tag.id || tag.value)}
                  onBlur={() => handleSaveEdit(tag.id || tag.value)}
                  size={size}
                  style={{ width: 'auto', minWidth: 100 }}
                  autoFocus
                />
              ) : (
                <Tooltip title={allowEdit ? 'Click to edit' : undefined}>
                  <Tag
                    color={getTagColor(tag, index)}
                    closable={allowRemove && tag.closable !== false}
                    onClose={() => handleRemoveTag(tag.id || tag.value)}
                    style={{
                      cursor: allowEdit ? 'pointer' : 'default',
                      ...tagProps?.style,
                    }}
                    onClick={() => allowEdit && handleEditTag(tag)}
                    {...tagProps}
                  >
                    {tag.label}
                  </Tag>
                </Tooltip>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {allowAdd && !readOnly && !disabled && (
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleInputKeyDown}
            placeholder={placeholder}
            size={size}
            style={{
              width: 'auto',
              minWidth: 100,
              flex: 1,
            }}
            disabled={disabled || (maxTags && value.length >= maxTags)}
            {...inputProps}
          />
        )}
      </Space>

      {maxTags && value.length >= maxTags && allowAdd && !readOnly && !disabled && (
        <Text type="secondary" style={{ fontSize: 12, marginTop: 4, display: 'block' }}>
          Maximum {maxTags} tags allowed
        </Text>
      )}
    </motion.div>
  );
};

// TagSelector component (select from predefined tags)
interface TagSelectorProps extends Omit<TagInputProps, 'value' | 'onChange'> {
  options?: TagItem[];
  selected?: TagItem[];
  onSelect?: (tags: TagItem[]) => void;
  searchable?: boolean;
  dropdownProps?: any;
}

export const TagSelector: React.FC<TagSelectorProps> = ({
  options = [],
  selected = [],
  onSelect,
  searchable = false,
  dropdownProps = {},
  ...props
}) => {
  const [searchValue, setSearchValue] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  // Filter options based on search
  const filteredOptions = searchable
    ? options.filter(option => 
        option.label.toLowerCase().includes(searchValue.toLowerCase())
      )
    : options;

  // Handle select option
  const handleSelectOption = (option: TagItem) => {
    const newSelected = [...selected, option];
    if (onSelect) {
      onSelect(newSelected);
    }
    setSearchValue('');
    setShowDropdown(false);
  };

  // Handle remove selected
  const handleRemoveSelected = (tagId: string) => {
    const newSelected = selected.filter(tag => tag.id !== tagId && tag.value !== tagId);
    if (onSelect) {
      onSelect(newSelected);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <TagInput
        value={selected}
        onChange={onSelect}
        placeholder="Select tags..."
        allowAdd={false}
        {...props}
      />

      {showDropdown && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          style={{
            border: '1px solid var(--border-color)',
            borderRadius: 8,
            padding: 8,
            marginTop: 8,
            background: 'var(--card-bg)',
            maxHeight: 200,
            overflowY: 'auto',
          }}
        >
          {searchable && (
            <Input
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Search tags..."
              size="small"
              style={{ marginBottom: 8 }}
              autoFocus
            />
          )}

          <Space wrap>
            {filteredOptions.map((option, index) => (
              <Tag
                key={option.id || option.value}
                color={option.color || props.colors?.[index % (props.colors?.length || 1)]}
                onClick={() => handleSelectOption(option)}
                style={{ cursor: 'pointer' }}
              >
                {option.label}
              </Tag>
            ))}
          </Space>
        </motion.div>
      )}
    </motion.div>
  );
};

// ChipInput component (alias for TagInput)
export const ChipInput: React.FC<TagInputProps> = (props) => {
  return <TagInput {...props} />;
};

export default TagInput;
