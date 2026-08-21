/**
 * Avatar Group Component for OpenLens
 * 
 * A component that displays multiple avatars in a stacked or grouped layout
 */

import React from 'react';
import { Avatar, Tooltip, Space, Typography } from 'antd';
import { motion } from 'framer-motion';
import { getInitials, stringToColor } from '../utils/uiUtils';

const { Text } = Typography;

interface AvatarItem {
  id?: string;
  name?: string;
  src?: string;
  alt?: string;
  color?: string;
  size?: number;
  tooltip?: string;
  [key: string]: any;
}

interface AvatarGroupProps {
  avatars: AvatarItem[];
  max?: number;
  size?: 'small' | 'default' | 'large' | number;
  shape?: 'circle' | 'square';
  stacked?: boolean;
  overlap?: number;
  spacing?: number;
  showMore?: boolean;
  moreText?: string;
  tooltip?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

const AvatarGroup: React.FC<AvatarGroupProps> = ({
  avatars = [],
  max = 5,
  size = 'default',
  shape = 'circle',
  stacked = true,
  overlap = -8,
  spacing = 8,
  showMore = true,
  moreText = '+{n}',
  tooltip = true,
  style = {},
  className = '',
}) => {
  // Get size in pixels
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 24,
      default: 32,
      large: 40,
    };
    return sizes[size] || sizes.default;
  };

  const avatarSize = getSize();

  // Get visible avatars
  const visibleAvatars = avatars.slice(0, max);
  const hiddenCount = avatars.length - max;

  // Get color for avatar
  const getAvatarColor = (avatar: AvatarItem, index: number): string => {
    if (avatar.color) return avatar.color;
    if (avatar.name) return stringToColor(avatar.name);
    return stringToColor(`avatar-${index}`);
  };

  // Get initials for avatar
  const getAvatarInitials = (avatar: AvatarItem): string => {
    if (avatar.name) return getInitials(avatar.name);
    if (avatar.alt) return getInitials(avatar.alt);
    return '?';
  };

  // Render stacked avatars
  if (stacked) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          alignItems: 'center',
          ...style,
        }}
        className={className}
      >
        {visibleAvatars.map((avatar, index) => (
          <motion.div
            key={avatar.id || index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            style={{
              marginLeft: index > 0 ? overlap : 0,
            }}
          >
            {tooltip && avatar.tooltip ? (
              <Tooltip title={avatar.tooltip}>
                <Avatar
                  src={avatar.src}
                  alt={avatar.alt || avatar.name}
                  size={avatarSize}
                  shape={shape}
                  style={{
                    background: getAvatarColor(avatar, index),
                    border: '2px solid var(--card-bg)',
                  }}
                >
                  {avatar.src ? null : getAvatarInitials(avatar)}
                </Avatar>
              </Tooltip>
            ) : (
              <Avatar
                src={avatar.src}
                alt={avatar.alt || avatar.name}
                size={avatarSize}
                shape={shape}
                style={{
                  background: getAvatarColor(avatar, index),
                  border: '2px solid var(--card-bg)',
                }}
              >
                {avatar.src ? null : getAvatarInitials(avatar)}
              </Avatar>
            )}
          </motion.div>
        ))}

        {showMore && hiddenCount > 0 && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: visibleAvatars.length * 0.05 }}
            style={{
              marginLeft: overlap,
            }}
          >
            <Avatar
              size={avatarSize}
              shape={shape}
              style={{
                background: 'var(--bg-color-secondary)',
                border: '2px solid var(--card-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Text style={{ fontSize: avatarSize / 2, color: 'var(--text-color-secondary)' }}>
                {moreText.replace('{n}', String(hiddenCount))}
              </Text>
            </Avatar>
          </motion.div>
        )}
      </motion.div>
    );
  }

  // Render horizontal avatars
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: spacing,
        flexWrap: 'wrap',
        ...style,
      }}
      className={className}
    >
      {visibleAvatars.map((avatar, index) => (
        <motion.div
          key={avatar.id || index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.05 }}
        >
          {tooltip && avatar.tooltip ? (
            <Tooltip title={avatar.tooltip}>
              <Avatar
                src={avatar.src}
                alt={avatar.alt || avatar.name}
                size={avatarSize}
                shape={shape}
                style={{
                  background: getAvatarColor(avatar, index),
                }}
              >
                {avatar.src ? null : getAvatarInitials(avatar)}
              </Avatar>
            </Tooltip>
          ) : (
            <Avatar
              src={avatar.src}
              alt={avatar.alt || avatar.name}
              size={avatarSize}
              shape={shape}
              style={{
                background: getAvatarColor(avatar, index),
              }}
            >
              {avatar.src ? null : getAvatarInitials(avatar)}
            </Avatar>
          )}
        </motion.div>
      ))}

      {showMore && hiddenCount > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: visibleAvatars.length * 0.05 }}
        >
          <Avatar
            size={avatarSize}
            shape={shape}
            style={{
              background: 'var(--bg-color-secondary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Text style={{ fontSize: avatarSize / 2, color: 'var(--text-color-secondary)' }}>
              {moreText.replace('{n}', String(hiddenCount))}
            </Text>
          </Avatar>
        </motion.div>
      )}
    </motion.div>
  );
};

