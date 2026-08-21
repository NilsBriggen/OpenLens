/**
 * UI Utility Functions for OpenLens
 * 
 * A collection of utility functions for common UI tasks:
 * - Copy to clipboard
 * - Format dates and times
 * - Format numbers
 * - Generate IDs
 * - Validate inputs
 */

import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import duration from 'dayjs/plugin/duration';

dayjs.extend(relativeTime);
dayjs.extend(duration);

/**
 * Copy text to clipboard
 */
export const copyToClipboard = (text: string): Promise<boolean> => {
  return navigator.clipboard.writeText(text)
    .then(() => true)
    .catch((error) => {
      console.error('Failed to copy to clipboard:', error);
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textarea);
      return success;
    });
};

/**
 * Format date as relative time (e.g., "2 hours ago")
 */
export const timeAgo = (date: string | Date, fromDate?: string | Date): string => {
  return dayjs(date).from(fromDate || new Date());
};

/**
 * Format date as relative time with more detail
 */
export const timeAgoDetailed = (date: string | Date): string => {
  const now = dayjs();
  const target = dayjs(date);
  const diff = now.diff(target, 'second');

  if (diff < 60) {
    return `${diff} second${diff !== 1 ? 's' : ''} ago`;
  }

  const diffMinutes = now.diff(target, 'minute');
  if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
  }

  const diffHours = now.diff(target, 'hour');
  if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  }

  const diffDays = now.diff(target, 'day');
  if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  }

  const diffWeeks = now.diff(target, 'week');
  if (diffWeeks < 4) {
    return `${diffWeeks} week${diffWeeks !== 1 ? 's' : ''} ago`;
  }

  const diffMonths = now.diff(target, 'month');
  if (diffMonths < 12) {
    return `${diffMonths} month${diffMonths !== 1 ? 's' : ''} ago`;
  }

  const diffYears = now.diff(target, 'year');
  return `${diffYears} year${diffYears !== 1 ? 's' : ''} ago`;
};

/**
 * Format date in a human-readable format
 */
export const formatDate = (
  date: string | Date,
  format: string = 'MMM D, YYYY'
): string => {
  return dayjs(date).format(format);
};

/**
 * Format date with time
 */
export const formatDateTime = (
  date: string | Date,
  format: string = 'MMM D, YYYY h:mm A'
): string => {
  return dayjs(date).format(format);
};

/**
 * Format number with commas
 */
export const formatNumber = (
  num: number,
  decimals: number = 0,
  locale: string = 'en-US'
): string => {
  return num.toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Format bytes to human-readable format
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format duration in human-readable format
 */
export const formatDuration = (
  seconds: number,
  format: 'short' | 'long' = 'short'
): string => {
  const duration = dayjs.duration(seconds, 'seconds');

  if (format === 'short') {
    if (duration.asSeconds() < 60) {
      return `${Math.floor(duration.asSeconds())}s`;
    }
    if (duration.asMinutes() < 60) {
      return `${Math.floor(duration.asMinutes())}m`;
    }
    if (duration.asHours() < 24) {
      return `${Math.floor(duration.asHours())}h`;
    }
    return `${Math.floor(duration.asDays())}d`;
  }

  // Long format
  const parts: string[] = [];
  const days = Math.floor(duration.asDays());
  const hours = Math.floor(duration.asHours()) % 24;
  const minutes = Math.floor(duration.asMinutes()) % 60;
  const secs = Math.floor(duration.asSeconds()) % 60;

  if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
  if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
  if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
  if (secs > 0 && parts.length === 0) parts.push(`${secs} second${secs !== 1 ? 's' : ''}`);

  return parts.join(', ') || '0 seconds';
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (
  text: string,
  length: number,
  suffix: string = '...'
): string => {
  if (text.length <= length) return text;
  return text.substring(0, length) + suffix;
};

/**
 * Truncate text from the middle
 */
export const truncateMiddle = (
  text: string,
  length: number,
  suffix: string = '...'
): string => {
  if (text.length <= length) return text;
  const half = Math.floor((length - suffix.length) / 2);
  return text.substring(0, half) + suffix + text.substring(text.length - half);
};

/**
 * Capitalize first letter
 */
export const capitalize = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

/**
 * Capitalize each word
 */
export const capitalizeWords = (text: string): string => {
  return text.split(' ').map(capitalize).join(' ');
};

/**
 * Generate a random ID
 */
export const generateId = (prefix: string = 'id'): string => {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Generate a UUID v4
 */
export const generateUUID = (): string => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
};

/**
 * Debounce a function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle a function
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle = false;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Sleep for a specified duration
 */
export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Check if value is empty (null, undefined, empty string, empty array, empty object)
 */
export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

/**
 * Check if value is a valid email
 */
export const isValidEmail = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Check if value is a valid URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Check if value is a valid IP address
 */
export const isValidIP = (ip: string): boolean => {
  const ipv4Regex = /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
  const ipv6Regex = /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/;
  return ipv4Regex.test(ip) || ipv6Regex.test(ip);
};

/**
 * Check if value is a valid domain
 */
export const isValidDomain = (domain: string): boolean => {
  const regex = /^([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$/;
  return regex.test(domain);
};

/**
 * Get initials from name
 */
export const getInitials = (name: string, maxLength: number = 2): string => {
  return name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .slice(0, maxLength)
    .join('');
};

/**
 * Get contrast color for a background color
 */
export const getContrastColor = (hexColor: string): '#fff' | '#000' => {
  // Convert hex to RGB
  const r = parseInt(hexColor.substr(1, 2), 16);
  const g = parseInt(hexColor.substr(3, 2), 16);
  const b = parseInt(hexColor.substr(5, 2), 16);

  // Calculate luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

  // Return black for light colors, white for dark colors
  return luminance > 0.5 ? '#000' : '#fff';
};

/**
 * Lighten or darken a color
 */
export const adjustColor = (
  hexColor: string,
  amount: number
): string => {
  // Convert hex to RGB
  let r = parseInt(hexColor.substr(1, 2), 16);
  let g = parseInt(hexColor.substr(3, 2), 16);
  let b = parseInt(hexColor.substr(5, 2), 16);

  // Adjust each channel
  r = Math.min(255, Math.max(0, r + amount));
  g = Math.min(255, Math.max(0, g + amount));
  b = Math.min(255, Math.max(0, b + amount));

  // Convert back to hex
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

/**
 * Generate a random color
 */
export const randomColor = (): string => {
  return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
};

/**
 * Generate a color from a string (consistent for the same string)
 */
export const stringToColor = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  let color = '#';
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xFF;
    color += value.toString(16).padStart(2, '0');
  }
  
  return color;
};

/**
 * Format a phone number
 */
export const formatPhoneNumber = (phone: string): string => {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
};

/**
 * Format a credit card number
 */
export const formatCreditCard = (card: string): string => {
  const cleaned = card.replace(/\D/g, '');
  return cleaned.replace(/(\d{4})(?=\d)/g, '$1-');
};

/**
 * Format a Social Security Number
 */
export const formatSSN = (ssn: string): string => {
  const cleaned = ssn.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{2})(\d{4})$/);
  if (match) {
    return `${match[1]}-${match[2]}-${match[3]}`;
  }
  return ssn;
};

/**
 * Sanitize HTML to prevent XSS
 */
export const sanitizeHtml = (html: string): string => {
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
};

/**
 * Escape special characters for regex
 */
export const escapeRegex = (str: string): string => {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

/**
 * Generate a slug from a string
 */
export const slugify = (str: string): string => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

/**
 * Check if two objects are deeply equal
 */
export const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true;
  
  if (typeof obj1 !== 'object' || obj1 === null || typeof obj2 !== 'object' || obj2 === null) {
    return false;
  }
  
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);
  
  if (keys1.length !== keys2.length) return false;
  
  for (const key of keys1) {
    if (!keys2.includes(key) || !deepEqual(obj1[key], obj2[key])) {
      return false;
    }
  }
  
  return true;
};

