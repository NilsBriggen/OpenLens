/**
 * Color Picker Component for OpenLens
 * 
 * A customizable color picker component with various input methods
 */

import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Space, Tooltip, Typography, Popover, Card, Row, Col } from 'antd';
import { SketchPicker, ChromePicker, TwitterPicker, GithubPicker, BlockPicker, CirclePicker, CompactPicker, SwatchesPicker, AlphaPicker, HuePicker } from 'react-color';
import { motion } from 'framer-motion';

const { Text, Title } = Typography;

interface ColorPickerProps {
  value?: string;
  onChange?: (color: string) => void;
  type?: 'sketch' | 'chrome' | 'twitter' | 'github' | 'block' | 'circle' | 'compact' | 'swatches' | 'alpha' | 'hue';
  colors?: string[];
  width?: string | number;
  disableAlpha?: boolean;
  presetColors?: string[];
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  readOnly?: boolean;
  showInput?: boolean;
  showPreview?: boolean;
  previewSize?: number;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';
  trigger?: 'click' | 'hover' | 'focus';
  style?: React.CSSProperties;
  className?: string;
  inputProps?: any;
  buttonProps?: any;
}

const ColorPicker: React.FC<ColorPickerProps> = ({
  value = '#1890ff',
  onChange,
  type = 'sketch',
  colors,
  width,
  disableAlpha = false,
  presetColors = [
    '#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1',
    '#fa8c16', '#eb2f96', '#13c2c2', '#52c41a', '#f5222d'
  ],
  size = 'default',
  disabled = false,
  readOnly = false,
  showInput = true,
  showPreview = true,
  previewSize = 32,
  placement = 'bottom',
  trigger = 'click',
  style = {},
  className = '',
  inputProps = {},
  buttonProps = {},
}) => {
  const [visible, setVisible] = useState(false);
  const [internalValue, setInternalValue] = useState(value);

  // Sync internal value with external value
  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Handle color change
  const handleColorChange = (color: any) => {
    const newColor = color.hex || color.rgb || color;
    const hexColor = typeof newColor === 'string' 
      ? newColor 
      : `rgba(${newColor.r}, ${newColor.g}, ${newColor.b}, ${newColor.a || 1})`;
    
    setInternalValue(hexColor);
    if (onChange) {
      onChange(hexColor);
    }
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    if (onChange) {
      onChange(newValue);
    }
  };

  // Get picker component based on type
  const getPicker = () => {
    // Typed as any: each react-color picker accepts a different prop
    // subset; extras are ignored at runtime.
    const commonProps: any = {
      color: internalValue,
      onChange: handleColorChange,
      disableAlpha,
      // @types/react-color types width as a string; coerce numbers.
      width: ((): string | undefined => {
        const w = width ?? (type === 'sketch' || type === 'chrome' ? 300 : undefined);
        return typeof w === 'number' ? `${w}px` : w;
      })(),
      colors: presetColors,
    };

    switch (type) {
      case 'sketch':
        return <SketchPicker {...commonProps} presetColors={presetColors} />;
      case 'chrome':
        return <ChromePicker {...commonProps} />;
      case 'twitter':
        return <TwitterPicker {...commonProps} />;
      case 'github':
        return <GithubPicker {...commonProps} />;
      case 'block':
        return <BlockPicker {...commonProps} />;
      case 'circle':
        return <CirclePicker {...commonProps} />;
      case 'compact':
        return <CompactPicker {...commonProps} />;
      case 'swatches':
        return <SwatchesPicker {...commonProps} />;
      case 'alpha':
        return <AlphaPicker {...commonProps} />;
      case 'hue':
        return <HuePicker {...commonProps} />;
      default:
        return <SketchPicker {...commonProps} presetColors={presetColors} />;
    }
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { input: number; button: number; preview: number }> = {
      small: { input: 24, button: 24, preview: 24 },
      default: { input: 32, button: 32, preview: 32 },
      large: { input: 40, button: 40, preview: 40 },
    };
    return sizes[size] || sizes.default;
  };

  const sizeStyles = getSizeStyles();

  // Build content
  const content = (
    <Card
      size="small"
      bodyStyle={{ padding: 16 }}
      style={{ width: width || (type === 'sketch' || type === 'chrome' ? 320 : 250) }}
    >
      {getPicker()}
      
      {showInput && (
        <Input
          value={internalValue}
          onChange={handleInputChange}
          size={size}
          style={{ marginTop: 16 }}
          {...inputProps}
        />
      )}
    </Card>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Popover
        content={content}
        open={visible}
        onOpenChange={setVisible}
        placement={placement}
        trigger={trigger}
      >
        <Space>
          {showPreview && (
            <div
              style={{
                width: previewSize || sizeStyles.preview,
                height: previewSize || sizeStyles.preview,
                borderRadius: 4,
                background: internalValue,
                border: '1px solid var(--border-color)',
                cursor: disabled || readOnly ? 'default' : 'pointer',
              }}
            />
          )}
          
          {showInput && (
            <Input
              value={internalValue}
              onChange={handleInputChange}
              size={size}
              style={{ width: 100 }}
              disabled={disabled || readOnly}
              {...inputProps}
            />
          )}
          
          {!showInput && (
            <Button
              size={size}
              disabled={disabled || readOnly}
              {...buttonProps}
            >
              Select Color
            </Button>
          )}
        </Space>
      </Popover>
    </motion.div>
  );
};

