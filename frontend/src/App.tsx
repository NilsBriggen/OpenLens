import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Import components
import MetadataExtractor from './components/MetadataExtractor';
import TextExtractor from './components/TextExtractor';
import VKScraper from './components/VKScraper';
import TwitterScraper from './components/TwitterScraper';
import InstagramScraper from './components/InstagramScraper';
import NLPAnalyzer from './components/NLPAnalyzer';
import GraphVisualization from './components/GraphVisualization';
import GeospatialMap from './components/GeospatialMap';
import TimelineVisualization from './components/TimelineVisualization';
import HeatmapVisualization from './components/HeatmapVisualization';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <Link to="/" className="flex-shrink-0 flex items-center">
                  <span className="text-2xl font-bold text-blue-600">OpenLens</span>
                </Link>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link
                    to="/"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Home
                  </Link>
                  <Link
                    to="/metadata"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Metadata
                  </Link>
                  <Link
                    to="/text"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Text
                  </Link>
                  <Link
                    to="/nlp"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    NLP
                  </Link>
                  <Link
                    to="/vk"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    VK
                  </Link>
                  <Link
                    to="/twitter"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Twitter
                  </Link>
                  <Link
                    to="/instagram"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Instagram
                  </Link>
                  <Link
                    to="/graph"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Graph
                  </Link>
                  <Link
                    to="/map"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Map
                  </Link>
                  <Link
                    to="/timeline"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Timeline
                  </Link>
                  <Link
                    to="/heatmap"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Heatmap
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route
              path="/"
              element={
                <div className="p-6 bg-white rounded-lg shadow-md">
                  <h1 className="text-3xl font-bold text-gray-800 mb-4">Welcome to OpenLens</h1>
                  <p className="text-gray-600 mb-6">
                    OpenLens is a modular, open-source OSINT (Open-Source Intelligence) framework for gathering, 
                    analyzing, and visualizing publicly available data.
                  </p>
                  <h2 className="text-xl font-semibold text-gray-700 mb-4">Features</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">Metadata Extraction</h3>
                      <p className="text-gray-600 text-sm">
                        Extract EXIF data (GPS, timestamps, device info) from images and parse text metadata.
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">Social Media Scraping</h3>
                      <p className="text-gray-600 text-sm">
                        Scrape data from VK, Twitter, Telegram, and Instagram.
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">NLP Analysis</h3>
                      <p className="text-gray-600 text-sm">
                        Extract entities (people, organizations, locations) and analyze text with spaCy.
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">Visualizations</h3>
                      <p className="text-gray-600 text-sm">
                        Generate timelines, heatmaps, and network graphs from your data.
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">Async Processing</h3>
                      <p className="text-gray-600 text-sm">
                        Use Celery for background task processing and queue management.
                      </p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h3 className="font-bold text-gray-800 mb-2">Database Support</h3>
                      <p className="text-gray-600 text-sm">
                        Store data in PostgreSQL (relational) and Neo4j (graph) databases.
                      </p>
                    </div>
                  </div>
                  <h2 className="text-xl font-semibold text-gray-700 mt-8 mb-4">Quick Start</h2>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-600 mb-2">
                      1. Use the navigation above to access different features.
                    </p>
                    <p className="text-gray-600 mb-2">
                      2. For metadata extraction, go to <Link to="/metadata" className="text-blue-600 hover:underline">Metadata</Link>.
                    </p>
                    <p className="text-gray-600 mb-2">
                      3. For social media scraping, use the VK, Twitter, or Instagram pages.
                    </p>
                    <p className="text-gray-600">
                      4. For NLP analysis, go to <Link to="/nlp" className="text-blue-600 hover:underline">NLP</Link>.
                    </p>
                  </div>
                </div>
              }
            />
            <Route path="/metadata" element={<MetadataExtractor />} />
            <Route path="/text" element={<TextExtractor />} />
            <Route path="/nlp" element={<NLPAnalyzer />} />
            <Route path="/vk" element={<VKScraper />} />
            <Route path="/twitter" element={<TwitterScraper />} />
            <Route path="/instagram" element={<InstagramScraper />} />
            <Route path="/graph" element={<GraphVisualization />} />
            <Route path="/map" element={<GeospatialMap />} />
            <Route path="/timeline" element={<TimelineVisualization />} />
            <Route path="/heatmap" element={<HeatmapVisualization />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-auto">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <p className="text-sm text-gray-500 text-center">
              OpenLens - Open-Source Intelligence Framework | Built with React, Flask, and Python
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
