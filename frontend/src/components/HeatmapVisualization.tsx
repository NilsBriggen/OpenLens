import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import 'leaflet.heat';

// Fix for default marker icons in React-Leaflet
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface HeatmapPoint {
  latitude: number;
  longitude: number;
  intensity: number;
  radius: number;
  color?: string;
}

interface Location {
  latitude: number;
  longitude: number;
  name: string;
  count: number;
}

const HeatmapVisualization: React.FC = () => {
  const [points, setPoints] = useState<HeatmapPoint[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'heatmap' | 'markers'>('heatmap');
  const [sampleData, setSampleData] = useState<boolean>(false);

  // Sample data for demonstration
  const getSamplePoints = (): HeatmapPoint[] => [
    { latitude: 55.7558, longitude: 37.6173, intensity: 0.8, radius: 25, color: '#FF0000' }, // Moscow
    { latitude: 48.8566, longitude: 2.3522, intensity: 0.9, radius: 25, color: '#FF0000' }, // Paris
    { latitude: 51.5074, longitude: -0.1278, intensity: 0.7, radius: 25, color: '#FF0000' }, // London
    { latitude: 40.7128, longitude: -74.0060, intensity: 1.0, radius: 25, color: '#FF0000' }, // New York
    { latitude: 35.6762, longitude: 139.6503, intensity: 0.6, radius: 25, color: '#FF0000' }, // Tokyo
    { latitude: 37.7749, longitude: -122.4194, intensity: 0.8, radius: 25, color: '#FF0000' }, // San Francisco
    { latitude: 52.5200, longitude: 13.4050, intensity: 0.7, radius: 25, color: '#FF0000' }, // Berlin
    { latitude: 39.9042, longitude: 116.4074, intensity: 0.9, radius: 25, color: '#FF0000' }, // Beijing
    { latitude: -33.8688, longitude: 151.2093, intensity: 0.5, radius: 25, color: '#FF0000' }, // Sydney
    { latitude: 19.4326, longitude: -99.1332, intensity: 0.6, radius: 25, color: '#FF0000' }, // Mexico City
  ];

  const getSampleLocations = (): Location[] => [
    { latitude: 55.7558, longitude: 37.6173, name: 'Moscow', count: 150 },
    { latitude: 48.8566, longitude: 2.3522, name: 'Paris', count: 200 },
    { latitude: 51.5074, longitude: -0.1278, name: 'London', count: 180 },
    { latitude: 40.7128, longitude: -74.0060, name: 'New York', count: 250 },
    { latitude: 35.6762, longitude: 139.6503, name: 'Tokyo', count: 120 },
  ];

  const generateHeatmap = async () => {
    setLoading(true);
    setError(null);

    try {
      // For demo purposes, we'll use sample data
      // In a real scenario, you would send posts to the backend
      const samplePosts = [
        { id: '1', geotag: { latitude: 55.7558, longitude: 37.6173 } },
        { id: '2', geotag: { latitude: 48.8566, longitude: 2.3522 } },
        { id: '3', geotag: { latitude: 51.5074, longitude: -0.1278 } },
        { id: '4', geotag: { latitude: 40.7128, longitude: -74.0060 } },
        { id: '5', geotag: { latitude: 35.6762, longitude: 139.6503 } },
      ];

      const response = await axios.post('http://localhost:5000/visualize/heatmap', {
        posts: samplePosts,
      });

      if (response.data.success) {
        setPoints(response.data.points);
      } else {
        setError(response.data.error || 'Failed to generate heatmap.');
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
      setPoints(getSamplePoints());
      setLocations(getSampleLocations());
    }
  }, [sampleData]);

  // Custom component to add heatmap layer
  const HeatmapLayer: React.FC<{ points: HeatmapPoint[] }> = ({ points }) => {
    const map = useMap();
    
    useEffect(() => {
      // Clear existing heatmap
      if (map.heat) {
        map.removeLayer(map.heat);
      }
      
      // Create new heatmap if we have points
      if (points.length > 0) {
        const heatmapPoints = points.map(point => [point.latitude, point.longitude, point.intensity]);
        map.heat = L.heatLayer(heatmapPoints as [number, number, number][], {
          radius: 25,
          blur: 15,
          maxZoom: 17,
          gradient: { 0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red' },
        }).addTo(map);
      }
    }, [points, map]);
    
    return null;
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Heatmap Visualization</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Generate Heatmap</h2>
          <p className="text-gray-600 mb-4">
            Generate a heatmap from geotagged data. For demonstration, you can use sample data or connect to the backend API.
          </p>
          <div className="flex gap-4">
            <button
              onClick={() => setSampleData(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Load Sample Data
            </button>
            <button
              onClick={generateHeatmap}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 transition-colors"
            >
              {loading ? 'Generating...' : 'Generate from API'}
            </button>
          </div>
          <div className="mt-4 flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={viewMode === 'heatmap'}
                onChange={() => setViewMode('heatmap')}
                className="text-blue-600"
              />
              <span>Heatmap View</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={viewMode === 'markers'}
                onChange={() => setViewMode('markers')}
                className="text-blue-600"
              />
              <span>Markers View</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Map</h2>
          
          <div className="h-[600px] w-full rounded-lg border border-gray-200">
            {points.length > 0 || locations.length > 0 ? (
              <MapContainer
                center={[51.505, -0.09]}
                zoom={2}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                
                {viewMode === 'heatmap' && points.length > 0 && (
                  <HeatmapLayer points={points} />
                )}
                
                {viewMode === 'markers' && locations.length > 0 && (
                  locations.map((location, index) => (
                    <Marker
                      key={index}
                      position={[location.latitude, location.longitude]}
                      icon={defaultIcon}
                    >
                      <Popup>
                        <div>
                          <h3 className="font-bold">{location.name}</h3>
                          <p>Count: {location.count}</p>
                          <p>Lat: {location.latitude.toFixed(4)}</p>
                          <p>Lon: {location.longitude.toFixed(4)}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))
                )}
                
                {viewMode === 'markers' && points.length > 0 && locations.length === 0 && (
                  points.map((point, index) => (
                    <Marker
                      key={index}
                      position={[point.latitude, point.longitude]}
                      icon={defaultIcon}
                    >
                      <Popup>
                        <div>
                          <p>Lat: {point.latitude.toFixed(4)}</p>
                          <p>Lon: {point.longitude.toFixed(4)}</p>
                          <p>Intensity: {point.intensity.toFixed(2)}</p>
                        </div>
                      </Popup>
                    </Marker>
                  ))
                )}
              </MapContainer>
            ) : (
              <div className="h-full w-full flex items-center justify-center bg-gray-100 rounded-lg">
                <p className="text-gray-500">No map data available. Load sample data or generate from API.</p>
              </div>
            )}
          </div>
          
          {locations.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Locations</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {locations.map((location, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-2">{location.name}</h4>
                    <p className="text-sm text-gray-600">
                      Latitude: {location.latitude.toFixed(4)}, Longitude: {location.longitude.toFixed(4)}
                    </p>
                    <p className="text-sm text-gray-600">Count: {location.count}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HeatmapVisualization;
