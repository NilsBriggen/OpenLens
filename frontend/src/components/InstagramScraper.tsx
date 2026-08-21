import React, { useState } from 'react';
import axios from 'axios';

interface InstagramPost {
  id: string;
  shortcode: string;
  caption: string;
  timestamp: string | null;
  likes: number;
  comments: number;
  views: number;
  url: string;
  media_url: string;
  media_type: string;
  hashtags: string[];
  mentions: string[];
  location: string | null;
  geotag: { latitude: number; longitude: number } | null;
}

interface InstagramUser {
  id: string;
  username: string;
  full_name: string;
  bio: string;
  url: string;
  followers: number;
  following: number;
  posts: number;
  is_verified: boolean;
  is_private: boolean;
  profile_pic_url: string;
  website: string;
  business_category: string;
}

const InstagramScraper: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'user' | 'posts' | 'hashtag'>('user');
  const [username, setUsername] = useState<string>('');
  const [hashtag, setHashtag] = useState<string>('');
  const [limit, setLimit] = useState<number>(10);
  const [user, setUser] = useState<InstagramUser | null>(null);
  const [posts, setPosts] = useState<InstagramPost[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleScrapeUser = async () => {
    if (!username.trim()) {
      setError('Please enter a username.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/instagram/user', {
        params: { username },
      });

      if (response.data.success) {
        setUser(response.data.user);
      } else {
        setError(response.data.error || 'Failed to scrape user profile.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeUserPosts = async () => {
    if (!username.trim()) {
      setError('Please enter a username.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/instagram/posts', {
        params: { username, limit },
      });

      if (response.data.success) {
        setPosts(response.data.posts);
      } else {
        setError(response.data.error || 'Failed to scrape posts.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeHashtag = async () => {
    if (!hashtag.trim()) {
      setError('Please enter a hashtag.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/instagram/hashtag', {
        params: { hashtag, limit },
      });

      if (response.data.success) {
        setPosts(response.data.posts);
      } else {
        setError(response.data.error || 'Failed to scrape hashtag posts.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp: string | null): string => {
    if (!timestamp) return 'Unknown';
    return new Date(timestamp).toLocaleString();
  };

  const formatNumber = (num: number | null): string => {
    if (num === null) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Instagram Scraper</h1>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            onClick={() => setActiveTab('user')}
            className={`px-4 py-2 font-medium ${activeTab === 'user' ? 'text-purple-600 border-b-2 border-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            User Profile
          </button>
          <button
            onClick={() => setActiveTab('posts')}
            className={`px-4 py-2 font-medium ${activeTab === 'posts' ? 'text-purple-600 border-b-2 border-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            User Posts
          </button>
          <button
            onClick={() => setActiveTab('hashtag')}
            className={`px-4 py-2 font-medium ${activeTab === 'hashtag' ? 'text-purple-600 border-b-2 border-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Hashtag Posts
          </button>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {activeTab === 'user' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">User Profile</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter Instagram username"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeUser}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-purple-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Get User Profile'}
              </button>
            </div>
          )}

          {activeTab === 'posts' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">User Posts</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter Instagram username"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                    max="50"
                    placeholder="Limit"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeUserPosts}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-purple-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Get User Posts'}
              </button>
            </div>
          )}

          {activeTab === 'hashtag' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Hashtag Posts</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    value={hashtag}
                    onChange={(e) => setHashtag(e.target.value)}
                    placeholder="Enter hashtag (without #)"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                    max="50"
                    placeholder="Limit"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeHashtag}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-purple-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Get Hashtag Posts'}
              </button>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Results Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {activeTab === 'user' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">User Profile</h2>
              {user ? (
                <div className="max-w-2xl">
                  <div className="flex items-center gap-6 mb-6">
                    <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-800">
                        {user.full_name}
                        <span className="ml-2 text-purple-600">@{user.username}</span>
                        {user.is_verified && <span className="ml-2 text-blue-500">✓</span>}
                      </h3>
                      <p className="text-gray-600 mt-1">{user.bio || 'No bio available'}</p>
                      <div className="flex gap-4 mt-3 text-sm text-gray-500">
                        {user.website && <span>🔗 {user.website}</span>}
                        {user.business_category && <span>🏢 {user.business_category}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.posts)}</div>
                      <div className="text-sm text-gray-500">Posts</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.followers)}</div>
                      <div className="text-sm text-gray-500">Followers</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.following)}</div>
                      <div className="text-sm text-gray-500">Following</div>
                    </div>
                  </div>
                  {user.url && (
                    <div className="mt-4">
                      <a
                        href={user.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-600 hover:text-purple-800 text-sm"
                      >
                        {user.url}
                      </a>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">No user profile found. Try a different username.</p>
              )}
            </div>
          )}

          {(activeTab === 'posts' || activeTab === 'hashtag') && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">
                {activeTab === 'posts' ? 'User Posts' : 'Hashtag Posts'}
              </h2>
              {posts.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {posts.map((post) => (
                    <div key={post.id} className="border border-gray-200 rounded-lg overflow-hidden">
                      {post.media_url && (
                        <img
                          src={post.media_url}
                          alt="Post"
                          className="w-full h-48 object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x300?text=Image+Not+Available';
                          }}
                        />
                      )}
                      <div className="p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-semibold text-gray-800">@{post.shortcode}</span>
                          <span className="text-gray-500 text-sm">{formatDate(post.timestamp)}</span>
                        </div>
                        {post.caption && (
                          <p className="text-gray-700 mb-3">{post.caption}</p>
                        )}
                        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                          <span>❤️ {formatNumber(post.likes)}</span>
                          <span>💬 {formatNumber(post.comments)}</span>
                          <span>👁️ {formatNumber(post.views)}</span>
                        </div>
                        {post.hashtags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-2">
                            {post.hashtags.map((hashtag, index) => (
                              <span key={index} className="text-purple-600 text-sm">#{hashtag}</span>
                            ))}
                          </div>
                        )}
                        {post.geotag && (
                          <div className="text-sm text-gray-500">
                            📍 {post.geotag.latitude.toFixed(4)}, {post.geotag.longitude.toFixed(4)}
                          </div>
                        )}
                        {post.location && (
                          <div className="text-sm text-gray-500">{post.location}</div>
                        )}
                        <div className="mt-2">
                          <a
                            href={post.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-purple-600 hover:text-purple-800 text-sm"
                          >
                            View on Instagram
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">
                  No posts found. Try a different {activeTab === 'posts' ? 'username' : 'hashtag'}.
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstagramScraper;