// ColorSwatch component (displays a color swatch)
interface ColorSwatchProps {
  color: string;
  size?: number;
  shape?: 'circle' | 'square' | 'round';
  onClick?: () => void;
  selected?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const ColorSwatch: React.FC<ColorSwatchProps> = ({
  color,
  size = 32,
  shape = 'square',
  onClick,
  selected = false,
  style = {},
  className = '',
}) => {
  const getShapeStyles = () => {
    switch (shape) {
      case 'circle':
        return { borderRadius: '50%' };
      case 'round':
        return { borderRadius: 8 };
      case 'square':
      default:
        return { borderRadius: 0 };
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={{
        width: size,
        height: size,
        background: color,
        cursor: onClick ? 'pointer' : 'default',
        border: selected ? '2px solid #1890ff' : '1px solid var(--border-color)',
        ...getShapeStyles(),
        ...style,
      }}
      className={className}
      onClick={onClick}
    />
  );
};

// ColorSwatches component (displays multiple color swatches)
interface ColorSwatchesProps {
  colors: string[];
  selected?: string;
  onSelect?: (color: string) => void;
  size?: number;
  shape?: 'circle' | 'square' | 'round';
  columns?: number;
  gap?: number;
  style?: React.CSSProperties;
  className?: string;
}

export const ColorSwatches: React.FC<ColorSwatchesProps> = ({
  colors = [],
  selected,
  onSelect,
  size = 32,
  shape = 'square',
  columns = 5,
  gap = 8,
  style = {},
  className = '',
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap,
        ...style,
      }}
      className={className}
    >
      {colors.map((color, index) => (
        <ColorSwatch
          key={index}
          color={color}
          size={size}
          shape={shape}
          onClick={() => onSelect && onSelect(color)}
          selected={selected === color}
        />
      ))}
    </motion.div>
  );
};

// GradientPicker component
interface GradientPickerProps {
  value?: string;
  onChange?: (gradient: string) => void;
  presets?: string[];
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  className?: string;
}

export const GradientPicker: React.FC<GradientPickerProps> = ({
  value = 'linear-gradient(45deg, #1890ff, #722ed1)',
  onChange,
  presets = [
    'linear-gradient(45deg, #1890ff, #722ed1)',
    'linear-gradient(45deg, #52c41a, #1890ff)',
    'linear-gradient(45deg, #faad14, #f5222d)',
    'linear-gradient(45deg, #fa8c16, #eb2f96)',
    'linear-gradient(45deg, #13c2c2, #52c41a)',
    'linear-gradient(45deg, #722ed1, #faad14)',
  ],
  size = 'default',
  style = {},
  className = '',
}) => {
  const [internalValue, setInternalValue] = useState(value);

  // Sync internal value with external value
  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Handle preset select
  const handlePresetSelect = (gradient: string) => {
    setInternalValue(gradient);
    if (onChange) {
      onChange(gradient);
    }
  };

  // Get size styles
  const getSizeStyles = () => {
    const sizes: Record<string, { swatch: number; preview: number }> = {
      small: { swatch: 24, preview: 100 },
      default: { swatch: 32, preview: 150 },
      large: { swatch: 40, preview: 200 },
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
      <Space direction="vertical">
        {/* Preview */}
        <div
          style={{
            width: sizeStyles.preview,
            height: sizeStyles.preview / 2,
            background: internalValue,
            borderRadius: 8,
            border: '1px solid var(--border-color)',
          }}
        />

        {/* Presets */}
        <Space wrap>
          {presets.map((preset, index) => (
            <div
              key={index}
              style={{
                width: sizeStyles.swatch,
                height: sizeStyles.swatch,
                background: preset,
                borderRadius: 4,
                border: internalValue === preset ? '2px solid #1890ff' : '1px solid var(--border-color)',
                cursor: 'pointer',
              }}
              onClick={() => handlePresetSelect(preset)}
            />
          ))}
        </Space>
      </Space>
    </motion.div>
  );
};

export default ColorPicker;
