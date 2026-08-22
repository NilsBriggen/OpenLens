import React from 'react';
import { Card, Typography, Form, Input, Button, Switch, Select } from 'antd';
import { SettingOutlined, SaveOutlined, SyncOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import PageHeader from '../components/common/PageHeader';

const { Text, Paragraph } = Typography;

const Settings: React.FC = () => {
  return (
    <div className="ol-page-body">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <PageHeader
          icon={<SettingOutlined />}
          title="Settings"
          subtitle="Configure your OpenLens platform"
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="ol-page-body"
      >
        <div className="ol-row-2up">
          <Card title="General Settings">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="Platform Name" style={{ marginBottom: 0 }}>
                <Input placeholder="OpenLens" style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Description" style={{ marginBottom: 0 }}>
                <Input.TextArea placeholder="Enterprise-Grade OSINT Platform" rows={3} />
              </Form.Item>
              <Form.Item label="Default Language" style={{ marginBottom: 0 }}>
                <Select options={[{ label: 'English', value: 'en' }]} style={{ height: 32 }} />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save Settings
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="Appearance">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="Theme" style={{ marginBottom: 0 }}>
                <Select
                  options={[
                    { label: 'System Default', value: 'system' },
                    { label: 'Light', value: 'light' },
                    { label: 'Dark', value: 'dark' },
                  ]}
                  style={{ height: 32 }}
                />
              </Form.Item>
              <Form.Item label="Primary Color" style={{ marginBottom: 0 }}>
                <Input type="color" defaultValue="#1890ff" style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Enable Animations" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save Appearance
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="API Settings">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="API Base URL" style={{ marginBottom: 0 }}>
                <Input placeholder="http://localhost:8000" style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Timeout (seconds)" style={{ marginBottom: 0 }}>
                <Input type="number" defaultValue={30} style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Enable Caching" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save API Settings
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="Security Settings">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="Session Timeout (minutes)" style={{ marginBottom: 0 }}>
                <Input type="number" defaultValue={30} style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Max Login Attempts" style={{ marginBottom: 0 }}>
                <Input type="number" defaultValue={5} style={{ height: 32 }} />
              </Form.Item>
              <Form.Item label="Enable 2FA" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save Security Settings
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="Notification Settings">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="Email Notifications" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Desktop Notifications" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Alert Severity Threshold" style={{ marginBottom: 0 }}>
                <Select
                  options={[
                    { label: 'All', value: 'all' },
                    { label: 'High and Critical', value: 'high' },
                    { label: 'Critical Only', value: 'critical' },
                  ]}
                  style={{ height: 32 }}
                />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save Notification Settings
                </Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="Data Settings">
            <Form layout="vertical" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <Form.Item label="Auto-Update Feeds" valuePropName="checked" style={{ marginBottom: 0 }}>
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Update Frequency" style={{ marginBottom: 0 }}>
                <Select
                  options={[
                    { label: 'Hourly', value: 'hourly' },
                    { label: 'Daily', value: 'daily' },
                    { label: 'Weekly', value: 'weekly' },
                  ]}
                  style={{ height: 32 }}
                />
              </Form.Item>
              <Form.Item label="Data Retention (days)" style={{ marginBottom: 0 }}>
                <Input type="number" defaultValue={90} style={{ height: 32 }} />
              </Form.Item>
              <Form.Item style={{ marginBottom: 0 }}>
                <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                  Save Data Settings
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>

        <div className="ol-section">
          <div className="ol-section-title">System Information</div>
          <Card>
            <div className="ol-row-quarter">
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border-color-secondary)' }}>
                <Text type="secondary">Version</Text>
                <Text strong>7.0.0</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border-color-secondary)' }}>
                <Text type="secondary">Build</Text>
                <Text strong>20240115</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border-color-secondary)' }}>
                <Text type="secondary">License</Text>
                <Text strong>Enterprise</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border-color-secondary)' }}>
                <Text type="secondary">Support</Text>
                <Text strong>Until 2027-08-21</Text>
              </div>
            </div>
          </Card>
        </div>

        <div className="ol-section">
          <div className="ol-section-title">Danger Zone</div>
          <div className="ol-warning-banner">
            <ExclamationCircleOutlined />
            <span>These actions are irreversible. Please proceed with caution.</span>
          </div>
          <div className="ol-row-2up" style={{ marginTop: 16 }}>
            <Card size="small" title="Reset Settings" className="ol-subcard">
              <Paragraph type="secondary">Reset all settings to default values</Paragraph>
              <Button danger block icon={<SyncOutlined />}>
                Reset All Settings
              </Button>
            </Card>
            <Card size="small" title="Clear Data" className="ol-subcard">
              <Paragraph type="secondary">Permanently delete all data</Paragraph>
              <Button danger block icon={<SyncOutlined />}>
                Clear All Data
              </Button>
            </Card>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Settings;
