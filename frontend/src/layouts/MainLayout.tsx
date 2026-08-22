import React, { useState, useEffect, useMemo } from 'react';
import { Layout, Menu, Dropdown, Avatar, Badge, Drawer } from 'antd';
import {
  DashboardOutlined,
  ProjectOutlined,
  RobotOutlined,
  SearchOutlined,
  SafetyCertificateOutlined,
  AlertOutlined,
  SettingOutlined,
  MenuOutlined,
  UserOutlined,
  LogoutOutlined,
  AppstoreOutlined,
  BarChartOutlined,
  SafetyOutlined,
  ThunderboltOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  CodeOutlined,
  GlobalOutlined,
  TeamOutlined,
  AuditOutlined,
  KeyOutlined,
  BellOutlined,
  FileSearchOutlined,
  SyncOutlined,
  ShareAltOutlined,
  EyeOutlined,
  FilterOutlined,
  NodeIndexOutlined,
  ClusterOutlined,
  BranchesOutlined,
  BlockOutlined,
  RightOutlined,
  DownOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import Cookies from 'js-cookie';
import { motion } from 'framer-motion';
import { useTheme, useAlerts } from '../hooks/useApi';
import { useWebSocket as useWebSocketContext } from '../contexts/WebSocketContext';
import LivePill from '../components/common/LivePill';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
  // Optional overrides. MainLayout manages theme itself via useTheme, so App
  // no longer has to thread these through every route (it never did, which
  // made the theme toggle throw on click).
  toggleTheme?: () => void;
  isDarkMode?: boolean;
}

interface MenuLeaf {
  key: string;
  icon: React.ReactNode;
  label: string;
}

interface MenuGroup extends MenuLeaf {
  children?: MenuLeaf[];
}

const mainMenuItems: MenuGroup[] = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: 'graph',
    icon: <ProjectOutlined />,
    label: 'Graph Explorer',
    children: [
      { key: 'graph-overview', label: 'Overview', icon: <AppstoreOutlined /> },
      { key: 'graph-network', label: 'Network Analysis', icon: <BarChartOutlined /> },
      { key: 'graph-paths', label: 'Path Finding', icon: <BranchesOutlined /> },
      { key: 'graph-communities', label: 'Communities', icon: <ClusterOutlined /> },
      { key: 'graph-temporal', label: 'Temporal Analysis', icon: <SyncOutlined /> },
      { key: 'graph-visualization', label: 'Visualization', icon: <EyeOutlined /> },
    ],
  },
  {
    key: 'ai',
    icon: <RobotOutlined />,
    label: 'AI Analytics',
    children: [
      { key: 'ai-anomalies', label: 'Anomaly Detection', icon: <AlertOutlined /> },
      { key: 'ai-entities', label: 'Entity Resolution', icon: <TeamOutlined /> },
      { key: 'ai-predictions', label: 'Predictive Analytics', icon: <FileSearchOutlined /> },
      { key: 'ai-classification', label: 'Classification', icon: <FilterOutlined /> },
      { key: 'ai-clustering', label: 'Clustering', icon: <ClusterOutlined /> },
      { key: 'ai-nlp', label: 'NLP Analysis', icon: <FileTextOutlined /> },
      { key: 'ai-recommendations', label: 'Recommendations', icon: <ThunderboltOutlined /> },
    ],
  },
  {
    key: 'scraping',
    icon: <SearchOutlined />,
    label: 'Scraping Hub',
    children: [
      { key: 'scraping-jobs', label: 'Scrape Jobs', icon: <DatabaseOutlined /> },
      { key: 'scraping-proxies', label: 'Proxy Manager', icon: <GlobalOutlined /> },
      { key: 'scraping-agents', label: 'User Agents', icon: <UserOutlined /> },
      { key: 'scraping-rate', label: 'Rate Limiting', icon: <BlockOutlined /> },
      { key: 'scraping-cache', label: 'Result Cache', icon: <CodeOutlined /> },
      { key: 'scraping-distributed', label: 'Distributed', icon: <ShareAltOutlined /> },
      { key: 'scraping-scheduler', label: 'Scheduler', icon: <SyncOutlined /> },
      { key: 'scraping-export', label: 'Data Export', icon: <FileTextOutlined /> },
      { key: 'scraping-monitoring', label: 'Monitoring', icon: <EyeOutlined /> },
    ],
  },
  {
    key: 'security',
    icon: <SafetyCertificateOutlined />,
    label: 'Security Center',
    children: [
      { key: 'security-users', label: 'User Management', icon: <TeamOutlined /> },
      { key: 'security-roles', label: 'RBAC', icon: <SafetyOutlined /> },
      { key: 'security-audit', label: 'Audit Logging', icon: <AuditOutlined /> },
      { key: 'security-encryption', label: 'Encryption', icon: <KeyOutlined /> },
      { key: 'security-auth', label: 'Authentication', icon: <UserOutlined /> },
      { key: 'security-authorization', label: 'Authorization', icon: <SafetyCertificateOutlined /> },
      { key: 'security-compliance', label: 'Compliance', icon: <FileTextOutlined /> },
    ],
  },
  {
    key: 'threat',
    icon: <AlertOutlined />,
    label: 'Threat Intelligence',
    children: [
      { key: 'threat-feeds', label: 'Threat Feeds', icon: <GlobalOutlined /> },
      { key: 'threat-iocs', label: 'IOC Management', icon: <DatabaseOutlined /> },
      { key: 'threat-analysis', label: 'Threat Analysis', icon: <FileSearchOutlined /> },
      { key: 'threat-alerts', label: 'Alert Management', icon: <BellOutlined /> },
      { key: 'threat-hunting', label: 'Threat Hunting', icon: <SearchOutlined /> },
      { key: 'threat-sharing', label: 'Intel Sharing', icon: <ShareAltOutlined /> },
      { key: 'threat-monitoring', label: 'Monitoring', icon: <EyeOutlined /> },
      { key: 'threat-graph', label: 'Threat Graph', icon: <ProjectOutlined /> },
    ],
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: 'Settings',
  },
];

