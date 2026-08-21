/**
 * Modal Dialog Component for OpenLens
 * 
 * A flexible, reusable modal component with:
 * - Customizable size and styling
 * - Footer with action buttons
 * - Support for forms
 * - Confirmation dialogs
 */

import React, { useState, useEffect } from 'react';
import { Modal, Button, Space, Typography, Divider } from 'antd';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface ModalDialogProps {
  visible: boolean;
  onClose: () => void;
  title?: string | React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  width?: number | string;
  size?: 'small' | 'medium' | 'large' | 'full';
  centered?: boolean;
  maskClosable?: boolean;
  closable?: boolean;
  destroyOnClose?: boolean;
  keyboard?: boolean;
  style?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  headerStyle?: React.CSSProperties;
  footerStyle?: React.CSSProperties;
  onOk?: () => void;
  onCancel?: () => void;
  okText?: string;
  cancelText?: string;
  okButtonProps?: any;
  cancelButtonProps?: any;
  loading?: boolean;
}

const ModalDialog: React.FC<ModalDialogProps> = ({
  visible,
  onClose,
  title,
  children,
  footer,
  width,
  size = 'medium',
  centered = true,
  maskClosable = true,
  closable = true,
  destroyOnClose = true,
  keyboard = true,
  style = {},
  bodyStyle = {},
  headerStyle = {},
  footerStyle = {},
  onOk,
  onCancel,
  okText = 'OK',
  cancelText = 'Cancel',
  okButtonProps = {},
  cancelButtonProps = {},
  loading = false,
}) => {
  // Determine width based on size
  const getWidth = () => {
    switch (size) {
      case 'small': return width || 400;
      case 'medium': return width || 600;
      case 'large': return width || 800;
      case 'full': return width || '90vw';
      default: return width || 600;
    }
  };

  // Handle close
  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  // Handle cancel
  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    handleClose();
  };

  // Handle ok
  const handleOk = () => {
    if (onOk) {
      onOk();
    }
    handleClose();
  };

  return (
    <Modal
      open={visible}
      onCancel={handleCancel}
      title={title}
      footer={footer !== undefined ? footer : (
        <Space>
          <Button onClick={handleCancel} disabled={loading} {...cancelButtonProps}>
            {cancelText}
          </Button>
          <Button
            type="primary"
            onClick={handleOk}
            loading={loading}
            {...okButtonProps}
          >
            {okText}
          </Button>
        </Space>
      )}
      width={getWidth()}
      centered={centered}
      maskClosable={maskClosable}
      closable={closable}
      destroyOnClose={destroyOnClose}
      keyboard={keyboard}
      style={{ borderRadius: 12, ...style }}
      styles={{
        body: { padding: 24, ...bodyStyle },
        header: headerStyle,
        footer: footerStyle,
      }}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: -20 }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.div>
    </Modal>
  );
};

// Confirmation Dialog Component
interface ConfirmDialogProps {
  visible: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message?: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  loading?: boolean;
  danger?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  visible,
  onClose,
  onConfirm,
  title = 'Confirm',
  message = 'Are you sure you want to perform this action?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  type = 'info',
  loading = false,
  danger = false,
}) => {
  const getIcon = () => {
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return 'ℹ';
    }
  };

  const getColor = () => {
    switch (type) {
      case 'success': return '#52c41a';
      case 'warning': return '#faad14';
      case 'error': return '#f5222d';
      default: return '#1890ff';
    }
  };

  return (
    <ModalDialog
      visible={visible}
      onClose={onClose}
      title={title}
      size="small"
      onOk={onConfirm}
      onCancel={onClose}
      okText={confirmText}
      cancelText={cancelText}
      okButtonProps={{ danger, type: danger ? 'primary' : undefined }}
      loading={loading}
    >
      <div style={{ textAlign: 'center', padding: 24 }}>
        <div
          style={{
            width: 60,
            height: 60,
            borderRadius: '50%',
            background: getColor(),
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
            fontSize: 24,
            color: '#fff',
          }}
        >
          {getIcon()}
        </div>
        <Text style={{ fontSize: 16 }}>
          {message}
        </Text>
      </div>
    </ModalDialog>
  );
};

// Form Modal Component
interface FormModalProps extends Omit<ModalDialogProps, 'footer'> {
  form: React.ReactNode;
  onSubmit: () => void;
  submitText?: string;
  showCancel?: boolean;
}

export const FormModal: React.FC<FormModalProps> = ({
  visible,
  onClose,
  title,
  form,
  onSubmit,
  submitText = 'Submit',
  showCancel = true,
  loading = false,
  ...props
}) => {
  return (
    <ModalDialog
      visible={visible}
      onClose={onClose}
      title={title}
      footer={null}
      loading={loading}
      {...props}
    >
      {form}
      <Divider style={{ margin: '24px 0' }} />
      <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
        {showCancel && (
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button
          type="primary"
          onClick={onSubmit}
          loading={loading}
        >
          {submitText}
        </Button>
      </Space>
    </ModalDialog>
  );
};

export default ModalDialog;
