import React, { useState, useRef, useEffect } from 'react';
import { Button, Input, Card, List, Avatar, Typography, Space, Tooltip, Spin, Divider, Drawer, Tag } from 'antd';
import { RobotOutlined, SendOutlined, CloseOutlined, UserOutlined, LoadingOutlined, CopyOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    sources?: string[];
  };
}

interface AIChatAssistantProps {
  visible: boolean;
  onClose: () => void;
  context?: string; // Current page/context for AI to understand
}

const AIChatAssistant: React.FC<AIChatAssistantProps> = ({ visible, onClose, context = 'general' }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello! I'm **OpenLens AI Assistant**. I can help you with:

- **Graph Analysis**: "Find connections between Person A and Company X"
- **Threat Intelligence**: "What are the latest IOCs?"
- **Scraping**: "Create a new scrape job for example.com"
- **Security**: "List all active users"
- **General**: "What can you do?"

Ask me anything about your data!`,
      timestamp: new Date(),
      metadata: { model: 'OpenLens-AI' },
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sample suggestions based on context
  const contextSuggestions: Record<string, string[]> = {
    dashboard: [
      'What are the latest activities?',
      'Show me system health',
      'What are the key metrics?',
      'Summarize recent alerts',
    ],
    graph: [
      'Find shortest path between nodes',
      'Detect communities in the graph',
      'Calculate centrality metrics',
      'Show me nodes with highest degree',
      'Find all connections for this node',
    ],
    ai: [
      'Detect anomalies in recent data',
      'Resolve these entities',
      'Predict connections between nodes',
      'Cluster similar nodes',
      'Analyze this text',
    ],
    scraping: [
      'Create a new scrape job',
      'Show active proxy servers',
      'Check rate limits',
      'View recent scrape jobs',
      'Export scraped data',
    ],
    security: [
      'List all users',
      'Show audit logs',
      'Check encryption status',
      'Review RBAC permissions',
      'Test authentication',
    ],
    threat: [
      'Show latest threat feeds',
      'List recent IOCs',
      'Analyze this threat',
      'Create new alert',
      'Start threat hunt',
    ],
    general: [
      'What can you do?',
      'Show me a tutorial',
      'Explain graph analysis',
      'Help with threat intelligence',
    ],
  };

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Update suggestions when context changes
  useEffect(() => {
    setSuggestions(contextSuggestions[context] || contextSuggestions.general);
  }, [context]);

  // Mock AI response (replace with actual API call)
  const getAIResponse = async (message: string): Promise<string> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Mock responses based on input
    const mockResponses: Record<string, string> = {
      'hello': `Hello! How can I help you with OpenLens today?`,
      'what can you do': `I can help you with:
- **Graph Analysis**: Query and analyze your graph data
- **Threat Intelligence**: Manage IOCs, alerts, and threat feeds
- **AI Analytics**: Detect anomalies, resolve entities, make predictions
- **Scraping**: Create and manage web scraping jobs
- **Security**: Manage users, roles, and audit logs
- **General**: Answer questions about the platform`,
      'find connections': `To find connections, you can:
1. Use the **Graph Explorer** page
2. Run a query like: **MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 100**
3. Use path finding algorithms: shortest path, all paths, Dijkstra, A*

Would you like me to run a specific query?`,
      'latest iocs': `Here are the latest IOCs from our threat intelligence feeds:

**Recent IOCs:**
- **192.168.1.100** (IP) - Malicious C2 server - Severity: Critical
- **bad-domain.com** (Domain) - Phishing site - Severity: High
- **a1b2c3d4...** (Hash) - Ransomware - Severity: Critical

You can view all IOCs in the **Threat Intelligence > IOC Management** section.`,
      'create scrape job': `To create a scrape job:

1. Go to **Scraping Hub**
2. Click **New Scrape Job**
3. Enter the URLs (one per line)
4. Set depth (1-10)
5. Configure options:
   - Use proxy rotation
   - Enable caching
   - Render JavaScript
6. Click **Create Job**

Would you like me to create a sample job for you?`,
      'list users': `Here are the users in the system:

**Active Users:**
- **admin** - Administrator (Last login: Today)
- **analyst1** - Analyst (Last login: Today)
- **analyst2** - Analyst (Last login: Yesterday)

**Inactive Users:**
- **viewer1** - Viewer (Last login: 1 week ago)

You can manage users in the **Security Center > User Management** section.`,
    };

    const lowerMessage = message.toLowerCase();
    for (const [key, response] of Object.entries(mockResponses)) {
      if (lowerMessage.includes(key)) {
        return response;
      }
    }

    // Generic response
    return `I understand you're asking about: **${message}**

Let me analyze this and provide relevant information from your OpenLens data.`;
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await getAIResponse(input.trim());
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date(),
        metadata: {
          model: 'OpenLens-AI-v7',
          tokens: Math.floor(Math.random() * 1000) + 500,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('AI response error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getAvatar = (role: string) => {
    switch (role) {
      case 'assistant':
        return <Avatar icon={<RobotOutlined />} style={{ background: '#1890ff' }} />;
      case 'user':
        return <Avatar icon={<UserOutlined />} style={{ background: '#52c41a' }} />;
      default:
        return <Avatar icon={<RobotOutlined />} />;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Drawer
      title={
        <Space>
          <RobotOutlined style={{ color: '#1890ff', fontSize: 20 }} />
          <Title level={4} style={{ margin: 0 }}>AI Assistant</Title>
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={visible}
      width={400}
      maskClosable={false}
      closable={true}
      headerStyle={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}
      bodyStyle={{ padding: 0, height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}
      footerStyle={{ padding: 16, borderTop: '1px solid #f0f0f0' }}
      footer={
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ flex: 1 }}
          />
          <Button
            type="primary"
            icon={loading ? <LoadingOutlined /> : <SendOutlined />}
            onClick={handleSend}
            disabled={!input.trim() || loading}
          />
        </Space.Compact>
      }
    >
      {/* Messages Container */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
        <List
          dataSource={messages}
          renderItem={(message) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              style={{ marginBottom: 16 }}
            >
              <List.Item
                style={{
                  padding: 0,
                  border: 'none',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    gap: 12,
                    alignItems: 'flex-start',
                  }}
                >
                  {getAvatar(message.role)}
                  <div
                    style={{
                      flex: 1,
                      maxWidth: 'calc(100% - 40px)',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: 8,
                      }}
                    >
                      <Text
                        type="secondary"
                        style={{ fontSize: 12 }}
                      >
                        {message.role === 'assistant' ? 'AI Assistant' : 'You'}
                      </Text>
                      <Text
                        type="secondary"
                        style={{ fontSize: 10 }}
                      >
                        {formatTime(message.timestamp)}
                      </Text>
                    </div>
                    
                    <div
                      style={{
                        background: message.role === 'assistant' 
                          ? 'var(--bg-color-secondary)' 
                          : '#e6f7ff',
                        padding: 12,
                        borderRadius: 12,
                        border: message.role === 'assistant' 
                          ? '1px solid var(--border-color)' 
                          : '1px solid #91d5ff',
                      }}
                    >
                      <ReactMarkdown
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            return inline ? (
                              <code
                                style={{
                                  background: 'rgba(0, 0, 0, 0.1)',
                                  padding: '2px 4px',
                                  borderRadius: 4,
                                  fontFamily: 'monospace',
                                }}
                                {...props}
                              >
                                {children}
                              </code>
                            ) : (
                              <pre
                                style={{
                                  background: 'rgba(0, 0, 0, 0.1)',
                                  padding: 12,
                                  borderRadius: 8,
                                  overflowX: 'auto',
                                  margin: '8px 0',
                                }}
                              >
                                <code {...props}>
                                  {children}
                                </code>
                              </pre>
                            );
                          },
                          table({ children }) {
                            return (
                              <table
                                style={{
                                  borderCollapse: 'collapse',
                                  width: '100%',
                                  margin: '8px 0',
                                }}
                              >
                                {children}
                              </table>
                            );
                          },
                          th({ children }) {
                            return (
                              <th
                                style={{
                                  border: '1px solid #f0f0f0',
                                  padding: 8,
                                  background: 'var(--bg-color-secondary)',
                                  textAlign: 'left',
                                }}
                              >
                                {children}
                              </th>
                            );
                          },
                          td({ children }) {
                            return (
                              <td
                                style={{
                                  border: '1px solid #f0f0f0',
                                  padding: 8,
                                }}
                              >
                                {children}
                              </td>
                            );
                          },
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                      
                      {message.metadata && (
                        <div
                          style={{
                            marginTop: 8,
                            display: 'flex',
                            gap: 8,
                            flexWrap: 'wrap',
                          }}
                        >
                          {message.metadata.model && (
                            <Tag color="blue" style={{ fontSize: 10 }}>
                              {message.metadata.model}
                            </Tag>
                          )}
                          {message.metadata.tokens && (
                            <Tag color="green" style={{ fontSize: 10 }}>
                              {message.metadata.tokens} tokens
                            </Tag>
                          )}
                          {message.metadata.sources && (
                            <Tooltip title={message.metadata.sources.join(', ')}>
                              <Tag color="purple" style={{ fontSize: 10 }}>
                                {message.metadata.sources.length} sources
                              </Tag>
                            </Tooltip>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </List.Item>
            </motion.div>
          )}
        />
        
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            style={{ marginBottom: 16 }}
          >
            <List.Item style={{ padding: 0, border: 'none' }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <Avatar icon={<LoadingOutlined spin />} style={{ background: '#1890ff' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>AI Assistant</Text>
                  </div>
                  <div style={{ background: 'var(--bg-color-secondary)', padding: 12, borderRadius: 12, border: '1px solid var(--border-color)' }}>
                    <Spin tip="Thinking..." size="small" />
                  </div>
                </div>
              </div>
            </List.Item>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length === 1 && !loading && (
        <div style={{ padding: 16, borderTop: '1px solid #f0f0f0' }}>
          <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
            Suggestions:
          </Text>
          <Space wrap>
            {suggestions.map((suggestion, index) => (
              <Button
                key={index}
                type="dashed"
                size="small"
                onClick={() => handleSuggestionClick(suggestion)}
                style={{ marginBottom: 8 }}
              >
                {suggestion}
              </Button>
            ))}
          </Space>
        </div>
      )}
    </Drawer>
  );
};

export default AIChatAssistant;
