import React, { useState } from 'react';
import { Card, Tabs, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Progress, Alert, Spin, Avatar, List, Tooltip } from 'antd';
import {
  ShieldOutlined,
  UserOutlined,
  TeamOutlined,
  SafetyOutlined,
  KeyOutlined,
  AuditOutlined,
  LockOutlined,
  UnlockOutlined,
  SearchOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  FilterOutlined,
  ExportOutlined,
  ImportOutlined,
  SettingOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Line, Bar, Pie } from '@ant-design/plots';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

// API Service
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${Cookies.get('access_token')}`,
  },
});

// Mock data
const mockUsers = [
  {
    id: 'user-1',
    username: 'admin',
    email: 'admin@openlens.com',
    fullName: 'Administrator',
    role: 'Administrator',
    status: 'active',
    lastLogin: '2024-01-15T14:30:00Z',
    createdAt: '2024-01-01T10:00:00Z',
    loginCount: 45,
  },
  {
    id: 'user-2',
    username: 'analyst1',
    email: 'analyst1@openlens.com',
    fullName: 'John Smith',
    role: 'Analyst',
    status: 'active',
    lastLogin: '2024-01-15T13:45:00Z',
    createdAt: '2024-01-02T11:00:00Z',
    loginCount: 32,
  },
  {
    id: 'user-3',
    username: 'analyst2',
    email: 'analyst2@openlens.com',
    fullName: 'Jane Doe',
    role: 'Analyst',
    status: 'inactive',
    lastLogin: '2024-01-10T09:00:00Z',
    createdAt: '2024-01-03T14:00:00Z',
    loginCount: 18,
  },
  {
    id: 'user-4',
    username: 'viewer1',
    email: 'viewer1@openlens.com',
    fullName: 'Bob Johnson',
    role: 'Viewer',
    status: 'active',
    lastLogin: '2024-01-15T12:15:00Z',
    createdAt: '2024-01-04T09:00:00Z',
    loginCount: 24,
  },
];

const mockRoles = [
  {
    id: 'role-1',
    name: 'Administrator',
    description: 'Full access to all features and data',
    permissions: ['*'],
    userCount: 1,
  },
  {
    id: 'role-2',
    name: 'Analyst',
    description: 'Can view and analyze data, create reports',
    permissions: ['read:data', 'analyze', 'create:reports'],
    userCount: 2,
  },
  {
    id: 'role-3',
    name: 'Viewer',
    description: 'Read-only access to data and reports',
    permissions: ['read:data', 'read:reports'],
    userCount: 1,
  },
  {
    id: 'role-4',
    name: 'Scraper',
    description: 'Can create and manage scraping jobs',
    permissions: ['create:jobs', 'manage:jobs', 'read:data'],
    userCount: 0,
  },
];

const mockPermissions = [
  { id: 'perm-1', name: 'read:data', description: 'Read data from all modules' },
  { id: 'perm-2', name: 'write:data', description: 'Write data to all modules' },
  { id: 'perm-3', name: 'delete:data', description: 'Delete data from all modules' },
  { id: 'perm-4', name: 'analyze', description: 'Run analysis on data' },
  { id: 'perm-5', name: 'create:reports', description: 'Create reports' },
  { id: 'perm-6', name: 'manage:users', description: 'Manage users and roles' },
  { id: 'perm-7', name: 'manage:jobs', description: 'Manage scraping jobs' },
  { id: 'perm-8', name: 'read:audit', description: 'Read audit logs' },
  { id: 'perm-9', name: 'manage:settings', description: 'Manage system settings' },
];

const mockAuditLogs = [
  {
    id: 'log-1',
    timestamp: '2024-01-15T14:30:00Z',
    user: 'admin',
    eventType: 'authentication',
    action: 'login',
    resource: 'system',
    details: { ip: '192.168.1.100', status: 'success' },
    severity: 'info',
  },
  {
    id: 'log-2',
    timestamp: '2024-01-15T14:25:00Z',
    user: 'analyst1',
    eventType: 'data',
    action: 'read',
    resource: 'graph',
    details: { query: 'MATCH (n) RETURN n LIMIT 100' },
    severity: 'info',
  },
  {
    id: 'log-3',
    timestamp: '2024-01-15T14:20:00Z',
    user: 'admin',
    eventType: 'configuration',
    action: 'update',
    resource: 'settings',
    details: { setting: 'theme', value: 'dark' },
    severity: 'info',
  },
  {
    id: 'log-4',
    timestamp: '2024-01-15T14:15:00Z',
    user: 'analyst2',
    eventType: 'security',
    action: 'failed_login',
    resource: 'system',
    details: { ip: '192.168.1.200', attempts: 3 },
    severity: 'warning',
  },
  {
    id: 'log-5',
    timestamp: '2024-01-15T14:10:00Z',
    user: 'admin',
    eventType: 'data',
    action: 'delete',
    resource: 'graph',
    details: { nodes: 5, edges: 10 },
    severity: 'info',
  },
];

const mockEncryptionStats = {
  totalEncrypted: 12453,
  totalDecrypted: 8734,
  algorithms: ['AES-256', 'RSA-2048', 'ChaCha20'],
  keyStrength: '256-bit',
  lastRotation: '2024-01-01T00:00:00Z',
};

const mockComplianceStats = {
  totalChecks: 45,
  passedChecks: 42,
  failedChecks: 3,
  complianceRate: 0.93,
  lastAudit: '2024-01-10T00:00:00Z',
};

const SecurityCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [userFormVisible, setUserFormVisible] = useState(false);
  const [roleFormVisible, setRoleFormVisible] = useState(false);
  const [permissionFormVisible, setPermissionFormVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState(mockUsers);
  const [roles, setRoles] = useState(mockRoles);
  const [permissions, setPermissions] = useState(mockPermissions);
  const [auditLogs, setAuditLogs] = useState(mockAuditLogs);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const queryClient = useQueryClient();

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#52c41a';
      case 'inactive': return '#faad14';
      case 'locked': return '#f5222d';
      default: return '#d9d9d9';
    }
  };

  // Get status tag
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'active': return <Tag color="success">Active</Tag>;
      case 'inactive': return <Tag color="warning">Inactive</Tag>;
      case 'locked': return <Tag color="error">Locked</Tag>;
      default: return <Tag>Unknown</Tag>;
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#f5222d';
      case 'high': return '#fa8c16';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      case 'info': return '#1890ff';
      default: return '#d9d9d9';
    }
  };

  // Get severity tag
  const getSeverityTag = (severity: string) => {
    switch (severity) {
      case 'critical': return <Tag color="error">Critical</Tag>;
      case 'high': return <Tag color="warning">High</Tag>;
      case 'medium': return <Tag color="warning">Medium</Tag>;
      case 'low': return <Tag color="success">Low</Tag>;
      case 'info': return <Tag color="info">Info</Tag>;
      default: return <Tag>Unknown</Tag>;
    }
  };

  // User columns
  const userColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: 'Name',
      dataIndex: 'fullName',
      key: 'fullName',
      width: 200,
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      width: 150,
      render: (role: string) => <Tag color="blue">{role}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'Last Login',
      dataIndex: 'lastLogin',
      key: 'lastLogin',
      width: 200,
    },
    {
      title: 'Logins',
      dataIndex: 'loginCount',
      key: 'loginCount',
      width: 100,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedUser(record)}>
            View
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            Edit
          </Button>
          {record.status === 'active' ? (
            <Button type="link" size="small" icon={<LockOutlined />}>
              Lock
            </Button>
          ) : (
            <Button type="link" size="small" icon={<UnlockOutlined />}>
              Unlock
            </Button>
          )}
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  // Role columns
  const roleColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      width: 300,
    },
    {
      title: 'Users',
      dataIndex: 'userCount',
      key: 'userCount',
      width: 100,
    },
    {
      title: 'Permissions',
      dataIndex: 'permissions',
      key: 'permissions',
      width: 200,
      render: (permissions: string[]) => (
        <Tooltip title={permissions.join(', ')}>
          <Text style={{ maxWidth: 150, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {permissions.length} permission{permissions.length !== 1 ? 's' : ''}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 150,
      render: (_: any, record: any) => (
        <Space>
          <Button type="link" size="small" onClick={() => setSelectedRole(record)}>
            View
          </Button>
          <Button type="link" size="small" icon={<EditOutlined />}>
            Edit
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  // Permission columns
  const permissionColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      width: 300,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: () => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />}>
            Edit
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  // Audit log columns
  const auditLogColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 200,
    },
    {
      title: 'User',
      dataIndex: 'user',
      key: 'user',
      width: 150,
    },
    {
      title: 'Event Type',
      dataIndex: 'eventType',
      key: 'eventType',
      width: 150,
      render: (type: string) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      width: 150,
    },
    {
      title: 'Resource',
      dataIndex: 'resource',
      key: 'resource',
      width: 150,
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => getSeverityTag(severity),
    },
    {
      title: 'Details',
      dataIndex: 'details',
      key: 'details',
      width: 200,
      render: (details: any) => (
        <Tooltip title={JSON.stringify(details)}>
          <Text style={{ maxWidth: 150, display: 'inline-block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            {JSON.stringify(details).substring(0, 30)}...
          </Text>
        </Tooltip>
      ),
    },
  ];

  // Create user
  const createUser = async (values: any) => {
    setLoading(true);
    try {
      const newUser = {
        id: `user-${Date.now()}`,
        username: values.username,
        email: values.email,
        fullName: values.fullName,
        role: values.role,
        status: 'active',
        lastLogin: null,
        createdAt: new Date().toISOString(),
        loginCount: 0,
      };
      setUsers([...users, newUser]);
      setUserFormVisible(false);
    } catch (error) {
      console.error('Create user error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create role
  const createRole = async (values: any) => {
    setLoading(true);
    try {
      const newRole = {
        id: `role-${Date.now()}`,
        name: values.name,
        description: values.description,
        permissions: values.permissions || [],
        userCount: 0,
      };
      setRoles([...roles, newRole]);
      setRoleFormVisible(false);
    } catch (error) {
      console.error('Create role error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create permission
  const createPermission = async (values: any) => {
    setLoading(true);
    try {
      const newPermission = {
        id: `perm-${Date.now()}`,
        name: values.name,
        description: values.description,
      };
      setPermissions([...permissions, newPermission]);
      setPermissionFormVisible(false);
    } catch (error) {
      console.error('Create permission error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter audit logs
  const filteredAuditLogs = auditLogs.filter(log => {
    if (filter !== 'all' && log.severity !== filter) return false;
    if (search && !log.user.toLowerCase().includes(search.toLowerCase()) && 
        !log.eventType.toLowerCase().includes(search.toLowerCase()) &&
        !log.action.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  // User stats chart
  const userStatsConfig = {
    data: [
      { role: 'Administrator', count: users.filter(u => u.role === 'Administrator').length },
      { role: 'Analyst', count: users.filter(u => u.role === 'Analyst').length },
      { role: 'Viewer', count: users.filter(u => u.role === 'Viewer').length },
      { role: 'Scraper', count: users.filter(u => u.role === 'Scraper').length },
    ],
    xField: 'role',
    yField: 'count',
    colorField: 'role',
    color: ['#f5222d', '#1890ff', '#52c41a', '#faad14'],
    label: {
      position: 'top' as const,
    },
  };

  // Audit log chart
  const auditLogChartConfig = {
    data: [
      { type: 'authentication', count: auditLogs.filter(l => l.eventType === 'authentication').length },
      { type: 'data', count: auditLogs.filter(l => l.eventType === 'data').length },
      { type: 'configuration', count: auditLogs.filter(l => l.eventType === 'configuration').length },
      { type: 'security', count: auditLogs.filter(l => l.eventType === 'security').length },
    ],
    xField: 'type',
    yField: 'count',
    seriesField: 'type',
    color: ['#1890ff', '#52c41a', '#faad14', '#f5222d'],
    label: {
      position: 'top' as const,
    },
  };

  // Severity chart
  const severityChartConfig = {
    data: [
      { severity: 'Critical', count: auditLogs.filter(l => l.severity === 'critical').length },
      { severity: 'High', count: auditLogs.filter(l => l.severity === 'high').length },
      { severity: 'Medium', count: auditLogs.filter(l => l.severity === 'medium').length },
      { severity: 'Low', count: auditLogs.filter(l => l.severity === 'low').length },
      { severity: 'Info', count: auditLogs.filter(l => l.severity === 'info').length },
    ],
    angleField: 'count',
    colorField: 'severity',
    radius: 0.8,
    label: {
      type: 'spider' as const,
      labelHeight: 28,
      content: '{name}\n{percentage}' as const,
    },
    color: ['#f5222d', '#fa8c16', '#faad14', '#52c41a', '#1890ff'],
  };

  return (
    <div className="security-center-page">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="page-header"
      >
        <div>
          <Title level={1}>
            <Space>
              <ShieldOutlined />
              Security Center
            </Space>
          </Title>
          <Paragraph type="secondary">
            Enterprise-grade security and access control
          </Paragraph>
        </div>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setUserFormVisible(true)}>
            New User
          </Button>
          <Button icon={<SyncOutlined />} onClick={() => window.location.reload()}>
            Refresh
          </Button>
        </Space>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Row gutter={24}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Users"
                value={users.length}
                prefix={<UserOutlined style={{ color: '#1890ff' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Roles"
                value={roles.length}
                prefix={<TeamOutlined style={{ color: '#52c41a' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Total Permissions"
                value={permissions.length}
                prefix={<SafetyOutlined style={{ color: '#faad14' }} />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="Audit Logs"
                value={auditLogs.length}
                prefix={<AuditOutlined style={{ color: '#722ed1' }} />}
              />
            </Card>
          </Col>
        </Row>
      </motion.div>

      <Divider />

      {/* Main Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card
          tabList={[
            { key: 'users', tab: 'User Management' },
            { key: 'roles', tab: 'RBAC' },
            { key: 'audit', tab: 'Audit Logging' },
            { key: 'encryption', tab: 'Encryption' },
            { key: 'auth', tab: 'Authentication' },
            { key: 'authorization', tab: 'Authorization' },
            { key: 'compliance', tab: 'Compliance' },
          ]}
          activeTabKey={activeTab}
          onTabChange={setActiveTab}
        >
          {activeTab === 'users' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>User Management</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Search
                      placeholder="Search users..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Select
                      placeholder="Filter by status"
                      style={{ width: '100%' }}
                      options={[
                        { label: 'All', value: 'all' },
                        { label: 'Active', value: 'active' },
                        { label: 'Inactive', value: 'inactive' },
                        { label: 'Locked', value: 'locked' },
                      ]}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setUserFormVisible(true)}
                      block
                    >
                      New User
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* User Stats Chart */}
              <Card title="Users by Role" style={{ marginBottom: 24 }}>
                <Bar {...userStatsConfig} height={200} />
              </Card>

              {/* Users Table */}
              <Card title="All Users">
                <Table
                  columns={userColumns}
                  dataSource={users}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1400 }}
                />
              </Card>

              {/* User Details Modal */}
              <Modal
                title="User Details"
                open={!!selectedUser}
                onCancel={() => setSelectedUser(null)}
                footer={null}
                width={800}
              >
                {selectedUser && (
                  <div>
                    <Row gutter={24}>
                      <Col span={24}>
                        <Card title="User Information" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>ID:</Text> {selectedUser.id}
                            </div>
                            <div>
                              <Text strong>Username:</Text> {selectedUser.username}
                            </div>
                            <div>
                              <Text strong>Full Name:</Text> {selectedUser.fullName}
                            </div>
                            <div>
                              <Text strong>Email:</Text> {selectedUser.email}
                            </div>
                            <div>
                              <Text strong>Role:</Text> {selectedUser.role}
                            </div>
                            <div>
                              <Text strong>Status:</Text> {getStatusTag(selectedUser.status)}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }} gutter={24}>
                      <Col span={12}>
                        <Card title="Timing" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Created:</Text> {selectedUser.createdAt}
                            </div>
                            <div>
                              <Text strong>Last Login:</Text> {selectedUser.lastLogin || 'Never'}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                      <Col span={12}>
                        <Card title="Statistics" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>Login Count:</Text> {selectedUser.loginCount}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                  </div>
                )}
              </Modal>

              {/* New User Modal */}
              <Modal
                title="New User"
                open={userFormVisible}
                onCancel={() => setUserFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={createUser} layout="vertical">
                  <Form.Item name="username" label="Username" rules={[{ required: true }]}>
                    <Input placeholder="Enter username" />
                  </Form.Item>
                  <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
                    <Input placeholder="Enter email" />
                  </Form.Item>
                  <Form.Item name="fullName" label="Full Name" rules={[{ required: true }]}>
                    <Input placeholder="Enter full name" />
                  </Form.Item>
                  <Form.Item name="password" label="Password" rules={[{ required: true }]}>
                    <Input.Password placeholder="Enter password" />
                  </Form.Item>
                  <Form.Item name="role" label="Role" rules={[{ required: true }]}>
                    <Select options={roles.map(r => ({ label: r.name, value: r.name }))} />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Create User
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>
            </div>
          )}

          {activeTab === 'roles' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Role-Based Access Control (RBAC)</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={18}>
                    <Search
                      placeholder="Search roles..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setRoleFormVisible(true)}
                      block
                    >
                      New Role
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Roles Table */}
              <Card title="All Roles">
                <Table
                  columns={roleColumns}
                  dataSource={roles}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1200 }}
                />
              </Card>

              {/* Role Details Modal */}
              <Modal
                title="Role Details"
                open={!!selectedRole}
                onCancel={() => setSelectedRole(null)}
                footer={null}
                width={800}
              >
                {selectedRole && (
                  <div>
                    <Row gutter={24}>
                      <Col span={24}>
                        <Card title="Role Information" size="small">
                          <Space direction="vertical">
                            <div>
                              <Text strong>ID:</Text> {selectedRole.id}
                            </div>
                            <div>
                              <Text strong>Name:</Text> {selectedRole.name}
                            </div>
                            <div>
                              <Text strong>Description:</Text> {selectedRole.description}
                            </div>
                            <div>
                              <Text strong>User Count:</Text> {selectedRole.userCount}
                            </div>
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                    
                    <Row style={{ marginTop: 24 }}>
                      <Col span={24}>
                        <Card title="Permissions" size="small">
                          <Space wrap>
                            {selectedRole.permissions.map((perm: string) => (
                              <Tag key={perm} color="blue">{perm}</Tag>
                            ))}
                          </Space>
                        </Card>
                      </Col>
                    </Row>
                  </div>
                )}
              </Modal>

              {/* New Role Modal */}
              <Modal
                title="New Role"
                open={roleFormVisible}
                onCancel={() => setRoleFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={createRole} layout="vertical">
                  <Form.Item name="name" label="Role Name" rules={[{ required: true }]}>
                    <Input placeholder="Enter role name" />
                  </Form.Item>
                  <Form.Item name="description" label="Description">
                    <Input.TextArea placeholder="Enter description" rows={3} />
                  </Form.Item>
                  <Form.Item name="permissions" label="Permissions">
                    <Select
                      mode="multiple"
                      options={permissions.map(p => ({ label: p.name, value: p.name }))}
                      placeholder="Select permissions"
                    />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Create Role
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>

              {/* Permissions Table */}
              <Card title="All Permissions" style={{ marginTop: 24 }}>
                <Card size="small" style={{ marginBottom: 24 }}>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setPermissionFormVisible(true)}
                  >
                    New Permission
                  </Button>
                </Card>
                <Table
                  columns={permissionColumns}
                  dataSource={permissions}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1000 }}
                />
              </Card>

              {/* New Permission Modal */}
              <Modal
                title="New Permission"
                open={permissionFormVisible}
                onCancel={() => setPermissionFormVisible(false)}
                footer={null}
                width={600}
              >
                <Form onFinish={createPermission} layout="vertical">
                  <Form.Item name="name" label="Permission Name" rules={[{ required: true }]}>
                    <Input placeholder="e.g., read:data" />
                  </Form.Item>
                  <Form.Item name="description" label="Description">
                    <Input.TextArea placeholder="Enter description" rows={3} />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      Create Permission
                    </Button>
                  </Form.Item>
                </Form>
              </Modal>
            </div>
          )}

          {activeTab === 'audit' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Audit Logging</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Row gutter={24} align="middle">
                  <Col xs={24} lg={12}>
                    <Search
                      placeholder="Search audit logs..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Select
                      placeholder="Filter by severity"
                      value={filter}
                      onChange={setFilter}
                      style={{ width: '100%' }}
                      options={[
                        { label: 'All', value: 'all' },
                        { label: 'Critical', value: 'critical' },
                        { label: 'High', value: 'high' },
                        { label: 'Medium', value: 'medium' },
                        { label: 'Low', value: 'low' },
                        { label: 'Info', value: 'info' },
                      ]}
                    />
                  </Col>
                  <Col xs={24} lg={6}>
                    <Button icon={<ExportOutlined />} block>
                      Export Logs
                    </Button>
                  </Col>
                </Row>
              </Card>

              {/* Audit Log Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} lg={12}>
                  <Card title="Events by Type">
                    <Bar {...auditLogChartConfig} height={200} />
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Events by Severity">
                    <Pie {...severityChartConfig} height={200} />
                  </Card>
                </Col>
              </Row>

              {/* Audit Logs Table */}
              <Card title="Audit Logs">
                <Table
                  columns={auditLogColumns}
                  dataSource={filteredAuditLogs}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1400 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'encryption' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Encryption</Title>
              
              {/* Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Encrypted"
                      value={mockEncryptionStats.totalEncrypted.toLocaleString()}
                      prefix={<LockOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Decrypted"
                      value={mockEncryptionStats.totalDecrypted.toLocaleString()}
                      prefix={<UnlockOutlined style={{ color: '#52c41a' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Key Strength"
                      value={mockEncryptionStats.keyStrength}
                      prefix={<KeyOutlined style={{ color: '#faad14' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Algorithms"
                      value={mockEncryptionStats.algorithms.length}
                      prefix={<CodeOutlined style={{ color: '#722ed1' }} />}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Encryption Info */}
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="Encryption Algorithms">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {mockEncryptionStats.algorithms.map(alg => (
                        <Tag key={alg} color="blue" style={{ padding: '8px 16px', fontSize: 14 }}>
                          {alg}
                        </Tag>
                      ))}
                    </Space>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Key Management">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text>Last Rotation:</Text>
                        <Text strong>{mockEncryptionStats.lastRotation}</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Text>Rotation Interval:</Text>
                        <Text strong>30 days</Text>
                      </div>
                    </Space>
                    <Divider />
                    <Space>
                      <Button type="primary" icon={<SyncOutlined />}>
                        Rotate Keys
                      </Button>
                      <Button icon={<SettingOutlined />}>
                        Configure
                      </Button>
                    </Space>
                  </Card>
                </Col>
              </Row>

              {/* Encryption Tools */}
              <Card title="Encryption Tools" style={{ marginTop: 24 }}>
                <Row gutter={24}>
                  <Col xs={24} lg={12}>
                    <Card title="Encrypt Data" size="small">
                      <Form layout="vertical">
                        <Form.Item label="Data to Encrypt">
                          <Input.TextArea rows={4} placeholder="Enter text to encrypt" />
                        </Form.Item>
                        <Form.Item label="Algorithm">
                          <Select options={mockEncryptionStats.algorithms.map(alg => ({ label: alg, value: alg }))} />
                        </Form.Item>
                        <Form.Item>
                          <Button type="primary" block icon={<LockOutlined />}>
                            Encrypt
                          </Button>
                        </Form.Item>
                      </Form>
                    </Card>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Card title="Decrypt Data" size="small">
                      <Form layout="vertical">
                        <Form.Item label="Data to Decrypt">
                          <Input.TextArea rows={4} placeholder="Enter encrypted text" />
                        </Form.Item>
                        <Form.Item label="Algorithm">
                          <Select options={mockEncryptionStats.algorithms.map(alg => ({ label: alg, value: alg }))} />
                        </Form.Item>
                        <Form.Item>
                          <Button type="primary" block icon={<UnlockOutlined />}>
                            Decrypt
                          </Button>
                        </Form.Item>
                      </Form>
                    </Card>
                  </Col>
                </Row>
              </Card>
            </div>
          )}

          {activeTab === 'auth' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Authentication</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Paragraph type="secondary">
                  Configure authentication settings and providers
                </Paragraph>
              </Card>

              {/* Authentication Methods */}
              <Row gutter={24}>
                <Col xs={24} lg={12}>
                  <Card title="Authentication Methods">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Space>
                          <LockOutlined style={{ color: '#1890ff' }} />
                          <Text strong>Local Authentication</Text>
                        </Space>
                        <Tag color="success">Enabled</Tag>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Space>
                          <GlobalOutlined style={{ color: '#52c41a' }} />
                          <Text strong>LDAP</Text>
                        </Space>
                        <Tag color="warning">Disabled</Tag>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Space>
                          <UserOutlined style={{ color: '#faad14' }} />
                          <Text strong>OAuth 2.0</Text>
                        </Space>
                        <Tag color="warning">Disabled</Tag>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
                        <Space>
                          <SafetyOutlined style={{ color: '#722ed1' }} />
                          <Text strong>SAML</Text>
                        </Space>
                        <Tag color="warning">Disabled</Tag>
                      </div>
                    </Space>
                  </Card>
                </Col>
                <Col xs={24} lg={12}>
                  <Card title="Authentication Settings">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Session Timeout:</Text>
                        <Text strong>24 hours</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Max Sessions:</Text>
                        <Text strong>5 per user</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Password Policy:</Text>
                        <Text strong>Strong</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
                        <Text>2FA Required:</Text>
                        <Tag color="warning">Disabled</Tag>
                      </div>
                    </Space>
                    <Divider />
                    <Space>
                      <Button type="primary" icon={<EditOutlined />}>
                        Edit Settings
                      </Button>
                    </Space>
                  </Card>
                </Col>
              </Row>

              {/* Password Policy */}
              <Card title="Password Policy" style={{ marginTop: 24 }}>
                <Row gutter={24}>
                  <Col xs={24} lg={12}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Minimum Length:</Text>
                        <Text strong>8 characters</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Require Uppercase:</Text>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Require Lowercase:</Text>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
                        <Text>Require Numbers:</Text>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      </div>
                    </Space>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Require Special Chars:</Text>
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Max Attempts:</Text>
                        <Text strong>5</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f0f0f0' }}>
                        <Text>Lockout Duration:</Text>
                        <Text strong>30 minutes</Text>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0' }}>
                        <Text>Password Expiry:</Text>
                        <Text strong>90 days</Text>
                      </div>
                    </Space>
                  </Col>
                </Row>
              </Card>
            </div>
          )}

          {activeTab === 'authorization' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Authorization</Title>
              
              <Card size="small" style={{ marginBottom: 24 }}>
                <Paragraph type="secondary">
                  Configure fine-grained access control policies
                </Paragraph>
              </Card>

              {/* Authorization Matrix */}
              <Card title="Access Control Matrix">
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ borderBottom: '2px solid #f0f0f0' }}>
                        <th style={{ textAlign: 'left', padding: 12, background: '#fafafa' }}>Resource</th>
                        {roles.map(role => (
                          <th key={role.id} style={{ textAlign: 'center', padding: 12, background: '#fafafa' }}>
                            {role.name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { name: 'Graph Analytics', key: 'graph' },
                        { name: 'AI/ML', key: 'ai' },
                        { name: 'Scraping', key: 'scraping' },
                        { name: 'Threat Intel', key: 'threat' },
                        { name: 'Security', key: 'security' },
                        { name: 'Settings', key: 'settings' },
                      ].map(resource => (
                        <tr key={resource.key} style={{ borderBottom: '1px solid #f0f0f0' }}>
                          <td style={{ padding: 12, fontWeight: 600 }}>{resource.name}</td>
                          {roles.map(role => (
                            <td key={role.id} style={{ textAlign: 'center', padding: 12 }}>
                              {role.permissions.includes('*') || role.permissions.includes(`access:${resource.key}`) ? (
                                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                              ) : (
                                <CloseCircleOutlined style={{ color: '#f5222d' }} />
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Policy Editor */}
              <Card title="Policy Editor" style={{ marginTop: 24 }}>
                <Row gutter={24}>
                  <Col xs={24} lg={12}>
                    <Card title="Create New Policy" size="small">
                      <Form layout="vertical">
                        <Form.Item label="Policy Name">
                          <Input placeholder="Enter policy name" />
                        </Form.Item>
                        <Form.Item label="Description">
                          <Input.TextArea rows={2} placeholder="Enter description" />
                        </Form.Item>
                        <Form.Item label="Resource">
                          <Select options={[
                            { label: 'All', value: '*' },
                            { label: 'Graph Analytics', value: 'graph' },
                            { label: 'AI/ML', value: 'ai' },
                            { label: 'Scraping', value: 'scraping' },
                            { label: 'Threat Intel', value: 'threat' },
                            { label: 'Security', value: 'security' },
                          ]} />
                        </Form.Item>
                        <Form.Item label="Actions">
                          <Select mode="multiple" options={[
                            { label: 'Read', value: 'read' },
                            { label: 'Write', value: 'write' },
                            { label: 'Delete', value: 'delete' },
                            { label: 'Execute', value: 'execute' },
                          ]} />
                        </Form.Item>
                        <Form.Item>
                          <Button type="primary" block icon={<PlusOutlined />}>
                            Create Policy
                          </Button>
                        </Form.Item>
                      </Form>
                    </Card>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Card title="Existing Policies" size="small">
                      <List
                        dataSource={[
                          { id: 'policy-1', name: 'Admin Full Access', description: 'Full access to all resources' },
                          { id: 'policy-2', name: 'Analyst Read-Only', description: 'Read-only access to data' },
                          { id: 'policy-3', name: 'Scraper Limited', description: 'Can only create and manage jobs' },
                        ]}
                        renderItem={(policy: any) => (
                          <List.Item>
                            <List.Item.Meta
                              title={policy.name}
                              description={policy.description}
                            />
                            <Space>
                              <Button type="link" size="small" icon={<EditOutlined />}>
                                Edit
                              </Button>
                              <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                                Delete
                              </Button>
                            </Space>
                          </List.Item>
                        )}
                      />
                    </Card>
                  </Col>
                </Row>
              </Card>
            </div>
          )}

          {activeTab === 'compliance' && (
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Compliance</Title>
              
              {/* Stats */}
              <Row gutter={24} style={{ marginBottom: 24 }}>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Total Checks"
                      value={mockComplianceStats.totalChecks}
                      prefix={<CheckCircleOutlined style={{ color: '#1890ff' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Passed Checks"
                      value={mockComplianceStats.passedChecks}
                      prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                      suffix={<Tag color="success">{(mockComplianceStats.complianceRate * 100).toFixed(1)}%</Tag>}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Failed Checks"
                      value={mockComplianceStats.failedChecks}
                      prefix={<CloseCircleOutlined style={{ color: '#f5222d' }} />}
                    />
                  </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                  <Card>
                    <Statistic
                      title="Last Audit"
                      value={mockComplianceStats.lastAudit}
                      prefix={<AuditOutlined style={{ color: '#722ed1' }} />}
                    />
                  </Card>
                </Col>
              </Row>

              {/* Compliance Chart */}
              <Card title="Compliance Status" style={{ marginBottom: 24 }}>
                <Bar
                  data={[
                    { category: 'Passed', value: mockComplianceStats.passedChecks, color: '#52c41a' },
                    { category: 'Failed', value: mockComplianceStats.failedChecks, color: '#f5222d' },
                  ]}
                  xField="category"
                  yField="value"
                  colorField="color"
                  height={200}
                />
              </Card>

              {/* Compliance Checks */}
              <Card title="Compliance Checks">
                <List
                  dataSource={[
                    { id: 'check-1', name: 'Password Policy', status: 'passed', category: 'Security' },
                    { id: 'check-2', name: 'Data Encryption', status: 'passed', category: 'Security' },
                    { id: 'check-3', name: 'Access Logging', status: 'passed', category: 'Audit' },
                    { id: 'check-4', name: 'Data Retention', status: 'failed', category: 'Data' },
                    { id: 'check-5', name: 'User Access Review', status: 'passed', category: 'Access' },
                  ]}
                  renderItem={(check: any) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={
                          <Avatar
                            icon={check.status === 'passed' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                            style={{ background: check.status === 'passed' ? '#52c41a' : '#f5222d' }}
                          />
                        }
                        title={check.name}
                        description={
                          <Space>
                            <Tag color={check.status === 'passed' ? 'success' : 'error'}>
                              {check.status}
                            </Tag>
                            <Text type="secondary">{check.category}</Text>
                          </Space>
                        }
                      />
                    </List.Item>
                  )}
                />
              </Card>

              {/* Actions */}
              <Card title="Actions" style={{ marginTop: 24 }}>
                <Space>
                  <Button type="primary" icon={<SyncOutlined />}>
                    Run Audit
                  </Button>
                  <Button icon={<ExportOutlined />}>
                    Export Report
                  </Button>
                  <Button icon={<SettingOutlined />}>
                    Configure Checks
                  </Button>
                </Space>
              </Card>
            </div>
          )}
        </Card>
      </motion.div>
    </div>
  );
};

// Temporary icon
const CodeOutlined = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="16 18 22 12 16 6" />
    <polyline points="8 6 2 12 8 18" />
  </svg>
);

export default SecurityCenter;
