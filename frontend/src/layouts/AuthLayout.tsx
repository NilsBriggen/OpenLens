import React from 'react';
import { Layout, theme } from 'antd';
import { motion } from 'framer-motion';
import { NodeIndexOutlined } from '@ant-design/icons';

const { Content } = Layout;

interface AuthLayoutProps {
  children: React.ReactNode;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  const { token } = theme.useToken();

  return (
    <Layout style={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${token.colorPrimary} 0%, #096dd9 100%)`,
    }}>
      <Content style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{
            width: '100%',
            maxWidth: 440,
          }}
        >
          <div style={{
            background: token.colorBgBase,
            borderRadius: 16,
            padding: 40,
            boxShadow: '0 8px 48px rgba(0, 0, 0, 0.3)',
          }}>
            {/* Logo */}
            <div style={{
              textAlign: 'center',
              marginBottom: 32,
            }}>
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5 }}
                style={{
                  width: 64,
                  height: 64,
                  background: `linear-gradient(135deg, ${token.colorPrimary}, #096dd9)`,
                  borderRadius: 16,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                }}
              >
                <NodeIndexOutlined style={{ fontSize: 32, color: 'white' }} />
              </motion.div>
              <h1 style={{
                fontSize: 24,
                fontWeight: 700,
                color: token.colorTextBase,
                margin: 0,
              }}>
                OpenLens
              </h1>
              <p style={{
                fontSize: 14,
                color: token.colorTextSecondary,
                margin: '8px 0 0',
              }}>
                Enterprise-Grade OSINT Platform
              </p>
            </div>

            {/* Content */}
            {children}

            {/* Footer */}
            <div style={{
              textAlign: 'center',
              marginTop: 32,
              paddingTop: 24,
              borderTop: `1px solid ${token.colorBorderSecondary}`,
            }}>
              <p style={{
                fontSize: 12,
                color: token.colorTextSecondary,
                margin: 0,
              }}>
                © {new Date().getFullYear()} OpenLens. All rights reserved.
              </p>
            </div>
          </div>
        </motion.div>
      </Content>
    </Layout>
  );
};

export default AuthLayout;
