/**
 * Toggle Switch Component for OpenLens
 * 
 * A customizable toggle switch component with various styles and sizes
 */

import React from 'react';
import { Switch, Typography, Space, Tooltip } from 'antd';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface ToggleSwitchProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  loading?: boolean;
  size?: 'small' | 'default' | 'large';
  checkedChildren?: React.ReactNode;
  unCheckedChildren?: React.ReactNode;
  defaultChecked?: boolean;
  style?: React.CSSProperties;
  className?: string;
  label?: string;
  labelPosition?: 'left' | 'right' | 'top' | 'bottom';
  tooltip?: string;
  onText?: string;
  offText?: string;
  width?: number;
  height?: number;
  onColor?: string;
  offColor?: string;
  handleColor?: string;
}

const ToggleSwitch: React.FC<ToggleSwitchProps> = ({
  checked = false,
  onChange,
  disabled = false,
  loading = false,
  size = 'default',
  checkedChildren,
  unCheckedChildren,
  defaultChecked,
  style = {},
  className = '',
  label,
  labelPosition = 'right',
  tooltip,
  onText,
  offText,
  width,
  height,
  onColor = '#1890ff',
  offColor = '#d9d9d9',
  handleColor = '#fff',
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { width: number; height: number; handle: number }> = {
      small: { width: 32, height: 16, handle: 12 },
      default: { width: 44, height: 20, handle: 16 },
      large: { width: 56, height: 24, handle: 20 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Build content based on label position
  const buildContent = () => {
    const switchElement = (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Tooltip title={tooltip}>
          <Switch
            checked={checked}
            onChange={onChange}
            disabled={disabled}
            loading={loading}
            size={size === 'large' ? 'default' : size}
            checkedChildren={checkedChildren || (onText ? <Text style={{ fontSize: 10 }}>{onText}</Text> : undefined)}
            unCheckedChildren={unCheckedChildren || (offText ? <Text style={{ fontSize: 10 }}>{offText}</Text> : undefined)}
            defaultChecked={defaultChecked}
            style={{
              ...style,
              // Custom styling would go here
            }}
            className={className}
          />
        </Tooltip>
      </motion.div>
    );

    if (!label) {
      return switchElement;
    }

    switch (labelPosition) {
      case 'left':
        return (
          <Space align="center">
            <Text style={{ fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 }}>
              {label}
            </Text>
            {switchElement}
          </Space>
        );

      case 'right':
        return (
          <Space align="center">
            {switchElement}
            <Text style={{ fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 }}>
              {label}
            </Text>
          </Space>
        );

      case 'top':
        return (
          <Space direction="vertical" align="center">
            <Text style={{ fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 }}>
              {label}
            </Text>
            {switchElement}
          </Space>
        );

      case 'bottom':
        return (
          <Space direction="vertical" align="center">
            {switchElement}
            <Text style={{ fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 }}>
              {label}
            </Text>
          </Space>
        );

      default:
        return (
          <Space align="center">
            {switchElement}
            <Text style={{ fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14 }}>
              {label}
            </Text>
          </Space>
        );
    }
  };

  return buildContent();
};

// Custom Toggle Switch (fully customizable)
interface CustomToggleProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  loading?: boolean;
  size?: 'small' | 'default' | 'large';
  width?: number;
  height?: number;
  onColor?: string;
  offColor?: string;
  handleColor?: string;
  onText?: string;
  offText?: string;
  showText?: boolean;
  textPosition?: 'left' | 'right' | 'inside';
  style?: React.CSSProperties;
  className?: string;
}

export const CustomToggle: React.FC<CustomToggleProps> = ({
  checked = false,
  onChange,
  disabled = false,
  loading = false,
  size = 'default',
  width,
  height,
  onColor = '#1890ff',
  offColor = '#d9d9d9',
  handleColor = '#fff',
  onText,
  offText,
  showText = false,
  textPosition = 'right',
  style = {},
  className = '',
}) => {
  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { width: number; height: number; handle: number; text: number }> = {
      small: { width: 40, height: 20, handle: 14, text: 10 },
      default: { width: 50, height: 24, handle: 18, text: 12 },
      large: { width: 60, height: 28, handle: 22, text: 14 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Get actual dimensions
  const actualWidth = width || sizeStyles.width;
  const actualHeight = height || sizeStyles.height;
  const handleSize = sizeStyles.handle;

  // Calculate handle position
  const handlePosition = checked 
    ? actualWidth - handleSize - (actualHeight - handleSize) / 2
    : (actualHeight - handleSize) / 2;

  // Handle click
  const handleClick = () => {
    if (disabled || loading) return;
    if (onChange) {
      onChange(!checked);
    }
  };

  // Build content
  const buildContent = () => {
    // Text to display
    const text = checked ? onText : offText;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          cursor: disabled || loading ? 'not-allowed' : 'pointer',
          ...style,
        }}
        className={className}
        onClick={handleClick}
      >
        {showText && textPosition === 'left' && (
          <Text style={{ fontSize: sizeStyles.text }}>
            {text}
          </Text>
        )}

        {/* Switch */}
        <div
          style={{
            position: 'relative',
            width: actualWidth,
            height: actualHeight,
            borderRadius: actualHeight / 2,
            background: checked ? onColor : offColor,
            transition: 'background 0.3s ease',
            opacity: disabled ? 0.5 : 1,
          }}
        >
          {/* Handle */}
          <motion.div
            style={{
              position: 'absolute',
              top: (actualHeight - handleSize) / 2,
              left: handlePosition,
              width: handleSize,
              height: handleSize,
              borderRadius: '50%',
              background: handleColor,
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.3)',
            }}
            animate={{ left: handlePosition }}
            transition={{ duration: 0.2 }}
          />

          {/* Text inside */}
          {showText && textPosition === 'inside' && (
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: checked ? actualWidth - handleSize - 4 : handleSize + 4,
                transform: 'translateY(-50%)',
                fontSize: sizeStyles.text * 0.8,
                color: checked 
                  ? (handleColor === '#fff' ? onColor : handleColor)
                  : (handleColor === '#fff' ? offColor : handleColor),
                whiteSpace: 'nowrap',
              }}
            >
              {text}
            </div>
          )}
        </div>

        {showText && textPosition === 'right' && (
          <Text style={{ fontSize: sizeStyles.text }}>
            {text}
          </Text>
        )}

        {loading && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <div
              style={{
                width: 12,
                height: 12,
                border: '2px solid rgba(255, 255, 255, 0.3)',
                borderTop: '2px solid #fff',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
              }}
            />
          </div>
        )}
      </motion.div>
    );
  };

  return buildContent();
};