const findLabel = (key: string): string => {
  for (const item of mainMenuItems) {
    if (item.key === key) return item.label;
    const child = item.children?.find((c) => c.key === key);
    if (child) return child.label;
  }
  return 'Dashboard';
};

const routeToKeyMap: Record<string, string> = {
  '/': 'dashboard',
  '/graph': 'graph',
  '/ai': 'ai',
  '/scraping': 'scraping',
  '/security': 'security',
  '/threat': 'threat',
  '/settings': 'settings',
};

const routeMap: Record<string, string> = {
  dashboard: '/',
  graph: '/graph',
  ai: '/ai',
  scraping: '/scraping',
  security: '/security',
  threat: '/threat',
  settings: '/settings',
};

const MainLayout: React.FC<MainLayoutProps> = ({ children, toggleTheme, isDarkMode }) => {
  const { theme: currentTheme, toggleTheme: toggleThemeInternal } = useTheme();
  const resolvedToggleTheme = toggleTheme ?? toggleThemeInternal;
  const resolvedIsDarkMode = isDarkMode ?? currentTheme === 'dark';
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeKey, setActiveKey] = useState('dashboard');
  const [openKeys, setOpenKeys] = useState<string[]>([]);
  const navigate = useNavigate();
  const location = useLocation();
  const { isConnected } = useWebSocketContext();
  // Single source for the notification count - the header bell and the
  // AI-assistant float button both read this same query, so they can never
  // disagree the way a hard-coded 5 and a Math.random() mock used to.
  const { data: activeAlerts } = useAlerts({ status: 'active' });
  const notifications = activeAlerts?.length ?? 0;

  const user = {
    name: 'Admin',
    avatar: 'A',
    role: 'Administrator',
  };

  useEffect(() => {
    const currentKey = routeToKeyMap[location.pathname] || 'dashboard';
    setActiveKey(currentKey);
  }, [location.pathname]);

  // Auto-open the group containing the active item. Only one group is open
  // at a time - enforced again in onOpenChange for user-driven toggles.
  useEffect(() => {
    const parent = mainMenuItems.find((item) => item.children?.some((c) => c.key === activeKey));
    setOpenKeys(parent ? [parent.key] : []);
  }, [activeKey]);

  const handleMenuClick = (key: string) => {
    setActiveKey(key);
    setMobileMenuOpen(false);
    navigate(routeMap[key] || '/');
  };

  const handleLogout = () => {
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');
    navigate('/login');
  };

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profile',
      icon: <UserOutlined />,
    },
    {
      key: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      danger: true,
      onClick: handleLogout,
    },
  ];

  // Shared item config for both the desktop and mobile menus - antd v5
  // deprecates the JSX Menu.Item/Menu.SubMenu children form in favor of this.
  const menuItems = useMemo(
    () =>
      mainMenuItems.map((item) => ({
        key: item.key,
        icon: item.icon,
        label: item.label,
        children: item.children?.map((child) => ({
          key: child.key,
          icon: child.icon,
          label: child.label,
        })),
      })),
    []
  );

  const currentPageLabel = useMemo(() => findLabel(activeKey), [activeKey]);

  const mobileMenu = (
    <Drawer
      title="Menu"
      placement="left"
      onClose={() => setMobileMenuOpen(false)}
      open={mobileMenuOpen}
      width={256}
      styles={{ body: { padding: 0 }, header: { display: 'none' } }}
    >
      <Menu mode="inline" selectedKeys={[activeKey]} items={menuItems} onClick={({ key }) => handleMenuClick(key)} />
    </Drawer>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Mobile Menu */}
      {mobileMenu}

      {/* Desktop Sidebar */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(val) => setCollapsed(val)}
        width={256}
        collapsedWidth={80}
        breakpoint="lg"
        onBreakpoint={(broken) => {
          if (broken) {
            setCollapsed(true);
          }
        }}
        className="main-sidebar"
        style={{
          position: 'fixed',
          height: '100vh',
          zIndex: 100,
        }}
      >
        <div
          style={{
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            height: 64,
            overflow: 'hidden',
          }}
        >
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              style={{ display: 'flex', alignItems: 'center', gap: 10 }}
            >
              <NodeIndexOutlined style={{ fontSize: 24, color: '#1890ff' }} />
              <span
                style={{
                  fontSize: 18,
                  fontWeight: 700,
                  letterSpacing: '-0.01em',
                  color: 'white',
                  whiteSpace: 'nowrap',
                }}
              >
                OpenLens
              </span>
            </motion.div>
          ) : (
            <NodeIndexOutlined style={{ fontSize: 24, color: '#1890ff' }} />
          )}
        </div>

        <Menu
          mode="inline"
          theme="dark"
          selectedKeys={[activeKey]}
          openKeys={openKeys}
          onOpenChange={(keys) => {
            const latest = keys.find((key) => !openKeys.includes(key));
            setOpenKeys(latest ? [latest] : []);
          }}
          onClick={({ key }) => handleMenuClick(key)}
          items={menuItems}
          style={{
            height: 'calc(100vh - 64px)',
            borderRight: 0,
          }}
          className="main-menu"
        />
      </Sider>

      {/* Main Content */}
      <Layout className={`main-content-shell${collapsed ? ' collapsed' : ''}`}>
        {/* Header */}
        <Header
          style={{
            position: 'sticky',
            top: 0,
            zIndex: 20,
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            height: 64,
            background: 'var(--card-bg)',
            borderBottom: '1px solid var(--border-color-secondary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <button
              type="button"
              className="ol-icon-btn mobile-menu-btn"
              style={{ display: 'none', border: 'none' }}
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open menu"
            >
              <MenuOutlined />
            </button>
            <button
              type="button"
              className="ol-icon-btn"
              style={{ fontSize: 16, border: 'none' }}
              onClick={resolvedToggleTheme}
              aria-label="Toggle theme"
            >
              {resolvedIsDarkMode ? <SunOutlined /> : <MoonOutlined />}
            </button>
            <span style={{ width: 1, height: 20, background: 'var(--border-color)' }} />
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14 }}>
              <span style={{ color: 'var(--text-color-tertiary)' }}>OpenLens</span>
              <RightOutlined style={{ fontSize: 10, color: 'var(--text-color-tertiary)' }} />
              <span style={{ color: 'var(--text-color)' }}>{currentPageLabel}</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <LivePill connected={isConnected} />

            <Badge count={notifications} size="small" offset={[-4, 4]}>
              <button type="button" className="ol-icon-btn" style={{ border: 'none' }} aria-label="Notifications">
                <BellOutlined style={{ fontSize: 18 }} />
              </button>
            </Badge>

            <button type="button" className="ol-icon-btn" style={{ border: 'none' }} aria-label="Help">
              <QuestionCircleOutlined style={{ fontSize: 18 }} />
            </button>

            <Dropdown menu={{ items: userMenuItems }} trigger={['click']} placement="bottomRight">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: 8,
                  transition: 'background 0.2s',
                }}
              >
                <Avatar size={32} style={{ background: '#1890ff', color: 'white' }}>
                  {user.avatar}
                </Avatar>
                <div style={{ lineHeight: 1.2 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-color)' }}>{user.name}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-color-tertiary)' }}>{user.role}</div>
                </div>
                <DownOutlined style={{ fontSize: 10, color: 'var(--text-color-tertiary)' }} />
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* Content */}
        <Content
          style={{
            padding: 24,
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            {children}
          </motion.div>
        </Content>
      </Layout>
    </Layout>
  );
};

// antd v5 ships no Sun/MoonOutlined icon - kept as small inline SVGs.
const SunOutlined = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5" />
    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </svg>
);

const MoonOutlined = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
  </svg>
);

export default MainLayout;
