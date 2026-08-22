import React, { useState } from 'react';
import { Card, Button, Space, Typography, Row, Col, Divider, Modal, Form, Input, Select, Table, Tag, Alert, Tooltip } from 'antd';
import { SafetyCertificateOutlined, UserOutlined, TeamOutlined, SafetyOutlined, KeyOutlined, AuditOutlined, LockOutlined, UnlockOutlined, PlusOutlined, DeleteOutlined, EditOutlined, ExportOutlined, SettingOutlined, SyncOutlined, CodeOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { Pie } from '@ant-design/plots';
import { useQueryClient } from '@tanstack/react-query';
import {
  useUsers, useRoles, usePermissions, useAuditLogs,
  useCreateUser, useCreateRole, useCreatePermission, useLocalStorage,
} from '../hooks/useApi';
import StatCard from '../components/common/StatCard';
import PageHeader from '../components/common/PageHeader';
import BarList from '../components/common/BarList';
import TabEmptyState from '../components/common/TabEmptyState';

const { Title, Text } = Typography;
const { Search } = Input;


// Mock data
// SAMPLE DATA: no backend endpoint exists yet for these metrics.
const mockEncryptionStats = {
  totalEncrypted: 12453,
  totalDecrypted: 8734,
  algorithms: ['AES-256', 'RSA-2048', 'ChaCha20'],
  keyStrength: '256-bit',
  lastRotation: '2024-01-01T00:00:00Z',
};

const SecurityCenter: React.FC = () => {
  const { value: activeTab, setValue: setActiveTab } = useLocalStorage('security-active-tab', 'users');
  const [userFormVisible, setUserFormVisible] = useState(false);
  const [roleFormVisible, setRoleFormVisible] = useState(false);
  const [permissionFormVisible, setPermissionFormVisible] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  // Live data, adapted to the display shape the tables read. fullName and
  // loginCount have no backend source yet and render as placeholders.
  const { data: apiUsers = [] } = useUsers();
  const { data: apiRoles = [] } = useRoles();
  const { data: apiPermissions = [] } = usePermissions();
  const { data: apiAuditLogs = [] } = useAuditLogs(100);
  const createUserMutation = useCreateUser();
  const createRoleMutation = useCreateRole();
  const createPermissionMutation = useCreatePermission();

  const users = React.useMemo(() => apiUsers.map((u) => ({
    id: u.id,
    username: u.username,
    email: u.email,
    fullName: '',
    role: (u.roles || []).join(', ') || 'none',
    status: u.isActive ? 'active' : 'inactive',
    lastLogin: u.lastLogin ?? ('' as string),
    createdAt: u.createdAt ?? '',
    loginCount: 0,
  })), [apiUsers]);

  const roles = React.useMemo(() => apiRoles.map((r) => ({
    id: r.id,
    name: r.name,
    description: r.description,
    permissions: r.permissions || [],
    userCount: apiUsers.filter((u) => (u.roles || []).includes(r.id)).length,
  })), [apiRoles, apiUsers]);

  const permissions = React.useMemo(() => apiPermissions.map((perm) => ({
    id: perm.id,
    name: perm.name,
    description: perm.description,
  })), [apiPermissions]);

  const auditLogs = React.useMemo(() => apiAuditLogs.map((event, index) => ({
    id: event.id || String(index),
    timestamp: event.timestamp ?? '',
    user: event.username || 'system',
    eventType: event.eventType,
    action: event.action,
    resource: event.resource,
    details: event.details || {},
    severity: event.severity || 'info',
  })), [apiAuditLogs]);
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
      case 'locked': return <Tag color="warning">Locked</Tag>;
      default: return <Tag>Unknown</Tag>;
    }
  };

  // Get role tag color by privilege level
  const getRoleTagColor = (role: string) => {
    const normalized = role.toLowerCase();
    if (normalized.includes('admin')) return 'error';
    if (normalized.includes('investigat')) return 'success';
    if (normalized.includes('analyst')) return 'blue';
    return 'default';
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
      case 'info': return <Tag color="success">Info</Tag>;
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
      render: (id: string) => <span className="ol-mono">{id}</span>,
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
      render: (role: string) => <Tag color={getRoleTagColor(role)}>{role}</Tag>,
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
      render: (id: string) => <span className="ol-mono">{id}</span>,
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
      render: (id: string) => <span className="ol-mono">{id}</span>,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      render: (name: string) => <span className="ol-mono">{name}</span>,
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

  // Create user - persists server-side and refreshes the list.
  const createUser = async (values: any) => {
    setLoading(true);
    try {
      await createUserMutation.mutateAsync({
        username: values.username,
        password: values.password || 'ChangeMe123!',
        email: values.email,
        full_name: values.fullName,
      });
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setUserFormVisible(false);
    } catch (error) {
      console.error('Create user error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create role - persists server-side and refreshes the list.
  const createRole = async (values: any) => {
    setLoading(true);
    try {
      await createRoleMutation.mutateAsync({
        name: values.name,
        description: values.description,
      });
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setRoleFormVisible(false);
    } catch (error) {
      console.error('Create role error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create permission - persists server-side and refreshes the list.
  const createPermission = async (values: any) => {
    setLoading(true);
    try {
      await createPermissionMutation.mutateAsync({
        name: values.name,
        description: values.description,
      });
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
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

  // Users by Role - bar list items. Buckets by whichever role strings the
  // users actually carry, rather than assumed display names that never
  // matched the real (lowercase) role values and left every bucket at 0.
  const roleTagToColorVar: Record<string, string> = {
    error: 'var(--error-color)',
    success: 'var(--success-color)',
    blue: 'var(--primary-color)',
    default: 'var(--text-color-secondary)',
  };
  const usersByRoleItems = Array.from(new Set(users.map((u) => u.role)))
    .sort()
    .map((role) => ({
      key: role,
      label: role.charAt(0).toUpperCase() + role.slice(1),
      value: users.filter((u) => u.role === role).length,
      color: roleTagToColorVar[getRoleTagColor(role)] ?? roleTagToColorVar.default,
    }));

  // Events by Type - bar list items. Buckets by whichever event_type strings
  // the backend actually emits (authorization, data_access, ...) rather than
  // an assumed taxonomy that never matched and left every bucket at 0.
  const eventTypeColorPalette = [
    'var(--primary-color)', 'var(--success-color)', 'var(--warning-color)',
    'var(--error-color)', 'var(--purple-color)', 'var(--text-color-secondary)',
  ];
  const auditEventsByTypeItems = Array.from(new Set(auditLogs.map((l) => l.eventType || 'unknown')))
    .sort()
    .map((eventType, index) => ({
      key: eventType,
      label: eventType.split('_').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      value: auditLogs.filter((l) => (l.eventType || 'unknown') === eventType).length,
      color: eventTypeColorPalette[index % eventTypeColorPalette.length],
    }));

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
    <div className="security-center-page ol-page-body">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <PageHeader
          icon={<SafetyCertificateOutlined />}
          title="Security Center"
          subtitle="Enterprise-grade security and access control"
          actions={
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setUserFormVisible(true)}>
                New User
              </Button>
              <Button icon={<ExportOutlined />}>
                Export Audit
              </Button>
            </Space>
          }
        />
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="ol-stats-grid">
          <StatCard
            label="Total Users"
            value={users.length}
            icon={<UserOutlined />}
            accent="primary"
          />
          <StatCard
            label="Total Roles"
            value={roles.length}
            icon={<TeamOutlined />}
            accent="success"
          />
          <StatCard
            label="Total Permissions"
            value={permissions.length}
            icon={<SafetyOutlined />}
            accent="warning"
          />
          <StatCard
            label="Audit Logs"
            value={auditLogs.length}
            icon={<AuditOutlined />}
            accent="purple"
          />
        </div>
      </motion.div>

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
                <BarList items={usersByRoleItems} />
              </Card>

              {/* Users Table */}
              <Card title="All Users">
                <Table
                  columns={userColumns}
                  dataSource={users}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1360 }}
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
                  scroll={{ x: 1000 }}
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
                  scroll={{ x: 820 }}
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
              <div className="ol-row-2up" style={{ marginBottom: 24 }}>
                <Card title="Events by Type">
                  <BarList items={auditEventsByTypeItems} />
                </Card>
                <Card title="Events by Severity">
                  <Pie {...severityChartConfig} height={200} />
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 16 }}>
                    {severityChartConfig.data.map((d, index) => (
                      <span
                        key={d.severity}
                        style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--text-color-secondary)' }}
                      >
                        <span
                          style={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            background: severityChartConfig.color[index],
                            display: 'inline-block',
                          }}
                        />
                        {d.severity} ({d.count})
                      </span>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Audit Logs Table */}
              <Card title="Audit Logs">
                <Table
                  columns={auditLogColumns}
                  dataSource={filteredAuditLogs}
                  rowKey="id"
                  size="small"
                  scroll={{ x: 1100 }}
                />
              </Card>
            </div>
          )}

          {activeTab === 'encryption' && (
            <>
            <Alert type="info" showIcon style={{ marginBottom: 16 }}
              message="Sample data"
              description="Encryption metrics are illustrative - no backend endpoint provides them yet." />
            <div>
              <Title level={4} style={{ marginBottom: 24 }}>Encryption</Title>

              {/* Stats */}
              <div className="ol-row-quarter" style={{ marginBottom: 24 }}>
                <Card bodyStyle={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                    <span style={{ fontSize: 13, color: 'var(--text-color-tertiary)' }}>Total Encrypted</span>
                    <LockOutlined style={{ color: 'var(--primary-color)', fontSize: 16 }} />
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 600, marginTop: 8, color: 'var(--text-color)' }}>
                    {mockEncryptionStats.totalEncrypted.toLocaleString()}
                  </div>
                </Card>
                <Card bodyStyle={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                    <span style={{ fontSize: 13, color: 'var(--text-color-tertiary)' }}>Total Decrypted</span>
                    <UnlockOutlined style={{ color: 'var(--success-color)', fontSize: 16 }} />
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 600, marginTop: 8, color: 'var(--text-color)' }}>
                    {mockEncryptionStats.totalDecrypted.toLocaleString()}
                  </div>
                </Card>
                <Card bodyStyle={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                    <span style={{ fontSize: 13, color: 'var(--text-color-tertiary)' }}>Key Strength</span>
                    <KeyOutlined style={{ color: 'var(--warning-color)', fontSize: 16 }} />
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 600, marginTop: 8, color: 'var(--text-color)' }}>
                    {mockEncryptionStats.keyStrength}
                  </div>
                </Card>
                <Card bodyStyle={{ padding: '16px 20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                    <span style={{ fontSize: 13, color: 'var(--text-color-tertiary)' }}>Algorithms</span>
                    <CodeOutlined style={{ color: 'var(--purple-color)', fontSize: 16 }} />
                  </div>
                  <div style={{ fontSize: 24, fontWeight: 600, marginTop: 8, color: 'var(--text-color)' }}>
                    {mockEncryptionStats.algorithms.length}
                  </div>
                </Card>
              </div>

              {/* Encryption Info */}
              <div className="ol-row-2up">
                <Card title="Encryption Algorithms">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    {mockEncryptionStats.algorithms.map(alg => (
                      <Tag key={alg} color="blue" style={{ padding: '8px 16px', fontSize: 14 }}>
                        {alg}
                      </Tag>
                    ))}
                  </Space>
                </Card>
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
              </div>

              {/* Encryption Tools */}
              <Card title="Encryption Tools" style={{ marginTop: 24 }}>
                <div className="ol-row-2up">
                  <Card title="Encrypt Data" size="small" className="ol-subcard">
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
                  <Card title="Decrypt Data" size="small" className="ol-subcard">
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
                </div>
              </Card>
            </div>
          </>
          )}

          {activeTab === 'auth' && (
            <TabEmptyState
              label="Authentication"
              description="Authentication provider configuration has no backing endpoint yet."
            />
          )}

          {activeTab === 'authorization' && (
            <TabEmptyState
              label="Authorization"
              description="Fine-grained access control policy management has no backing endpoint yet."
            />
          )}

          {activeTab === 'compliance' && (
            <TabEmptyState
              label="Compliance"
              description="Compliance checks and reporting have no backing endpoint yet."
            />
          )}
        </Card>
      </motion.div>
    </div>
  );
};

export default SecurityCenter;
