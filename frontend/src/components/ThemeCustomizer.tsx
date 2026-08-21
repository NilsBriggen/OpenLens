import React, { useState, useEffect } from 'react';
import { Drawer, Button, Typography, Space, Divider, ColorPicker, Switch, Slider, Card, Row, Col, Tooltip } from 'antd';
import {
  SettingOutlined,
  PaintOutlined,
  SunOutlined,
  MoonOutlined,
  EyeOutlined,
  BorderOutlined,
  FontSizeOutlined,
  PaletteOutlined
} from '@ant-design/icons';
import { useTheme } from '../hooks';

const { Text, Title } = Typography;

interface ThemeCustomizerProps {
  visible: boolean;
  onClose: () => void;
}

interface ThemeSettings {
  primaryColor: string;
  secondaryColor: string;
  successColor: string;
  warningColor: string;
  errorColor: string;
  infoColor: string;
  borderRadius: number;
  fontSize: number;
  darkMode: boolean;
}

const ThemeCustomizer: React.FC<ThemeCustomizerProps> = ({ visible, onClose }) => {
  const { theme, toggleTheme, isDark } = useTheme();
  const [settings, setSettings] = useState<ThemeSettings>(() => {
    const saved = localStorage.getItem('themeSettings');
    return saved ? JSON.parse(saved) : {
      primaryColor: '#1890ff',
      secondaryColor: '#52c41a',
      successColor: '#52c41a',
      warningColor: '#faad14',
      errorColor: '#f5222d',
      infoColor: '#1890ff',
      borderRadius: 8,
      fontSize: 14,
      darkMode: isDark,
    };
  });

  // Update CSS variables when settings change
  useEffect(() => {
    const root = document.documentElement;
    
    root.style.setProperty('--primary-color', settings.primaryColor);
    root.style.setProperty('--secondary-color', settings.secondaryColor);
    root.style.setProperty('--success-color', settings.successColor);
    root.style.setProperty('--warning-color', settings.warningColor);
    root.style.setProperty('--error-color', settings.errorColor);
    root.style.setProperty('--info-color', settings.infoColor);
    root.style.setProperty('--border-radius', `${settings.borderRadius}px`);
    root.style.setProperty('--font-size', `${settings.fontSize}px`);

    // Save to localStorage
    localStorage.setItem('themeSettings', JSON.stringify(settings));
  }, [settings]);

  // Sync with theme context
  useEffect(() => {
    setSettings(prev => ({ ...prev, darkMode: isDark }));
  }, [isDark]);

  const handleColorChange = (key: keyof ThemeSettings, color: string) => {
    setSettings(prev => ({ ...prev, [key]: color }));
  };

  const handleSliderChange = (key: keyof ThemeSettings, value: number) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSwitchChange = (key: keyof ThemeSettings, value: boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    if (key === 'darkMode') {
      toggleTheme();
    }
  };

  const resetToDefaults = () => {
    setSettings({
      primaryColor: '#1890ff',
      secondaryColor: '#52c41a',
      successColor: '#52c41a',
      warningColor: '#faad14',
      errorColor: '#f5222d',
      infoColor: '#1890ff',
      borderRadius: 8,
      fontSize: 14,
      darkMode: isDark,
    });
  };

  return (
    <Drawer
      title={
        <Space>
          <PaletteOutlined style={{ color: '#1890ff' }} />
          <Title level={4} style={{ margin: 0 }}>Theme Customizer</Title>
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={visible}
      width={400}
      maskClosable={true}
      closable={true}
      headerStyle={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}
      bodyStyle={{ padding: 0 }}
      footer={
        <Space>
          <Button onClick={resetToDefaults}>
            Reset to Defaults
          </Button>
          <Button type="primary" onClick={onClose}>
            Close
          </Button>
        </Space>
      }
      footerStyle={{ padding: 16, borderTop: '1px solid #f0f0f0' }}
    >
      <div style={{ padding: 16, height: 'calc(100vh - 180px)', overflowY: 'auto' }}>
        {/* Theme Mode */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Title level={5} style={{ margin: 0, marginBottom: 12 }}>
            <Space>
              <EyeOutlined />
              Theme Mode
            </Space>
          </Title>
          <Space>
            <Tooltip title="Light Mode">
              <Button
                icon={<SunOutlined />}
                onClick={() => handleSwitchChange('darkMode', false)}
                type={!settings.darkMode ? 'primary' : 'default'}
              />
            </Tooltip>
            <Tooltip title="Dark Mode">
              <Button
                icon={<MoonOutlined />}
                onClick={() => handleSwitchChange('darkMode', true)}
                type={settings.darkMode ? 'primary' : 'default'}
              />
            </Tooltip>
            <Switch
              checked={settings.darkMode}
              onChange={(checked) => handleSwitchChange('darkMode', checked)}
              checkedChildren="Dark"
              unCheckedChildren="Light"
            />
          </Space>
        </Card>

        {/* Colors */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Title level={5} style={{ margin: 0, marginBottom: 12 }}>
            <Space>
              <PaintOutlined />
              Colors
            </Space>
          </Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text>Primary Color</Text>
              <ColorPicker
                value={settings.primaryColor}
                onChange={(_, hex) => handleColorChange('primaryColor', hex)}
                showText
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text>Success Color</Text>
              <ColorPicker
                value={settings.successColor}
                onChange={(_, hex) => handleColorChange('successColor', hex)}
                showText
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text>Warning Color</Text>
              <ColorPicker
                value={settings.warningColor}
                onChange={(_, hex) => handleColorChange('warningColor', hex)}
                showText
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text>Error Color</Text>
              <ColorPicker
                value={settings.errorColor}
                onChange={(_, hex) => handleColorChange('errorColor', hex)}
                showText
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text>Info Color</Text>
              <ColorPicker
                value={settings.infoColor}
                onChange={(_, hex) => handleColorChange('infoColor', hex)}
                showText
              />
            </div>
          </Space>
        </Card>

        {/* Layout */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <Title level={5} style={{ margin: 0, marginBottom: 12 }}>
            <Space>
              <BorderOutlined />
              Layout
            </Space>
          </Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <Text>Border Radius</Text>
              <Slider
                min={0}
                max={24}
                value={settings.borderRadius}
                onChange={(value) => handleSliderChange('borderRadius', value)}
                style={{ width: 150 }}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text>Base Font Size</Text>
              <Slider
                min={12}
                max={20}
                value={settings.fontSize}
                onChange={(value) => handleSliderChange('fontSize', value)}
                style={{ width: 150 }}
              />
            </div>
          </Space>
        </Card>

        {/* Preview */}
        <Card size="small">
          <Title level={5} style={{ margin: 0, marginBottom: 12 }}>
            Preview
          </Title>
          <div
            style={{
              background: 'var(--bg-color-secondary)',
              padding: 16,
              borderRadius: settings.borderRadius,
              border: '1px solid var(--border-color)',
            }}
          >
            <div
              style={{
                width: 40,
                height: 40,
                background: settings.primaryColor,
                borderRadius: settings.borderRadius,
                marginBottom: 8,
              }}
            />
            <Text style={{ fontSize: settings.fontSize, color: 'var(--text-color)' }}>
              Sample Text
            </Text>
            <div style={{ marginTop: 8 }}>
              <Button type="primary" size="small" style={{ borderRadius: settings.borderRadius }}>
                Primary Button
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </Drawer>
  );
};

export default ThemeCustomizer;
