/**
 * Rating Component for OpenLens
 * 
 * A customizable rating component with various styles and interactions
 */

import React, { useState } from 'react';
import { Rate, Typography, Space, Tooltip } from 'antd';
import { StarOutlined, StarFilled, StarTwoTone } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Text } = Typography;

interface RatingProps {
  value?: number;
  onChange?: (value: number) => void;
  count?: number;
  allowHalf?: boolean;
  allowClear?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  size?: 'small' | 'default' | 'large' | number;
  character?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  tooltip?: boolean;
  tooltips?: string[];
  color?: string;
  activeColor?: string;
  inactiveColor?: string;
  showValue?: boolean;
  valueTemplate?: string;
}

const Rating: React.FC<RatingProps> = ({
  value = 0,
  onChange,
  count = 5,
  allowHalf = false,
  allowClear = true,
  disabled = false,
  readOnly = false,
  size = 'default',
  character = <StarOutlined />,
  style = {},
  className = '',
  tooltip = false,
  tooltips,
  color = '#ffc600',
  activeColor,
  inactiveColor = '#d9d9d9',
  showValue = false,
  valueTemplate = '{value} / {count}',
}) => {
  const [hoverValue, setHoverValue] = useState<number | undefined>(undefined);

  // Get size
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 16,
      default: 20,
      large: 24,
    };
    return sizes[size] || sizes.default;
  };

  // Handle change
  const handleChange = (newValue: number) => {
    if (disabled || readOnly) return;
    if (onChange) {
      onChange(newValue);
    }
  };

  // Handle hover
  const handleHover = (newValue: number) => {
    if (disabled || readOnly) return;
    setHoverValue(newValue);
  };

  // Handle leave
  const handleLeave = () => {
    if (disabled || readOnly) return;
    setHoverValue(undefined);
  };

  // Get tooltip for a star
  const getTooltip = (index: number): string | undefined => {
    if (!tooltip) return undefined;
    if (tooltips && tooltips[index]) return tooltips[index];
    return `${index + 1} ${index + 1 === 1 ? 'star' : 'stars'}`;
  };

  // Build value display
  const valueDisplay = showValue && (
    <Text style={{ marginLeft: 8, fontSize: getSize() * 0.8 }}>
      {valueTemplate
        .replace('{value}', String(value))
        .replace('{count}', String(count))}
    </Text>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Space align="center">
        <Rate
          value={value}
          onChange={handleChange}
          count={count}
          allowHalf={allowHalf}
          allowClear={allowClear}
          disabled={disabled || readOnly}
          character={character}
          style={{ fontSize: getSize() }}
          onHoverChange={handleHover}
          onFocus={handleLeave}
          onBlur={handleLeave}
          tooltip={tooltip}
          tooltips={tooltips}
        />
        {valueDisplay}
      </Space>
    </motion.div>
  );
};

// StarRating component (alias for Rating)
export const StarRating: React.FC<RatingProps> = (props) => {
  return <Rating {...props} />;
};

// EmojiRating component
interface EmojiRatingProps {
  value?: number;
  onChange?: (value: number) => void;
  count?: number;
  emojis?: string[];
  size?: 'small' | 'default' | 'large' | number;
  disabled?: boolean;
  readOnly?: boolean;
  style?: React.CSSProperties;
  className?: string;
  showValue?: boolean;
}

export const EmojiRating: React.FC<EmojiRatingProps> = ({
  value = 0,
  onChange,
  count = 5,
  emojis = ['😡', '😞', '😐', '😊', '😍'],
  size = 'default',
  disabled = false,
  readOnly = false,
  style = {},
  className = '',
  showValue = false,
}) => {
  // Get size
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 20,
      default: 28,
      large: 36,
    };
    return sizes[size] || sizes.default;
  };

  // Handle click
  const handleClick = (index: number) => {
    if (disabled || readOnly) return;
    if (onChange) {
      onChange(index + 1);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Space align="center">
        {Array.from({ length: count }).map((_, index) => {
          const emoji = emojis[index] || emojis[emojis.length - 1];
          const isSelected = index < (value || 0);
          
          return (
            <motion.span
              key={index}
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => handleClick(index)}
              style={{
                fontSize: getSize(),
                cursor: disabled || readOnly ? 'default' : 'pointer',
                opacity: isSelected ? 1 : 0.5,
              }}
            >
              {emoji}
            </motion.span>
          );
        })}
        
        {showValue && (
          <Text style={{ marginLeft: 8, fontSize: getSize() * 0.8 }}>
            {value} / {count}
          </Text>
        )}
      </Space>
    </motion.div>
  );
};

