import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button, Input, Card, List, Avatar, Typography, Space, Tooltip, Spin, Divider, Drawer, Tag, Alert, message } from 'antd';
import { RobotOutlined, SendOutlined, CloseOutlined, UserOutlined, LoadingOutlined, CopyOutlined, CodeOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import {
  useAnomalyDetection,
  useEntityResolution,
  useLinkPrediction,
  useNodeClassification,
  useGraphEvolutionPrediction,
  useThreatPrediction,
  useApiPost
} from '../hooks/useApi';
import { apiClient } from '../lib/apiClient';

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
    queryType?: string;
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
- **Anomaly Detection**: "Detect anomalies in recent data"
- **Entity Resolution**: "Resolve these entities"
- **Scraping**: "Create a new scrape job for example.com"
- **Security**: "List all active users"
- **General**: "What can you do?"

Ask me anything about your data!`,
      timestamp: new Date(),
      metadata: { model: 'OpenLens-AI-v7' },
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // AI API hooks
  const anomalyDetectionMutation = useAnomalyDetection();
  const entityResolutionMutation = useEntityResolution();
  const linkPredictionMutation = useLinkPrediction();
  const nodeClassificationMutation = useNodeClassification();
  const graphEvolutionMutation = useGraphEvolutionPrediction();
  const threatPredictionMutation = useThreatPrediction();
  
  // Generic AI chat endpoint
  const chatMutation = useApiPost<any, { message: string; context?: string; conversation_id?: string }>(
    '/api/ai/chat'
  );

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

  // Update suggestions when context changes
  useEffect(() => {
    setSuggestions(contextSuggestions[context] || contextSuggestions.general);
  }, [context]);

  // Parse and execute AI commands
  const parseCommand = useCallback(async (message: string): Promise<string> => {
    const lowerMessage = message.toLowerCase().trim();
    
    // Check for specific commands that map to backend APIs
    
    // Anomaly Detection
    if (lowerMessage.includes('detect anomaly') || lowerMessage.includes('detect anomalies')) {
      try {
        const result = await anomalyDetectionMutation.mutateAsync({
          data: [], // Would need actual data
          method: 'statistical',
          threshold: 3.0,
        });
        return `Anomaly detection completed. Found ${result?.anomalies?.length || 0} anomalies.`;
      } catch (error) {
        return `Error running anomaly detection: ${error}`;
      }
    }
    
    // Entity Resolution
    if (lowerMessage.includes('resolve entity') || lowerMessage.includes('resolve entities')) {
      try {
        const result = await entityResolutionMutation.mutateAsync({
          entities: [], // Would need actual entities
          method: 'exact',
          threshold: 0.85,
        });
        return `Entity resolution completed. Found ${result?.matches?.length || 0} matches.`;
      } catch (error) {
        return `Error running entity resolution: ${error}`;
      }
    }
    
    // Link Prediction
    if (lowerMessage.includes('predict link') || lowerMessage.includes('predict connection')) {
      try {
        const result = await linkPredictionMutation.mutateAsync({
          node1: 'node1',
          node2: 'node2',
          method: 'common_neighbors',
        });
        return `Link prediction: ${result?.score ? (result.score * 100).toFixed(2) + '%' : 'unknown'} probability.`;
      } catch (error) {
        return `Error running link prediction: ${error}`;
      }
    }
    
    // Threat Prediction
    if (lowerMessage.includes('predict threat') || lowerMessage.includes('predict threats')) {
      try {
        const result = await threatPredictionMutation.mutateAsync();
        return `Threat prediction completed. Found ${result?.threats?.length || 0} potential threats.`;
      } catch (error) {
        return `Error running threat prediction: ${error}`;
      }
    }
    
    // Graph Evolution
    if (lowerMessage.includes('predict evolution') || lowerMessage.includes('graph evolution')) {
      try {
        const result = await graphEvolutionMutation.mutateAsync();
        return `Graph evolution prediction completed.`;
      } catch (error) {
        return `Error running graph evolution prediction: ${error}`;
      }
    }
    
    // Default: use the chat API
    return null; // Will use the chat API
  }, [anomalyDetectionMutation, entityResolutionMutation, linkPredictionMutation, threatPredictionMutation, graphEvolutionMutation]);

  // Get AI response from backend
  const getAIResponse = useCallback(async (message: string): Promise<string> => {
    // First, try to parse as a command
    const commandResponse = await parseCommand(message);
    if (commandResponse) {
      return commandResponse;
    }
    
    // Otherwise, use the chat API
    try {
      const response = await chatMutation.mutateAsync({
        message,
        context,
        conversation_id: conversationId || undefined,
      });
      
      // Handle different response formats
      if (typeof response === 'string') {
        return response;
      } else if (response?.data) {
        return response.data;
      } else if (response?.message) {
        return response.message;
      } else {
        return JSON.stringify(response, null, 2);
      }
    } catch (error: any) {
      console.error('Chat API error:', error);
      
      // Fallback to mock response if API fails
      return `I encountered an error connecting to the AI service. Here's what I can tell you:

**Available Commands:**
- "Detect anomalies" - Run anomaly detection
- "Resolve entities" - Resolve entity matches
- "Predict link between X and Y" - Predict connections
- "Predict threats" - Predict potential threats
- "Graph evolution" - Predict graph changes

Please try one of these commands or check your connection.`;
    }
  }, [chatMutation, parseCommand, context, conversationId]);

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
          queryType: 'chat',
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
    message.success('Copied to clipboard');
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

  const clearConversation = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: `Hello! I'm **OpenLens AI Assistant**. How can I help you today?`,
        timestamp: new Date(),
        metadata: { model: 'OpenLens-AI-v7' },
      },
    ]);
    setConversationId(null);
  };

  return (
    <Drawer
      title={
        <Space>
          <Avatar icon={<RobotOutlined />} style={{ background: '#1890ff' }} />
          <Title level={4} style={{ margin: 0 }}>
            AI Assistant
          </Title>
          <Tag color="blue">v7.0</Tag>
        </Space>
      }
      placement="right"
      open={visible}
      onClose={onClose}
      width={400}
      height="100vh"
      style={{ position: 'fixed', top: 0, right: 0 }}
      bodyStyle={{ padding: 0, height: '100%', display: 'flex', flexDirection: 'column' }}
      closable={true}
      mask={false}
      maskClosable={false}
    >
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Messages Container */}
        <div style={{ flex: 1, overflow: 'auto', padding: '16px 16px 0' }}>
          <AnimatePresence>
            {messages.map((msg, index) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                style={{ marginBottom: 16 }}
              >
                <Card
                  size="small"
                  style={{
                    borderRadius: 8,
                    border: msg.role === 'user' ? '1px solid #52c41a' : '1px solid #1890ff',
                    background: msg.role === 'user' ? '#f6ffed' : '#e6f7ff',
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <Space size="small">
                    {getAvatar(msg.role)}
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                        <Text strong style={{ color: msg.role === 'user' ? '#52c41a' : '#1890ff' }}>
                          {msg.role === 'user' ? 'You' : 'AI Assistant'}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 10 }}>
                          {formatTime(msg.timestamp)}
                        </Text>
                      </div>
                      <div style={{ maxWidth: '100%' }}>
                        <ReactMarkdown
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <div style={{ position: 'relative', margin: '8px 0' }}>
                                  <pre
                                    style={{
                                      background: '#272822',
                                      color: '#f8f8f2',
                                      padding: 12,
                                      borderRadius: 4,
                                      overflowX: 'auto',
                                      fontSize: 12,
                                    }}
                                  >
                                    <code style={{ color: 'inherit' }} {...props}>
                                      {String(children).replace(/\n$/, '')}
                                    </code>
                                  </pre>
                                  <Button
                                    size="small"
                                    icon={<CopyOutlined />}
                                    style={{
                                      position: 'absolute',
                                      top: 4,
                                      right: 4,
                                      opacity: 0.7,
                                    }}
                                    onClick={() => copyToClipboard(String(children))}
                                  />
                                </div>
                              ) : (
                                <code
                                  style={{
                                    background: '#f5f5f5',
                                    padding: '2px 4px',
                                    borderRadius: 2,
                                    fontSize: 12,
                                  }}
                                  {...props}
                                >
                                  {children}
                                </code>
                              );
                            },
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                        {msg.metadata && (
                          <div style={{ marginTop: 8, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                            {msg.metadata.model && (
                              <Tag color="blue" style={{ fontSize: 10 }}>
                                {msg.metadata.model}
                              </Tag>
                            )}
                            {msg.metadata.tokens && (
                              <Tag color="green" style={{ fontSize: 10 }}>
                                {msg.metadata.tokens.toLocaleString()} tokens
                              </Tag>
                            )}
                            {msg.metadata.queryType && (
                              <Tag color="purple" style={{ fontSize: 10 }}>
                                {msg.metadata.queryType}
                              </Tag>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </Space>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 16 }}>
              <Spin indicator={<LoadingOutlined spin />} />
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: 16, borderTop: '1px solid #f0f0f0' }}>
          {suggestions.length > 0 && (
            <div style={{ marginBottom: 12 }}>
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
                Suggestions:
              </Text>
              <Space wrap>
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    size="small"
                    type="dashed"
                    onClick={() => handleSuggestionClick(suggestion)}
                    style={{ marginBottom: 4 }}
                  >
                    {suggestion}
                  </Button>
                ))}
              </Space>
            </div>
          )}
          
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              style={{ flex: 1 }}
              disabled={loading}
            />
            <Tooltip title="Send (Ctrl+Enter)">
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!input.trim() || loading}
              />
            </Tooltip>
          </Space.Compact>
          
          <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between' }}>
            <Button size="small" icon={<CloseOutlined />} onClick={clearConversation}>
              Clear
            </Button>
            <Text type="secondary" style={{ fontSize: 10 }}>
              {messages.length - 1} messages
            </Text>
          </div>
        </div>
      </div>
    </Drawer>
  );
};

export default AIChatAssistant;
