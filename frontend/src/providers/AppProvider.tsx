import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme } from 'antd';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { useTheme } from '../hooks';

interface AppProviderProps {
  children: React.ReactNode;
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: 2,
    },
  },
});

const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const { theme: currentTheme, isDark } = useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={
          algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 8,
          },
        }}
      >
        <WebSocketProvider>
          {children}
        </WebSocketProvider>
      </ConfigProvider>
    </QueryClientProvider>
  );
};

export default AppProvider;
