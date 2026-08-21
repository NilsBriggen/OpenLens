/**
 * CopyToClipboard Component for OpenLens
 * 
 * A reusable component that copies text to clipboard with feedback
 */

import React, { useState } from 'react';
import { Button, Tooltip, Input, Space, Typography, message } from 'antd';
import {
  CopyOutlined,
  CheckOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { copyToClipboard } from '../utils/uiUtils';

const { Text } = Typography;

interface CopyToClipboardProps {
  text: string;
  children?: React.ReactNode;
  onCopy?: () => void;
  onCopied?: () => void;
  tooltipText?: string;
  copiedTooltipText?: string;
  buttonProps?: any;
  showInput?: boolean;
  inputProps?: any;
  icon?: React.ReactNode;
  copiedIcon?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

const CopyToClipboard: React.FC<CopyToClipboardProps> = ({
  text,
  children,
  onCopy,
  onCopied,
  tooltipText = 'Copy to clipboard',
  copiedTooltipText = 'Copied!',
  buttonProps = {},
  showInput = false,
  inputProps = {},
  icon = <CopyOutlined />,
  copiedIcon = <CheckOutlined />,
  style = {},
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [copying, setCopying] = useState(false);

  // Handle copy
  const handleCopy = async () => {
    if (copying) return;

    setCopying(true);

    try {
      const success = await copyToClipboard(text);
      
      if (success) {
        setCopied(true);
        if (onCopied) {
          onCopied();
        }
        
        // Reset after 2 seconds
        setTimeout(() => {
          setCopied(false);
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to copy:', error);
      message.error('Failed to copy to clipboard');
    } finally {
      setCopying(false);
      if (onCopy) {
        onCopy();
      }
    }
  };

  // Render with input
  if (showInput) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={style}
        className={className}
      >
        <Input
          value={text}
          readOnly
          addonAfter={
            <Tooltip title={copied ? copiedTooltipText : tooltipText}>
              <Button
                type="text"
                icon={copied ? copiedIcon : icon}
                onClick={handleCopy}
                loading={copying}
                style={{ color: copied ? '#52c41a' : undefined }}
                {...buttonProps}
              />
            </Tooltip>
          }
          {...inputProps}
        />
      </motion.div>
    );
  }

  // Render with children
  if (children) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={style}
        className={className}
        onClick={handleCopy}
      >
        <Tooltip title={copied ? copiedTooltipText : tooltipText}>
          <span style={{ cursor: 'pointer' }}>
            {children}
          </span>
        </Tooltip>
      </motion.div>
    );
  }

  // Default render (button)
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
      className={className}
    >
      <Tooltip title={copied ? copiedTooltipText : tooltipText}>
        <Button
          icon={copied ? copiedIcon : icon}
          onClick={handleCopy}
          loading={copying}
          style={{ color: copied ? '#52c41a' : undefined }}
          {...buttonProps}
        />
      </Tooltip>
    </motion.div>
  );
};

// CopyText component (displays text with copy button)
interface CopyTextProps {
  text: string;
  maxLength?: number;
  showFullOnHover?: boolean;
  onCopy?: () => void;
  onCopied?: () => void;
  style?: React.CSSProperties;
  textStyle?: React.CSSProperties;
  buttonStyle?: React.CSSProperties;
}

export const CopyText: React.FC<CopyTextProps> = ({
  text,
  maxLength,
  showFullOnHover = true,
  onCopy,
  onCopied,
  style = {},
  textStyle = {},
  buttonStyle = {},
}) => {
  const [copied, setCopied] = useState(false);
  const [hover, setHover] = useState(false);

  // Get display text
  const displayText = maxLength && !hover ? (
    text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  ) : text;

  // Handle copy
  const handleCopy = async () => {
    const success = await copyToClipboard(text);
    
    if (success) {
      setCopied(true);
      if (onCopied) {
        onCopied();
      }
      
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }
    
    if (onCopy) {
      onCopy();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        ...style,
      }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <Tooltip title={showFullOnHover && maxLength && text.length > maxLength ? text : undefined}>
        <Text
          code
          style={{
            cursor: 'pointer',
            ...textStyle,
          }}
          onClick={handleCopy}
        >
          {displayText}
        </Text>
      </Tooltip>
      
      <Tooltip title={copied ? 'Copied!' : 'Copy to clipboard'}>
        <Button
          type="text"
          icon={copied ? <CheckOutlined style={{ color: '#52c41a' }} /> : <CopyOutlined />}
          onClick={handleCopy}
          size="small"
          style={{
            padding: 0,
            height: 'auto',
            ...buttonStyle,
          }}
        />
      </Tooltip>
    </motion.div>
  );
};

// CopyButton component (simple button that copies text)
interface CopyButtonProps {
  text: string;
  children?: React.ReactNode;
  onCopy?: () => void;
  onCopied?: () => void;
  type?: 'primary' | 'default' | 'dashed' | 'text' | 'link';
  size?: 'large' | 'middle' | 'small';
  icon?: React.ReactNode;
  style?: React.CSSProperties;
}

export const CopyButton: React.FC<CopyButtonProps> = ({
  text,
  children,
  onCopy,
  onCopied,
  type = 'default',
  size = 'small',
  icon = <CopyOutlined />,
  style = {},
}) => {
  const [copied, setCopied] = useState(false);

  // Handle copy
  const handleCopy = async () => {
    const success = await copyToClipboard(text);
    
    if (success) {
      setCopied(true);
      if (onCopied) {
        onCopied();
      }
      
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }
    
    if (onCopy) {
      onCopy();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.2 }}
      style={style}
    >
      <Button
        type={type}
        size={size}
        icon={copied ? <CheckOutlined style={{ color: '#52c41a' }} /> : icon}
        onClick={handleCopy}
      >
        {children}
      </Button>
    </motion.div>
  );
};

export default CopyToClipboard;
