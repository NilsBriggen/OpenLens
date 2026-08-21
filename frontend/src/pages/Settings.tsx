import React from 'react';
import { Card, Typography, Row, Col, Divider, Form, Input, Button, Switch, Select, Alert } from 'antd';
import { SettingOutlined, SaveOutlined, SyncOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text, Paragraph } = Typography;

const Settings: React.FC = () => {
  return (
    <div className="settings-page">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="page-header">
        <div>
          <Title level={1}><SettingOutlined /> Settings</Title>
          <Paragraph type="secondary">Configure your OpenLens platform</Paragraph>
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}>
        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Card title="General Settings">
              <Form layout="vertical">
                <Form.Item label="Platform Name">
                  <Input placeholder="OpenLens" />
                </Form.Item>
                <Form.Item label="Description">
                  <Input.TextArea placeholder="Enterprise-Grade OSINT Platform" rows={3} />
                </Form.Item>
                <Form.Item label="Default Language">
                  <Select options={[{ label: 'English', value: 'en' }]} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save Settings
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Appearance">
              <Form layout="vertical">
                <Form.Item label="Theme">
                  <Select options={[
                    { label: 'System Default', value: 'system' },
                    { label: 'Light', value: 'light' },
                    { label: 'Dark', value: 'dark' },
                  ]} />
                </Form.Item>
                <Form.Item label="Primary Color">
                  <Input type="color" defaultValue="#1890ff" />
                </Form.Item>
                <Form.Item label="Enable Animations" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save Appearance
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Card title="API Settings">
              <Form layout="vertical">
                <Form.Item label="API Base URL">
                  <Input placeholder="http://localhost:8000" />
                </Form.Item>
                <Form.Item label="Timeout (seconds)">
                  <Input type="number" defaultValue={30} />
                </Form.Item>
                <Form.Item label="Enable Caching" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save API Settings
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Security Settings">
              <Form layout="vertical">
                <Form.Item label="Session Timeout (minutes)">
                  <Input type="number" defaultValue={30} />
                </Form.Item>
                <Form.Item label="Max Login Attempts">
                  <Input type="number" defaultValue={5} />
                </Form.Item>
                <Form.Item label="Enable 2FA" valuePropName="checked">
                  <Switch />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save Security Settings
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Row gutter={24}>
          <Col xs={24} lg={12}>
            <Card title="Notification Settings">
              <Form layout="vertical">
                <Form.Item label="Email Notifications" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item label="Desktop Notifications" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item label="Alert Severity Threshold">
                  <Select options={[
                    { label: 'All', value: 'all' },
                    { label: 'High and Critical', value: 'high' },
                    { label: 'Critical Only', value: 'critical' },
                  ]} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save Notification Settings
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="Data Settings">
              <Form layout="vertical">
                <Form.Item label="Auto-Update Feeds" valuePropName="checked">
                  <Switch defaultChecked />
                </Form.Item>
                <Form.Item label="Update Frequency">
                  <Select options={[
                    { label: 'Hourly', value: 'hourly' },
                    { label: 'Daily', value: 'daily' },
                    { label: 'Weekly', value: 'weekly' },
                  ]} />
                </Form.Item>
                <Form.Item label="Data Retention (days)">
                  <Input type="number" defaultValue={90} />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" icon={<SaveOutlined />} htmlType="submit">
                    Save Data Settings
                  </Button>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Card title="System Information">
          <Row gutter={24}>
            <Col xs={24} sm={12} lg={6}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text>Version:</Text>
                <Text strong>7.0.0</Text>
              </div>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text>Build:</Text>
                <Text strong>20240115</Text>
              </div>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                <Text>License:</Text>
                <Text strong>Enterprise</Text>
              </div>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0' }}>
                <Text>Support:</Text>
                <Text strong>Until 2025-01-15</Text>
              </div>
            </Col>
          </Row>
        </Card>

        <Divider />

        <Card title="Danger Zone">
          <Alert
            message="These actions are irreversible. Please proceed with caution."
            type="warning"
            showIcon
            style={{ marginBottom: 24 }}
          />
          <Row gutter={24}>
            <Col xs={24} lg={12}>
              <Card title="Reset Settings" size="small">
                <Paragraph type="secondary">Reset all settings to default values</Paragraph>
                <Button danger block icon={<SyncOutlined />}>
                  Reset All Settings
                </Button>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Clear Data" size="small">
                <Paragraph type="secondary">Permanently delete all data</Paragraph>
                <Button danger block icon={<SyncOutlined />}>
                  Clear All Data
                </Button>
              </Card>
            </Col>
          </Row>
        </Card>
      </motion.div>
    </div>
  );
};

export default Settings;
