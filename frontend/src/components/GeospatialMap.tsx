import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Define types for map data
interface Location {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  description?: string;
  timestamp?: string;
}

const GeospatialMap: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [center, setCenter] = useState<[number, number]>([51.505, -0.09]); // Default: London
  const [zoom, setZoom] = useState<number>(3);

  // Sample data for demonstration
  const sampleLocations: Location[] = [
    {
      id: '1',
      name: 'San Francisco',
      latitude: 37.7749,
      longitude: -122.4194,
      description: 'Sample post from San Francisco',
      timestamp: '2023-10-15 12:34:56',
    },
    {
      id: '2',
      name: 'New York',
      latitude: 40.7128,
      longitude: -74.0060,
      description: 'Sample post from New York',
      timestamp: '2023-10-16 08:23:45',
    },
    {
      id: '3',
      name: 'London',
      latitude: 51.5074,
      longitude: -0.1278,
      description: 'Sample post from London',
      timestamp: '2023-10-17 14:12:33',
    },
    {
      id: '4',
      name: 'Tokyo',
      latitude: 35.6762,
      longitude: 139.6503,
      description: 'Sample post from Tokyo',
      timestamp: '2023-10-18 20:45:12',
    },
    {
      id: '5',
      name: 'Moscow',
      latitude: 55.7558,
      longitude: 37.6173,
      description: 'Sample post from Moscow',
      timestamp: '2023-10-19 10:30:00',
    },
  ];

  // Load sample data
  useEffect(() => {
    setLocations(sampleLocations);
    // Center on the first location if available
    if (sampleLocations.length > 0) {
      setCenter([sampleLocations[0].latitude, sampleLocations[0].longitude]);
      setZoom(5);
    }
  }, []);

  // Function to add a new location
  const addLocation = (location: Location) => {
    setLocations([...locations, location]);
  };

  // Function to clear all locations
  const clearLocations = () => {
    setLocations([]);
    setCenter([51.505, -0.09]);
    setZoom(3);
  };

  // Function to center on a specific location
  const centerOnLocation = (lat: number, lng: number) => {
    setCenter([lat, lng]);
    setZoom(12);
  };

  // Custom component to handle map bounds
  const MapUpdater: React.FC<{ locations: Location[] }> = ({ locations }) => {
    const map = useMap();

    useEffect(() => {
      if (locations.length > 0) {
        // Fit the map to the bounds of all locations
        const bounds = L.latLngBounds(
          locations.map((loc) => [loc.latitude, loc.longitude] as [number, number])
        );
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }, [locations, map]);

    return null;
  };

  return (
    <div className="geospatial-map">
      <h2>🗺️ Geospatial Map</h2>
      <p>
        Plot and visualize locations from posts, images, or other data sources.
        Click on markers to view details.
      </p>

      <div className="map-controls">
        <button onClick={() => setLocations(sampleLocations)}>Load Sample Data</button>
        <button onClick={clearLocations}>Clear Map</button>
        <button onClick={() => centerOnLocation(37.7749, -122.4194)}>
          Center on SF
        </button>
      </div>

      <div className="map-container" style={{ height: '600px', width: '100%' }}>
        <MapContainer
          center={center}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {/* Update map bounds when locations change */}
          <MapUpdater locations={locations} />

          {/* Render markers for each location */}
          {locations.map((location) => (
            <Marker
              key={location.id}
              position={[location.latitude, location.longitude]}
              icon={defaultIcon}
            >
              <Popup>
                <div className="location-popup">
                  <h4>{location.name}</h4>
                  {location.description && <p>{location.description}</p>}
                  <p>
                    Latitude: {location.latitude.toFixed(4)}, 
                    Longitude: {location.longitude.toFixed(4)}
                  </p>
                  {location.timestamp && <p>Timestamp: {location.timestamp}</p>}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      <div className="map-info">
        <p>
          <strong>Locations:</strong> {locations.length}
        </p>
      </div>

      <div className="map-instructions">
        <h4>📌 How to Use:</h4>
        <ul>
          <li>Click "Load Sample Data" to add test locations.</li>
          <li>Click on markers to view details.</li>
          <li>Use the mouse to zoom in/out and pan around the map.</li>
          <li>Click "Clear Map" to remove all locations.</li>
        </ul>
      </div>
    </div>
  );
};

export default GeospatialMap;