// UserAvatar component
interface UserAvatarProps {
  user: {
    id?: string;
    name?: string;
    email?: string;
    avatar?: string;
    color?: string;
    [key: string]: any;
  };
  size?: 'small' | 'default' | 'large' | number;
  shape?: 'circle' | 'square';
  showName?: boolean;
  namePosition?: 'top' | 'bottom' | 'left' | 'right';
  tooltip?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({
  user,
  size = 'default',
  shape = 'circle',
  showName = false,
  namePosition = 'bottom',
  tooltip = true,
  style = {},
  className = '',
}) => {
  // Get size in pixels
  const getSize = () => {
    if (typeof size === 'number') return size;
    const sizes: Record<string, number> = {
      small: 24,
      default: 32,
      large: 40,
    };
    return sizes[size] || sizes.default;
  };

  const avatarSize = getSize();

  // Get color
  const color = user.color || stringToColor(user.name || user.email || user.id || '');

  // Get initials
  const initials = getInitials(user.name || user.email || '?');

  // Get tooltip text
  const tooltipText = user.name || user.email || user.id;

  // Build content based on name position
  const content = (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        ...style,
      }}
      className={className}
    >
      {namePosition === 'left' && showName && (
        <Text style={{ fontSize: avatarSize / 1.5 }}>
          {user.name}
        </Text>
      )}

      {tooltip ? (
        <Tooltip title={tooltipText}>
          <Avatar
            src={user.avatar}
            alt={user.name}
            size={avatarSize}
            shape={shape}
            style={{
              background: color,
              cursor: 'pointer',
            }}
          >
            {user.avatar ? null : initials}
          </Avatar>
        </Tooltip>
      ) : (
        <Avatar
          src={user.avatar}
          alt={user.name}
          size={avatarSize}
          shape={shape}
          style={{
            background: color,
          }}
        >
          {user.avatar ? null : initials}
        </Avatar>
      )}

      {namePosition === 'right' && showName && (
        <Text style={{ fontSize: avatarSize / 1.5 }}>
          {user.name}
        </Text>
      )}
    </motion.div>
  );

  // Handle top/bottom positioning
  if (namePosition === 'top' || namePosition === 'bottom') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          flexDirection: namePosition === 'top' ? 'column' : 'column-reverse',
          alignItems: 'center',
          gap: 4,
          ...style,
        }}
        className={className}
      >
        {showName && (
          <Text style={{ fontSize: avatarSize / 1.5 }}>
            {user.name}
          </Text>
        )}
        
        {tooltip ? (
          <Tooltip title={tooltipText}>
            <Avatar
              src={user.avatar}
              alt={user.name}
              size={avatarSize}
              shape={shape}
              style={{
                background: color,
                cursor: 'pointer',
              }}
            >
              {user.avatar ? null : initials}
            </Avatar>
          </Tooltip>
        ) : (
          <Avatar
            src={user.avatar}
            alt={user.name}
            size={avatarSize}
            shape={shape}
            style={{
              background: color,
            }}
          >
            {user.avatar ? null : initials}
          </Avatar>
        )}
      </motion.div>
    );
  }

  return content;
};

// TeamAvatar component (displays a team/group of users)
interface TeamAvatarProps {
  users: UserAvatarProps['user'][];
  size?: 'small' | 'default' | 'large' | number;
  max?: number;
  showMore?: boolean;
  moreText?: string;
  tooltip?: boolean;
  style?: React.CSSProperties;
  className?: string;
}

export const TeamAvatar: React.FC<TeamAvatarProps> = ({
  users = [],
  size = 'default',
  max = 5,
  showMore = true,
  moreText = '+{n}',
  tooltip = true,
  style = {},
  className = '',
}) => {
  return (
    <AvatarGroup
      avatars={users.map(user => ({
        id: user.id,
        name: user.name,
        src: user.avatar,
        alt: user.name,
        color: user.color,
        tooltip: tooltip ? (user.name || user.email) : undefined,
      }))}
      max={max}
      size={size}
      shape="circle"
      stacked={true}
      showMore={showMore}
      moreText={moreText}
      tooltip={tooltip}
      style={style}
      className={className}
    />
  );
};

export default AvatarGroup;