// LikeDislike component
interface LikeDislikeProps {
  value?: 'like' | 'dislike' | null;
  onChange?: (value: 'like' | 'dislike' | null) => void;
  likeIcon?: React.ReactNode;
  dislikeIcon?: React.ReactNode;
  likeText?: string;
  dislikeText?: string;
  size?: 'small' | 'default' | 'large' | number;
  disabled?: boolean;
  readOnly?: boolean;
  allowClear?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const LikeDislike: React.FC<LikeDislikeProps> = ({
  value = null,
  onChange,
  likeIcon = '👍',
  dislikeIcon = '👎',
  likeText = 'Like',
  dislikeText = 'Dislike',
  size = 'default',
  disabled = false,
  readOnly = false,
  allowClear = false,
  style = {},
  className = '',
}) => {
  // Get size
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 20,
      default: 24,
      large: 28,
    };
    return sizes[size] || sizes.default;
  };

  // Handle like
  const handleLike = () => {
    if (disabled || readOnly) return;
    const newValue = value === 'like' && allowClear ? null : 'like';
    if (onChange) {
      onChange(newValue);
    }
  };

  // Handle dislike
  const handleDislike = () => {
    if (disabled || readOnly) return;
    const newValue = value === 'dislike' && allowClear ? null : 'dislike';
    if (onChange) {
      onChange(newValue);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Space>
        <motion.button
          type="button"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleLike}
          disabled={disabled || readOnly}
          style={{
            background: 'none',
            border: 'none',
            cursor: disabled || readOnly ? 'default' : 'pointer',
            fontSize: getSize(),
            opacity: value === 'like' ? 1 : 0.5,
            padding: 0,
          }}
        >
          <Space align="center">
            {likeIcon}
            {likeText && (
              <Text style={{ fontSize: getSize() * 0.8 }}>
                {likeText}
              </Text>
            )}
          </Space>
        </motion.button>

        <motion.button
          type="button"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleDislike}
          disabled={disabled || readOnly}
          style={{
            background: 'none',
            border: 'none',
            cursor: disabled || readOnly ? 'default' : 'pointer',
            fontSize: getSize(),
            opacity: value === 'dislike' ? 1 : 0.5,
            padding: 0,
          }}
        >
          <Space align="center">
            {dislikeIcon}
            {dislikeText && (
              <Text style={{ fontSize: getSize() * 0.8 }}>
                {dislikeText}
              </Text>
            )}
          </Space>
        </motion.button>
      </Space>
    </motion.div>
  );
};

// Score component (numeric score with stars)
interface ScoreProps {
  value?: number;
  max?: number;
  size?: 'small' | 'default' | 'large' | number;
  showValue?: boolean;
  valueTemplate?: string;
  style?: React.CSSProperties;
  className?: string;
}

export const Score: React.FC<ScoreProps> = ({
  value = 0,
  max = 5,
  size = 'default',
  showValue = true,
  valueTemplate = '{value} / {max}',
  style = {},
  className = '',
}) => {
  // Get size
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 16,
      default: 20,
      large: 24,
    };
    return sizes[size] || sizes.default;
  };

  // Calculate percentage
  const percentage = (value / max) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Space align="center">
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
          }}
        >
          {Array.from({ length: max }).map((_, index) => {
            const isFilled = index < Math.floor(value);
            const isPartial = index === Math.floor(value) && value % 1 !== 0;
            const fillPercentage = isPartial ? (value % 1) * 100 : 0;

            return (
              <div
                key={index}
                style={{
                  position: 'relative',
                  display: 'inline-block',
                  fontSize: getSize(),
                }}
              >
                <StarOutlined
                  style={{
                    color: '#d9d9d9',
                  }}
                />
                {isFilled && (
                  <StarFilled
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      color: '#ffc600',
                    }}
                  />
                )}
                {isPartial && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: `${fillPercentage}%`,
                      overflow: 'hidden',
                    }}
                  >
                    <StarFilled
                      style={{
                        color: '#ffc600',
                      }}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        {showValue && (
          <Text style={{ marginLeft: 8, fontSize: getSize() * 0.8 }}>
            {valueTemplate
              .replace('{value}', String(value))
              .replace('{max}', String(max))}
          </Text>
        )}
      </Space>
    </motion.div>
  );
};

export default Rating;
