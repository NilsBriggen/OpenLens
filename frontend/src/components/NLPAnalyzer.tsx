import React, { useState } from 'react';
import axios from 'axios';

interface Entity {
  text: string;
  label: string;
  start: number;
  end: number;
}

interface NLPAnalysis {
  entities: Entity[];
  people: string[];
  organizations: string[];
  locations: string[];
  dates: string[];
  keywords: string[];
}

const NLPAnalyzer: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [analysis, setAnalysis] = useState<NLPAnalysis | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/nlp/analyze', {
        text: text,
      });

      if (response.data.success) {
        setAnalysis(response.data.analysis);
      } else {
        setError(response.data.error || 'Failed to analyze text.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExtractEntities = async () => {
    if (!text.trim()) {
      setError('Please enter some text to extract entities.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/nlp/entities', {
        text: text,
      });

      if (response.data.success) {
        setAnalysis({
          entities: response.data.entities,
          people: response.data.people,
          organizations: response.data.organizations,
          locations: response.data.locations,
          dates: response.data.dates,
          keywords: response.data.keywords,
        });
      } else {
        setError(response.data.error || 'Failed to extract entities.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getLabelColor = (label: string): string => {
    const colors: Record<string, string> = {
      PERSON: 'bg-blue-100 text-blue-800',
      ORG: 'bg-green-100 text-green-800',
      GPE: 'bg-purple-100 text-purple-800',  // Geo-Political Entity (locations)
      DATE: 'bg-yellow-100 text-yellow-800',
      KEYWORD: 'bg-gray-100 text-gray-800',
    };
    return colors[label] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">NLP Text Analyzer</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Input Text</h2>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter text to analyze (e.g., 'Mistral AI is based in Paris and was founded in 2023.')"
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent h-32"
          />
          <div className="flex gap-4 mt-4">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
            >
              {loading ? 'Analyzing...' : 'Full Analysis'}
            </button>
            <button
              onClick={handleExtractEntities}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 transition-colors"
            >
              {loading ? 'Extracting...' : 'Extract Entities'}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {analysis && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">Analysis Results</h2>

            {/* Entities */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-600 mb-3">Detected Entities</h3>
              {analysis.entities.length > 0 ? (
                <div className="space-y-2">
                  {analysis.entities.map((entity, index) => (
                    <div
                      key={index}
                      className={`inline-block px-3 py-1 rounded-full text-sm mr-2 mb-2 ${getLabelColor(entity.label)}`}
                    >
                      <span className="font-medium">{entity.text}</span>
                      <span className="ml-2 text-xs opacity-70">{entity.label}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No entities detected.</p>
              )}
            </div>

            {/* Categories */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-600 mb-3">People</h3>
                {analysis.people.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.people.map((person, index) => (
                      <li key={index} className="text-gray-700">{person}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No people detected.</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-600 mb-3">Organizations</h3>
                {analysis.organizations.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.organizations.map((org, index) => (
                      <li key={index} className="text-gray-700">{org}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No organizations detected.</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-600 mb-3">Locations</h3>
                {analysis.locations.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.locations.map((location, index) => (
                      <li key={index} className="text-gray-700">{location}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No locations detected.</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-600 mb-3">Dates</h3>
                {analysis.dates.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.dates.map((date, index) => (
                      <li key={index} className="text-gray-700">{date}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500">No dates detected.</p>
                )}
              </div>

              <div className="md:col-span-2">
                <h3 className="text-lg font-medium text-gray-600 mb-3">Keywords</h3>
                {analysis.keywords.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {analysis.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No keywords detected.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NLPAnalyzer;