/**
 * Clone a deep copy of an object
 */
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Merge objects deeply
 */
export const deepMerge = <T extends object, U extends object>(
  target: T,
  source: U
): T & U => {
  // Internal cast: TypeScript cannot prove a write through an intersection's
  // mapped index is sound, though the public signature (T & U) is correct.
  const output = { ...target } as Record<string, unknown>;
  const src = source as Record<string, unknown>;

  for (const key in src) {
    const value = src[key];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      const existing = output[key];
      if (existing && typeof existing === 'object' && !Array.isArray(existing)) {
        output[key] = deepMerge(existing as object, value as object);
      } else {
        output[key] = value;
      }
    } else {
      output[key] = value;
    }
  }

  return output as T & U;
};

/**
 * Pick specific keys from an object
 */
export const pick = <T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Pick<T, K> => {
  const result = {} as Pick<T, K>;
  for (const key of keys) {
    if (key in obj) {
      result[key] = obj[key];
    }
  }
  return result;
};

/**
 * Omit specific keys from an object
 */
export const omit = <T extends object, K extends keyof T>(
  obj: T,
  keys: K[]
): Omit<T, K> => {
  const result = { ...obj } as Record<string, unknown>;
  for (const key of keys) {
    delete result[key as string];
  }
  return result as Omit<T, K>;
};

/**
 * Get a nested property from an object using a dot-notation path
 */
export const getNested = (obj: any, path: string, defaultValue?: any): any => {
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current === null || current === undefined) {
      return defaultValue;
    }
    current = current[key];
  }
  
  return current !== undefined ? current : defaultValue;
};

/**
 * Set a nested property in an object using a dot-notation path
 */
export const setNested = (obj: any, path: string, value: any): any => {
  const keys = path.split('.');
  let current = obj;
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (current[key] === undefined) {
      current[key] = {};
    }
    current = current[key];
  }
  
  current[keys[keys.length - 1]] = value;
  return obj;
};

/**
 * Flatten an object (convert nested object to flat object with dot-notation keys)
 */
export const flattenObject = (obj: any, prefix: string = ''): Record<string, any> => {
  const result: Record<string, any> = {};
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const newKey = prefix ? `${prefix}.${key}` : key;
      
      if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
        Object.assign(result, flattenObject(obj[key], newKey));
      } else {
        result[newKey] = obj[key];
      }
    }
  }
  
  return result;
};

/**
 * Unflatten an object (convert flat object with dot-notation keys to nested object)
 */
export const unflattenObject = (obj: Record<string, any>): any => {
  const result: any = {};
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      setNested(result, key, obj[key]);
    }
  }
  
  return result;
};

export default {
  copyToClipboard,
  timeAgo,
  timeAgoDetailed,
  formatDate,
  formatDateTime,
  formatNumber,
  formatBytes,
  formatDuration,
  truncate,
  truncateMiddle,
  capitalize,
  capitalizeWords,
  generateId,
  generateUUID,
  debounce,
  throttle,
  sleep,
  isEmpty,
  isValidEmail,
  isValidUrl,
  isValidIP,
  isValidDomain,
  getInitials,
  getContrastColor,
  adjustColor,
  randomColor,
  stringToColor,
  formatPhoneNumber,
  formatCreditCard,
  formatSSN,
  sanitizeHtml,
  escapeRegex,
  slugify,
  deepEqual,
  deepClone,
  deepMerge,
  pick,
  omit,
  getNested,
  setNested,
  flattenObject,
  unflattenObject,
};
