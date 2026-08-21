import React, { useState } from 'react';
import axios from 'axios';

interface TextResult {
  success: boolean;
  text?: string;
  metadata?: any;
  error?: string;
}

const TextExtractor: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [result, setResult] = useState<TextResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/extract/text', {
        text: text,
      });
      setResult(response.data);
    } catch (error) {
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract text metadata',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderMetadata = (metadata: any) => {
    if (!metadata) return null;

    return (
      <div className="text-metadata-result">
        <h4>Extracted Metadata:</h4>
        
        {metadata.hashtags && metadata.hashtags.length > 0 && (
          <div className="hashtags">
            <h5>🏷️ Hashtags:</h5>
            <div className="tag-list">
              {metadata.hashtags.map((tag: string, index: number) => (
                <span key={index} className="tag">#{tag}</span>
              ))}
            </div>
          </div>
        )}
        
        {metadata.geotags && metadata.geotags.length > 0 && (
          <div className="geotags">
            <h5>📍 Geotags:</h5>
            <ul>
              {metadata.geotags.map((geotag: any, index: number) => (
                <li key={index}>
                  Latitude: {geotag.latitude}, Longitude: {geotag.longitude}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {metadata.mentions && metadata.mentions.length > 0 && (
          <div className="mentions">
            <h5>👥 Mentions:</h5>
            <div className="mention-list">
              {metadata.mentions.map((mention: string, index: number) => (
                <span key={index} className="mention">@{mention}</span>
              ))}
            </div>
          </div>
        )}
        
        {metadata.urls && metadata.urls.length > 0 && (
          <div className="urls">
            <h5>🔗 URLs:</h5>
            <ul>
              {metadata.urls.map((url: string, index: number) => (
                <li key={index}>
                  <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="text-extractor">
      <h2>📝 Text Extractor</h2>
      <p>
        Enter text to extract geotags, hashtags, mentions, and URLs.
      </p>
      
      <form onSubmit={handleSubmit} className="text-form">
        <textarea
          value={text}
          onChange={handleTextChange}
          placeholder="Enter text here..."
          rows={6}
          required
        />
        <button type="submit" disabled={!text.trim() || isLoading}>
          {isLoading ? 'Extracting...' : 'Extract Metadata'}
        </button>
      </form>

      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.success ? (
            <>
              <h3>✅ Success!</h3>
              {result.text && <p>Text: {result.text}</p>}
              {renderMetadata(result.metadata)}
            </>
          ) : (
            <>
              <h3>❌ Error</h3>
              <p>{result.error}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default TextExtractor;
