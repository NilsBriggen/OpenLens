import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface TimelineEvent {
  id: string;
  title: string;
  start: string;
  end?: string;
  description?: string;
  category?: string;
  icon?: string;
  color?: string;
}

const TimelineVisualization: React.FC = () => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [sampleData, setSampleData] = useState<boolean>(false);
  const timelineRef = useRef<HTMLDivElement>(null);

  // Sample data for demonstration
  const getSampleEvents = (): TimelineEvent[] => [
    {
      id: '1',
      title: 'First OSINT Investigation',
      start: '2023-01-15T10:00:00Z',
      end: '2023-01-15T12:00:00Z',
      description: 'Initial data collection from social media platforms.',
      category: 'Investigation',
      icon: '🔍',
      color: '#3B82F6',
    },
    {
      id: '2',
      title: 'Metadata Extraction',
      start: '2023-01-16T14:30:00Z',
      end: '2023-01-16T16:00:00Z',
      description: 'Extracted EXIF data from 50 images.',
      category: 'Processing',
      icon: '📷',
      color: '#10B981',
    },
    {
      id: '3',
      title: 'NLP Analysis',
      start: '2023-01-17T09:00:00Z',
      end: '2023-01-17T11:00:00Z',
      description: 'Analyzed text data for entities and keywords.',
      category: 'Analysis',
      icon: '🧠',
      color: '#8B5CF6',
    },
    {
      id: '4',
      title: 'Graph Visualization',
      start: '2023-01-18T13:00:00Z',
      end: '2023-01-18T15:00:00Z',
      description: 'Created network graph of relationships.',
      category: 'Visualization',
      icon: '📊',
      color: '#F59E0B',
    },
    {
      id: '5',
      title: 'Report Generation',
      start: '2023-01-19T10:00:00Z',
      end: '2023-01-19T12:00:00Z',
      description: 'Generated comprehensive OSINT report.',
      category: 'Reporting',
      icon: '📄',
      color: '#EF4444',
    },
  ];

  const generateTimeline = async () => {
    setLoading(true);
    setError(null);

    try {
      // For demo purposes, we'll use sample data
      // In a real scenario, you would send posts to the backend
      const samplePosts = [
        { id: '1', content: 'First OSINT Investigation', timestamp: '2023-01-15T10:00:00Z', category: 'Investigation' },
        { id: '2', content: 'Metadata Extraction', timestamp: '2023-01-16T14:30:00Z', category: 'Processing' },
        { id: '3', content: 'NLP Analysis', timestamp: '2023-01-17T09:00:00Z', category: 'Analysis' },
        { id: '4', content: 'Graph Visualization', timestamp: '2023-01-18T13:00:00Z', category: 'Visualization' },
        { id: '5', content: 'Report Generation', timestamp: '2023-01-19T10:00:00Z', category: 'Reporting' },
      ];

      const response = await axios.post('http://localhost:5000/visualize/timeline', {
        posts: samplePosts,
      });

      if (response.data.success) {
        setEvents(response.data.events);
      } else {
        setError(response.data.error || 'Failed to generate timeline.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sampleData) {
      setEvents(getSampleEvents());
    }
  }, [sampleData]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getCategoryColor = (category?: string): string => {
    const colors: Record<string, string> = {
      Investigation: 'bg-blue-100 text-blue-800',
      Processing: 'bg-green-100 text-green-800',
      Analysis: 'bg-purple-100 text-purple-800',
      Visualization: 'bg-yellow-100 text-yellow-800',
      Reporting: 'bg-red-100 text-red-800',
    };
    return category ? colors[category] || 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Timeline Visualization</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Generate Timeline</h2>
          <p className="text-gray-600 mb-4">
            Generate a timeline from your data. For demonstration, you can use sample data or connect to the backend API.
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => setSampleData(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Load Sample Data
            </button>
            <button
              onClick={generateTimeline}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 transition-colors"
            >
              {loading ? 'Generating...' : 'Generate from API'}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Timeline</h2>
          
          {events.length > 0 ? (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-300" />
              
              {/* Events */}
              <div className="space-y-8">
                {events.map((event, index) => (
                  <div key={event.id} className="relative flex items-start gap-6">
                    {/* Timeline dot */}
                    <div className="absolute left-7 w-4 h-4 bg-blue-600 rounded-full border-4 border-white shadow-md" />
                    
                    {/* Event content */}
                    <div className="flex-1 bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="flex items-center gap-2 mb-2">
                        {event.icon && <span className="text-2xl">{event.icon}</span>}
                        <h3 className="text-lg font-semibold text-gray-800">{event.title}</h3>
                        {event.category && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(event.category)}`}>
                            {event.category}
                          </span>
                        )}
                      </div>
                      
                      <div className="text-sm text-gray-500 mb-2">
                        {formatDate(event.start)}
                        {event.end && ` - ${formatDate(event.end)}`}
                      </div>
                      
                      {event.description && (
                        <p className="text-gray-600">{event.description}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">No timeline data available.</p>
              <p className="text-gray-500">Click "Load Sample Data" or "Generate from API" to see a timeline.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TimelineVisualization;
