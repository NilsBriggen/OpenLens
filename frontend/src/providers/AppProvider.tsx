import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme } from 'antd';
import { WebSocketProvider } from '../contexts/WebSocketContext';
import { useTheme } from '../hooks/useApi';

interface AppProviderProps {
  children: React.ReactNode;
}

// Create a single query client instance to be shared across the app
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
    mutations: {
      retry: 1,
    },
  },
});

const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const { theme: currentTheme } = useTheme();

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          algorithm: currentTheme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 8,
          },
          components: {
            Button: {
              borderRadius: 6,
            },
            Card: {
              borderRadius: 8,
            },
            Input: {
              borderRadius: 6,
            },
            Select: {
              borderRadius: 6,
            },
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

export { queryClient };
export default AppProvider;