// Toggle Group (multiple toggles grouped together)
interface ToggleGroupProps {
  options: { value: string; label: string; disabled?: boolean }[];
  value?: string | string[];
  onChange?: (value: string | string[]) => void;
  multiple?: boolean;
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const ToggleGroup: React.FC<ToggleGroupProps> = ({
  options = [],
  value,
  onChange,
  multiple = false,
  size = 'default',
  disabled = false,
  style = {},
  className = '',
}) => {
  // Handle toggle
  const handleToggle = (optionValue: string) => {
    if (disabled) return;

    if (multiple) {
      const currentValues = Array.isArray(value) ? value : [];
      const newValues = currentValues.includes(optionValue)
        ? currentValues.filter(v => v !== optionValue)
        : [...currentValues, optionValue];
      if (onChange) {
        onChange(newValues);
      }
    } else {
      const newValue = value === optionValue ? undefined : optionValue;
      if (onChange) {
        onChange(newValue || '');
      }
    }
  };

  // Check if option is selected
  const isSelected = (optionValue: string): boolean => {
    if (multiple) {
      return Array.isArray(value) 
        ? value.includes(optionValue) 
        : false;
    }
    return value === optionValue;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'inline-flex',
        gap: 8,
        ...style,
      }}
      className={className}
    >
      {options.map((option, index) => (
        <motion.div
          key={option.value}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <ToggleSwitch
            checked={isSelected(option.value)}
            onChange={() => handleToggle(option.value)}
            disabled={disabled || option.disabled}
            size={size === 'large' ? 'default' : size}
            label={option.label}
            labelPosition="right"
            onColor="#1890ff"
            offColor="#d9d9d9"
          />
        </motion.div>
      ))}
    </motion.div>
  );
};

// OnOffToggle (simple on/off toggle)
interface OnOffToggleProps {
  checked?: boolean;
  onChange?: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'small' | 'default' | 'large';
  onText?: string;
  offText?: string;
  style?: React.CSSProperties;
  className?: string;
}

export const OnOffToggle: React.FC<OnOffToggleProps> = ({
  checked = false,
  onChange,
  disabled = false,
  size = 'default',
  onText = 'ON',
  offText = 'OFF',
  style = {},
  className = '',
}) => {
  return (
    <CustomToggle
      checked={checked}
      onChange={onChange}
      disabled={disabled}
      size={size === 'large' ? 'default' : size}
      onColor="#52c41a"
      offColor="#f5222d"
      onText={onText}
      offText={offText}
      showText={true}
      textPosition="inside"
      style={style}
      className={className}
    />
  );
};

export default ToggleSwitch;
