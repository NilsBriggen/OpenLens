import React, { useState } from 'react';
import axios from 'axios';

interface MetadataResult {
  success: boolean;
  filename?: string;
  metadata?: any;
  error?: string;
}

const MetadataExtractor: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<MetadataResult | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/extract/metadata', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (error) {
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract metadata',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderMetadata = (metadata: any) => {
    if (!metadata) return null;

    return (
      <div className="metadata-result">
        <h4>Extracted Metadata:</h4>
        <pre>{JSON.stringify(metadata, null, 2)}</pre>
        
        {/* Special formatting for GPS data */}
        {metadata.gps && (
          <div className="gps-data">
            <h5>📍 GPS Coordinates:</h5>
            <p>
              Latitude: {metadata.gps.latitude}, Longitude: {metadata.gps.longitude}
              {metadata.gps.altitude && `, Altitude: ${metadata.gps.altitude}m`}
            </p>
          </div>
        )}
        
        {/* Special formatting for timestamp */}
        {metadata.timestamp && (
          <div className="timestamp-data">
            <h5>📅 Timestamp:</h5>
            <p>{metadata.timestamp}</p>
          </div>
        )}
        
        {/* Special formatting for device info */}
        {(metadata.make || metadata.model || metadata.software) && (
          <div className="device-data">
            <h5>📱 Device Info:</h5>
            <p>
              {metadata.make && `Make: ${metadata.make}`}
              {metadata.model && `, Model: ${metadata.model}`}
              {metadata.software && `, Software: ${metadata.software}`}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="metadata-extractor">
      <h2>📷 Metadata Extractor</h2>
      <p>
        Upload an image to extract EXIF metadata (GPS coordinates, timestamps, device info, etc.).
      </p>
      
      <form onSubmit={handleSubmit} className="upload-form">
        <input type="file" onChange={handleFileChange} accept="image/*" required />
        <button type="submit" disabled={!file || isLoading}>
          {isLoading ? 'Extracting...' : 'Extract Metadata'}
        </button>
      </form>

      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.success ? (
            <>
              <h3>✅ Success!</h3>
              {result.filename && <p>Filename: {result.filename}</p>}
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

export default MetadataExtractor;
