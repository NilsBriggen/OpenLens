import React, { useState } from 'react';
import axios from 'axios';

interface Tweet {
  id: string;
  content: string;
  username: string;
  user_id: string;
  display_name: string;
  timestamp: string | null;
  likes: number;
  retweets: number;
  replies: number;
  quotes: number;
  views: number;
  hashtags: string[];
  mentions: string[];
  urls: string[];
  media: string[];
  geotag: { latitude: number; longitude: number } | null;
}

interface TwitterUser {
  id: string;
  username: string;
  display_name: string;
  bio: string;
  location: string;
  url: string;
  join_date: string | null;
  followers: number;
  following: number;
  tweets: number;
  likes: number;
  verified: boolean;
  profile_image: string;
  banner_image: string;
}

interface Trend {
  name: string;
  url: string;
  tweet_volume: number | null;
}

const TwitterScraper: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'tweets' | 'user' | 'trends'>('tweets');
  const [query, setQuery] = useState<string>('');
  const [username, setUsername] = useState<string>('');
  const [limit, setLimit] = useState<number>(10);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [user, setUser] = useState<TwitterUser | null>(null);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleScrapeTweets = async () => {
    if (!query.trim()) {
      setError('Please enter a search query.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/twitter/tweets', {
        params: { query, limit },
      });

      if (response.data.success) {
        setTweets(response.data.tweets);
      } else {
        setError(response.data.error || 'Failed to scrape tweets.');
      }
    } catch (err) {
      setError('Failed to connect to the API. Make sure the backend is running.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeUser = async () => {
    if (!username.trim()) {
      setError('Please enter a username.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/twitter/user', {
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

  const handleScrapeTrends = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get('http://localhost:5000/scrape/twitter/trends', {
        params: { limit },
      });

      if (response.data.success) {
        setTrends(response.data.trends);
      } else {
        setError(response.data.error || 'Failed to scrape trends.');
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
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Twitter Scraper</h1>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            onClick={() => setActiveTab('tweets')}
            className={`px-4 py-2 font-medium ${activeTab === 'tweets' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Tweets
          </button>
          <button
            onClick={() => setActiveTab('user')}
            className={`px-4 py-2 font-medium ${activeTab === 'user' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            User Profile
          </button>
          <button
            onClick={() => setActiveTab('trends')}
            className={`px-4 py-2 font-medium ${activeTab === 'trends' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Trends
          </button>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {activeTab === 'tweets' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Search Tweets</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter search query (e.g., 'OSINT', 'from:username')"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                    max="100"
                    placeholder="Limit"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeTweets}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Search Tweets'}
              </button>
            </div>
          )}

          {activeTab === 'user' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">User Profile</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter Twitter username (without @)"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeUser}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Get User Profile'}
              </button>
            </div>
          )}

          {activeTab === 'trends' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Trends</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <input
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 1))}
                    min="1"
                    max="50"
                    placeholder="Limit"
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <button
                onClick={handleScrapeTrends}
                disabled={loading}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
              >
                {loading ? 'Scraping...' : 'Get Trends'}
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
          {activeTab === 'tweets' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Tweets</h2>
              {tweets.length > 0 ? (
                <div className="space-y-4">
                  {tweets.map((tweet) => (
                    <div key={tweet.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                          {tweet.display_name.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-gray-800">@{tweet.username}</span>
                            <span className="text-gray-500 text-sm">{formatDate(tweet.timestamp)}</span>
                          </div>
                          <p className="text-gray-700 mb-2">{tweet.content}</p>
                          <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span>❤️ {formatNumber(tweet.likes)}</span>
                            <span>🔄 {formatNumber(tweet.retweets)}</span>
                            <span>💬 {formatNumber(tweet.replies)}</span>
                            <span>👁️ {formatNumber(tweet.views)}</span>
                          </div>
                          {tweet.hashtags.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-2">
                              {tweet.hashtags.map((hashtag, index) => (
                                <span key={index} className="text-blue-600 text-sm">#{hashtag}</span>
                              ))}
                            </div>
                          )}
                          {tweet.geotag && (
                            <div className="mt-2 text-sm text-gray-500">
                              📍 {tweet.geotag.latitude.toFixed(4)}, {tweet.geotag.longitude.toFixed(4)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No tweets found. Try a different query.</p>
              )}
            </div>
          )}

          {activeTab === 'user' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">User Profile</h2>
              {user ? (
                <div className="max-w-2xl">
                  <div className="flex items-center gap-6 mb-6">
                    <div className="w-24 h-24 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                      {user.display_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-800">
                        {user.display_name}
                        <span className="ml-2 text-blue-600">@{user.username}</span>
                        {user.verified && <span className="ml-2 text-blue-500">✓</span>}
                      </h3>
                      <p className="text-gray-600 mt-1">{user.bio}</p>
                      <div className="flex gap-4 mt-3 text-sm text-gray-500">
                        <span>📍 {user.location || 'Unknown'}</span>
                        <span>🔗 {user.url || 'No URL'}</span>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.followers)}</div>
                      <div className="text-sm text-gray-500">Followers</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.following)}</div>
                      <div className="text-sm text-gray-500">Following</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.tweets)}</div>
                      <div className="text-sm text-gray-500">Tweets</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-2xl font-bold text-gray-800">{formatNumber(user.likes)}</div>
                      <div className="text-sm text-gray-500">Likes</div>
                    </div>
                  </div>
                  {user.join_date && (
                    <div className="mt-4 text-sm text-gray-500">
                      Joined: {formatDate(user.join_date)}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500">No user profile found. Try a different username.</p>
              )}
            </div>
          )}

          {activeTab === 'trends' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Trending Topics</h2>
              {trends.length > 0 ? (
                <div className="space-y-3">
                  {trends.map((trend, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <span className="text-lg font-medium text-gray-800">{index + 1}. {trend.name}</span>
                        {trend.tweet_volume && (
                          <span className="ml-2 text-sm text-gray-500">
                            ({formatNumber(trend.tweet_volume)} tweets)
                          </span>
                        )}
                      </div>
                      {trend.url && (
                        <a
                          href={trend.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm"
                        >
                          View
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No trends found.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TwitterScraper;
