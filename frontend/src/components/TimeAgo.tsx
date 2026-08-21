/**
 * TimeAgo Component for OpenLens
 * 
 * A component that displays relative time and updates automatically
 */

import React, { useState, useEffect } from 'react';
import { Tooltip, Typography, Space } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { timeAgo, timeAgoDetailed, formatDate, formatDateTime } from '../utils/uiUtils';

const { Text } = Typography;

interface TimeAgoProps {
  date: string | Date;
  format?: 'short' | 'long' | 'detailed' | 'date' | 'datetime';
  tooltip?: boolean;
  tooltipFormat?: string;
  interval?: number;
  prefix?: string;
  suffix?: string;
  style?: React.CSSProperties;
  className?: string;
  icon?: React.ReactNode;
  showIcon?: boolean;
}

const TimeAgo: React.FC<TimeAgoProps> = ({
  date,
  format = 'short',
  tooltip = true,
  tooltipFormat = 'MMM D, YYYY h:mm A',
  interval = 60000, // 1 minute
  prefix,
  suffix,
  style = {},
  className = '',
  icon = <ClockCircleOutlined style={{ fontSize: 12 }} />,
  showIcon = false,
}) => {
  const [timeString, setTimeString] = useState<string>('');
  const [tooltipString, setTooltipString] = useState<string>('');

  // Update time string
  useEffect(() => {
    const updateTime = () => {
      switch (format) {
        case 'short':
          setTimeString(timeAgo(date));
          break;
        case 'long':
          setTimeString(timeAgoDetailed(date));
          break;
        case 'detailed':
          setTimeString(timeAgoDetailed(date));
          break;
        case 'date':
          setTimeString(formatDate(date));
          break;
        case 'datetime':
          setTimeString(formatDateTime(date));
          break;
        default:
          setTimeString(timeAgo(date));
      }

      // Update tooltip
      setTooltipString(formatDateTime(date, tooltipFormat));
    };

    // Initial update
    updateTime();

    // Set up interval for updates
    const timer = setInterval(updateTime, interval);

    return () => clearInterval(timer);
  }, [date, format, interval, tooltipFormat]);

  // Build content
  const content = (
    <Text style={style} className={className}>
      {prefix}
      {showIcon && icon && <span style={{ marginRight: 4 }}>{icon}</span>}
      {timeString}
      {suffix}
    </Text>
  );

  // Return with tooltip if enabled
  if (tooltip) {
    return (
      <motion.span
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Tooltip title={tooltipString}>
          {content}
        </Tooltip>
      </motion.span>
    );
  }

  return (
    <motion.span
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {content}
    </motion.span>
  );
};

// RelativeTime component (alias for TimeAgo)
export const RelativeTime: React.FC<TimeAgoProps> = (props) => {
  return <TimeAgo {...props} />;
};

// DateTime component (displays formatted date/time)
interface DateTimeProps {
  date: string | Date;
  format?: string;
  style?: React.CSSProperties;
  className?: string;
  icon?: React.ReactNode;
  showIcon?: boolean;
}

export const DateTime: React.FC<DateTimeProps> = ({
  date,
  format = 'MMM D, YYYY h:mm A',
  style = {},
  className = '',
  icon = <ClockCircleOutlined style={{ fontSize: 12 }} />,
  showIcon = false,
}) => {
  return (
    <motion.span
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Text style={style} className={className}>
        {showIcon && icon && <span style={{ marginRight: 4 }}>{icon}</span>}
        {formatDateTime(date, format)}
      </Text>
    </motion.span>
  );
};

// Countdown component
interface CountdownProps {
  target: string | Date;
  format?: 'short' | 'long';
  onComplete?: () => void;
  style?: React.CSSProperties;
  className?: string;
  prefix?: string;
  suffix?: string;
}

export const Countdown: React.FC<CountdownProps> = ({
  target,
  format = 'short',
  onComplete,
  style = {},
  className = '',
  prefix,
  suffix,
}) => {
  const [timeLeft, setTimeLeft] = useState<string>('');
  const [completed, setCompleted] = useState(false);

  // Update countdown
  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date();
      const targetDate = new Date(target);
      const diff = targetDate.getTime() - now.getTime();

      if (diff <= 0) {
        setCompleted(true);
        setTimeLeft('0');
        if (onComplete) {
          onComplete();
        }
        return;
      }

      const duration = Math.floor(diff / 1000);

      if (format === 'long') {
        const days = Math.floor(duration / 86400);
        const hours = Math.floor((duration % 86400) / 3600);
        const minutes = Math.floor((duration % 3600) / 60);
        const seconds = duration % 60;

        const parts: string[] = [];
        if (days > 0) parts.push(`${days}d`);
        if (hours > 0) parts.push(`${hours}h`);
        if (minutes > 0) parts.push(`${minutes}m`);
        parts.push(`${seconds}s`);

        setTimeLeft(parts.join(' '));
      } else {
        // Short format
        if (duration >= 86400) {
          setTimeLeft(`${Math.floor(duration / 86400)}d`);
        } else if (duration >= 3600) {
          setTimeLeft(`${Math.floor(duration / 3600)}h`);
        } else if (duration >= 60) {
          setTimeLeft(`${Math.floor(duration / 60)}m`);
        } else {
          setTimeLeft(`${duration}s`);
        }
      }
    };

    // Initial update
    updateCountdown();

    // Set up interval
    const timer = setInterval(updateCountdown, 1000);

    return () => clearInterval(timer);
  }, [target, format, onComplete]);

  return (
    <motion.span
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Text
        style={style}
        className={className}
        type={completed ? 'success' : undefined}
      >
        {prefix}
        {timeLeft}
        {suffix}
      </Text>
    </motion.span>
  );
};

// Age component (displays age from birth date)
interface AgeProps {
  birthDate: string | Date;
  showAge?: boolean;
  showBirthDate?: boolean;
  birthDateFormat?: string;
  style?: React.CSSProperties;
  className?: string;
}

export const Age: React.FC<AgeProps> = ({
  birthDate,
  showAge = true,
  showBirthDate = false,
  birthDateFormat = 'MMM D, YYYY',
  style = {},
  className = '',
}) => {
  const [age, setAge] = useState<number>(0);

  // Calculate age
  useEffect(() => {
    const calculateAge = () => {
      const birth = new Date(birthDate);
      const today = new Date();
      let age = today.getFullYear() - birth.getFullYear();
      const monthDiff = today.getMonth() - birth.getMonth();

      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
      }

      setAge(age);
    };

    calculateAge();

    // Update once per day
    const timer = setInterval(calculateAge, 86400000);

    return () => clearInterval(timer);
  }, [birthDate]);

  return (
    <motion.span
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Text style={style} className={className}>
        {showAge && `${age} year${age !== 1 ? 's' : ''}`}
        {showAge && showBirthDate && ' ('}
        {showBirthDate && formatDate(birthDate, birthDateFormat)}
        {showAge && showBirthDate && ')'}
      </Text>
    </motion.span>
  );
};

export default TimeAgo;
