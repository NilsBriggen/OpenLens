import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Dropdown, Avatar, Badge, theme, Drawer } from 'antd';
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
  HomeOutlined,
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
  BlockOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import Cookies from 'js-cookie';
import { motion } from 'framer-motion';
import { useTheme } from '../hooks/useApi';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  onRouteChange?: (path: string) => void;
  children: React.ReactNode;
  // Optional overrides. MainLayout manages theme itself via useTheme, so App
  // no longer has to thread these through every route (it never did, which
  // made the theme toggle throw on click).
  toggleTheme?: () => void;
  isDarkMode?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children, toggleTheme, isDarkMode, onRouteChange }) => {
  const { theme: currentTheme, toggleTheme: toggleThemeInternal } = useTheme();
  const resolvedToggleTheme = toggleTheme ?? toggleThemeInternal;
  const resolvedIsDarkMode = isDarkMode ?? currentTheme === 'dark';
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeKey, setActiveKey] = useState('dashboard');
  const [notifications, setNotifications] = useState(5);
  const navigate = useNavigate();
  const location = useLocation();

  const user = {
    name: 'Admin',
    avatar: 'A',
    role: 'Administrator'
  };

  // Map routes to menu keys
  const routeToKeyMap: Record<string, string> = {
    '/': 'dashboard',
    '/graph': 'graph',
    '/ai': 'ai',
    '/scraping': 'scraping',
    '/security': 'security',
    '/threat': 'threat',
    '/settings': 'settings'
  };

  useEffect(() => {
    const currentKey = routeToKeyMap[location.pathname] || 'dashboard';
    setActiveKey(currentKey);
  }, [location.pathname]);

  const handleMenuClick = (key: string) => {
    setActiveKey(key);
    setMobileMenuOpen(false);
    
    const routeMap: Record<string, string> = {
      'dashboard': '/',
      'graph': '/graph',
      'ai': '/ai',
      'scraping': '/scraping',
      'security': '/security',
      'threat': '/threat',
      'settings': '/settings'
    };
    
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

  const mainMenuItems = [
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

  const renderMenuItem = (item: any) => {
    if (item.children) {
      return (
        <Menu.SubMenu
          key={item.key}
          icon={item.icon}
          title={item.label}
          popupClassName="main-menu-submenu"
        >
          {item.children.map(renderMenuItem)}
        </Menu.SubMenu>
      );
    }
    return (
      <Menu.Item
        key={item.key}
        icon={item.icon}
        onClick={() => handleMenuClick(item.key)}
      >
        {item.label}
      </Menu.Item>
    );
  };

  const mobileMenu = (
    <Drawer
      title="Menu"
      placement="left"
      onClose={() => setMobileMenuOpen(false)}
      open={mobileMenuOpen}
      width={256}
      bodyStyle={{ padding: 0 }}
      headerStyle={{ display: 'none' }}
    >
      <Menu
        mode="inline"
        selectedKeys={[activeKey]}
        items={mainMenuItems.map(item => ({
          key: item.key,
          icon: item.icon,
          label: item.label,
          children: item.children?.map(child => ({
            key: child.key,
            icon: child.icon,
            label: child.label,
          })),
        }))}
        onClick={({ key }) => handleMenuClick(key)}
      />
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
        <div className="logo-container" style={{
          padding: 16,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start',
          height: 64,
          overflow: 'hidden',
        }}>
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <NodeIndexOutlined style={{ fontSize: 24, color: '#1890ff' }} />
              <span style={{
                fontSize: 18,
                fontWeight: 700,
                color: 'white',
                whiteSpace: 'nowrap',
              }}>
                OpenLens
              </span>
            </motion.div>
          ) : (
            <NodeIndexOutlined style={{ fontSize: 24, color: '#1890ff' }} />
          )}
        </div>
        
        <Menu
          mode="inline"
          selectedKeys={[activeKey]}
          style={{
            height: 'calc(100vh - 64px)',
            borderRight: 0,
          }}
          className="main-menu"
        >
          {mainMenuItems.map(renderMenuItem)}
        </Menu>
      </Sider>
      
      {/* Main Content */}
      <Layout style={{
        marginLeft: collapsed ? 80 : 256,
        transition: 'margin-left 0.2s ease',
      }}>
        {/* Header */}
        <Header style={{
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 64,
          background: theme.useToken().token.colorBgBase,
          borderBottom: `1px solid ${theme.useToken().token.colorBorderSecondary}`,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}>
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileMenuOpen(true)}
              style={{
                display: 'none',
              }}
              className="mobile-menu-btn"
            />
            <Button
              type="text"
              icon={resolvedIsDarkMode ? <SunOutlined /> : <MoonOutlined />}
              onClick={resolvedToggleTheme}
              style={{
                fontSize: 16,
              }}
            />
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}>
            <Badge count={notifications} size="small">
              <Button
                type="text"
                icon={<BellOutlined style={{ fontSize: 18 }} />}
                style={{
                  padding: '0 8px',
                }}
              />
            </Badge>
            
            <Dropdown
              menu={{ items: userMenuItems }}
              trigger={['click']}
              placement="bottomRight"
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                cursor: 'pointer',
                padding: '8px 12px',
                borderRadius: 8,
                transition: 'background 0.3s',
              }}
              >
                <Avatar
                  style={{
                    background: '#1890ff',
                    color: 'white',
                  }}
                >
                  {user.avatar}
                </Avatar>
                <div style={{
                  display: 'none',
                }}>
                  <div style={{ fontWeight: 600 }}>{user.name}</div>
                  <div style={{ fontSize: 12, color: theme.useToken().token.colorTextSecondary }}>
                    {user.role}
                  </div>
                </div>
              </div>
            </Dropdown>
          </div>
        </Header>
        
        {/* Content */}
        <Content style={{
          padding: 24,
          minHeight: 'calc(100vh - 64px)',
        }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </Content>
      </Layout>
    </Layout>
  );
};

// Temporary icons for theme toggle
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
