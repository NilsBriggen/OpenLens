import React, { useState } from 'react';
import axios from 'axios';

interface VKUser {
  id: string;
  first_name: string;
  last_name: string;
  username: string;
  bio: string;
  city: string | null;
  country: string | null;
  birthday: string | null;
  followers: number;
}

interface VKPost {
  id: string;
  author_name: string;
  content: string;
  timestamp: string;
  likes: number;
  reposts: number;
  views: number;
  comments: number;
  attachments: any[];
}

const VKScraper: React.FC = () => {
  const [username, setUsername] = useState<string>('');
  const [limit, setLimit] = useState<number>(5);
  const [userResult, setUserResult] = useState<VKUser | null>(null);
  const [postsResult, setPostsResult] = useState<VKPost[] | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'posts' | 'search'>('profile');

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value);
  };

  const handleLimitChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLimit(parseInt(e.target.value) || 5);
  };

  const handleSearchQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const fetchUserProfile = async () => {
    if (!username.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/scrape/vk/user?username=${username}`);
      if (response.data.success) {
        setUserResult(response.data.user);
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUserPosts = async () => {
    if (!username.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:5000/scrape/vk/posts?username=${username}&limit=${limit}`
      );
      if (response.data.success) {
        setPostsResult(response.data.posts);
      }
    } catch (error) {
      console.error('Failed to fetch user posts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSearchResults = async () => {
    if (!searchQuery.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:5000/scrape/vk/search?query=${encodeURIComponent(searchQuery)}&limit=10`
      );
      if (response.data.success) {
        setSearchResults(response.data.users);
      }
    } catch (error) {
      console.error('Failed to search users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'profile') {
      fetchUserProfile();
    } else if (activeTab === 'posts') {
      fetchUserPosts();
    } else if (activeTab === 'search') {
      fetchSearchResults();
    }
  };

  return (
    <div className="vk-scraper">
      <h2>🌐 VK Scraper</h2>
      <p>
        Scrape public VK (VKontakte) profiles, posts, and search for users.
      </p>

      <div className="tabs">
        <button
          className={activeTab === 'profile' ? 'active' : ''}
          onClick={() => setActiveTab('profile')}
        >
          User Profile
        </button>
        <button
          className={activeTab === 'posts' ? 'active' : ''}
          onClick={() => setActiveTab('posts')}
        >
          User Posts
        </button>
        <button
          className={activeTab === 'search' ? 'active' : ''}
          onClick={() => setActiveTab('search')}
        >
          Search Users
        </button>
      </div>

      <form onSubmit={handleSubmit} className="scraper-form">
        {activeTab === 'profile' && (
          <>
            <input
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Enter VK username (e.g., durov)"
              required
            />
            <button type="submit" disabled={!username.trim() || isLoading}>
              {isLoading ? 'Scraping...' : 'Scrape Profile'}
            </button>
          </>
        )}

        {activeTab === 'posts' && (
          <>
            <input
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="Enter VK username"
              required
            />
            <input
              type="number"
              value={limit}
              onChange={handleLimitChange}
              min="1"
              max="50"
              placeholder="Limit"
            />
            <button type="submit" disabled={!username.trim() || isLoading}>
              {isLoading ? 'Scraping...' : 'Scrape Posts'}
            </button>
          </>
        )}

        {activeTab === 'search' && (
          <>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchQueryChange}
              placeholder="Enter search query"
              required
            />
            <button type="submit" disabled={!searchQuery.trim() || isLoading}>
              {isLoading ? 'Searching...' : 'Search'}
            </button>
          </>
        )}
      </form>

      <div className="results">
        {activeTab === 'profile' && userResult && (
          <div className="user-profile">
            <h3>👤 User Profile</h3>
            <div className="profile-card">
              <h4>
                {userResult.first_name} {userResult.last_name}
              </h4>
              {userResult.username && <p>Username: @{userResult.username}</p>}
              {userResult.bio && <p>Bio: {userResult.bio}</p>}
              {userResult.city && <p>City: {userResult.city}</p>}
              {userResult.country && <p>Country: {userResult.country}</p>}
              {userResult.birthday && <p>Birthday: {userResult.birthday}</p>}
              <p>Followers: {userResult.followers}</p>
            </div>
          </div>
        )}

        {activeTab === 'posts' && postsResult && postsResult.length > 0 && (
          <div className="user-posts">
            <h3>📝 User Posts</h3>
            <div className="posts-list">
              {postsResult.map((post: VKPost, index: number) => (
                <div key={index} className="post-card">
                  <h4>Post by {post.author_name}</h4>
                  <p>{post.content}</p>
                  <div className="post-metrics">
                    <span>❤️ {post.likes}</span>
                    <span>🔄 {post.reposts}</span>
                    <span>👁️ {post.views}</span>
                    <span>💬 {post.comments}</span>
                  </div>
                  {post.timestamp && <p className="timestamp">Posted on: {post.timestamp}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'search' && searchResults && searchResults.length > 0 && (
          <div className="search-results">
            <h3>🔍 Search Results</h3>
            <div className="users-list">
              {searchResults.map((user: any, index: number) => (
                <div key={index} className="user-card">
                  <h4>{user.name}</h4>
                  {user.username && <p>Username: @{user.username}</p>}
                  <p>
                    <a href={user.url} target="_blank" rel="noopener noreferrer">
                      View Profile
                    </a>
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'search' && searchQuery && !searchResults && !isLoading && (
          <p>No results found for "{searchQuery}"</p>
        )}
      </div>
    </div>
  );
};

export default VKScraper;
