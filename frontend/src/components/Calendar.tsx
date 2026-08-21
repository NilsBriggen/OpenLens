/**
 * Calendar Component for OpenLens
 * 
 * A customizable calendar component with various views and features
 */

import React, { useState } from 'react';
import { Calendar as AntCalendar, Badge, Button, Card, Space, Typography, Select, Tooltip } from 'antd';
import { LeftOutlined, RightOutlined, TodayOutlined, CalendarOutlined, UnorderedListOutlined, AppstoreOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import dayjs from 'dayjs';

const { Title, Text } = Typography;
const { Option } = Select;

interface CalendarEvent {
  id: string;
  title: string;
  start: string | Date;
  end?: string | Date;
  allDay?: boolean;
  color?: string;
  description?: string;
  location?: string;
  [key: string]: any;
}

interface CalendarProps {
  value?: dayjs.Dayjs;
  onChange?: (date: dayjs.Dayjs) => void;
  onSelect?: (date: dayjs.Dayjs) => void;
  mode?: 'month' | 'year' | 'decade';
  fullscreen?: boolean;
  headerRender?: (props: { value: dayjs.Dayjs; onChange: (date: dayjs.Dayjs) => void; type: string; onTypeChange: (type: string) => void }) => React.ReactNode;
  footerRender?: (props: { value: dayjs.Dayjs; onChange: (date: dayjs.Dayjs) => void }) => React.ReactNode;
  events?: CalendarEvent[];
  showEvents?: boolean;
  eventRender?: (event: CalendarEvent) => React.ReactNode;
  showWeekNumbers?: boolean;
  showToday?: boolean;
  style?: React.CSSProperties;
  className?: string;
  card?: boolean;
}

const Calendar: React.FC<CalendarProps> = ({
  value,
  onChange,
  onSelect,
  mode = 'month',
  fullscreen = false,
  headerRender,
  footerRender,
  events = [],
  showEvents = true,
  eventRender,
  showWeekNumbers = false,
  showToday = true,
  style = {},
  className = '',
  card = true,
}) => {
  const [internalValue, setInternalValue] = useState(value || dayjs());
  const [currentMode, setCurrentMode] = useState(mode);
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);

  // Sync value
  React.useEffect(() => {
    if (value) {
      setInternalValue(value);
    }
  }, [value]);

  // Handle date change
  const handleDateChange = (date: dayjs.Dayjs) => {
    setInternalValue(date);
    setSelectedDate(date);
    if (onChange) {
      onChange(date);
    }
    if (onSelect) {
      onSelect(date);
    }
  };

  // Handle today
  const handleToday = () => {
    const today = dayjs();
    setInternalValue(today);
    setSelectedDate(today);
    if (onChange) {
      onChange(today);
    }
    if (onSelect) {
      onSelect(today);
    }
  };

  // Handle mode change
  const handleModeChange = (newMode: string) => {
    setCurrentMode(newMode as 'month' | 'year' | 'decade');
  };

  // Get events for a date
  const getEventsForDate = (date: dayjs.Dayjs) => {
    return events.filter(event => {
      const eventStart = dayjs(event.start);
      const eventEnd = event.end ? dayjs(event.end) : eventStart;
      
      return date.isSame(eventStart, 'day') || 
             date.isSame(eventEnd, 'day') ||
             (date.isAfter(eventStart, 'day') && date.isBefore(eventEnd, 'day'));
    });
  };

  // Render default header
  const defaultHeaderRender = (props: { value: dayjs.Dayjs; onChange: (date: dayjs.Dayjs) => void; type: string; onTypeChange: (type: string) => void }) => {
    const { value, onChange, type, onTypeChange } = props;

    return (
      <Space style={{ width: '100%', justifyContent: 'space-between' }}>
        <Space>
          <Button
            type="text"
            icon={<LeftOutlined />}
            onClick={() => {
              const newValue = value.subtract(1, type === 'month' ? 'month' : type === 'year' ? 'year' : 'decade');
              onChange(newValue);
            }}
          />
          <Button
            type="text"
            onClick={() => {
              const newValue = value.subtract(1, type === 'month' ? 'month' : type === 'year' ? 'year' : 'decade');
              onChange(newValue);
            }}
          >
            {value.format(type === 'month' ? 'MMMM YYYY' : type === 'year' ? 'YYYY' : 'YYYY')}
          </Button>
          <Button
            type="text"
            icon={<RightOutlined />}
            onClick={() => {
              const newValue = value.add(1, type === 'month' ? 'month' : type === 'year' ? 'year' : 'decade');
              onChange(newValue);
            }}
          />
        </Space>

        <Space>
          <Select
            value={type}
            onChange={onTypeChange}
            size="small"
            style={{ width: 100 }}
          >
            <Option value="month">Month</Option>
            <Option value="year">Year</Option>
            <Option value="decade">Decade</Option>
          </Select>
          
          {showToday && (
            <Button
              type="text"
              icon={<TodayOutlined />}
              onClick={handleToday}
            >
              Today
            </Button>
          )}
        </Space>
      </Space>
    );
  };

  // Render event
  const renderEvent = (event: CalendarEvent) => {
    if (eventRender) {
      return eventRender(event);
    }

    return (
      <Tooltip title={event.title}>
        <Badge
          color={event.color || '#1890ff'}
          text={event.title}
          style={{ margin: '2px 0' }}
        />
      </Tooltip>
    );
  };

  // Date cell render
  const dateCellRender = (date: dayjs.Dayjs) => {
    if (!showEvents) return date.date();

    const dateEvents = getEventsForDate(date);
    
    if (dateEvents.length === 0) {
      return date.date();
    }

    return (
      <div style={{ position: 'relative' }}>
        {date.date()}
        <div style={{ marginTop: 4 }}>
          {dateEvents.slice(0, 2).map((event, index) => (
            <div key={index} style={{ margin: '2px 0' }}>
              {renderEvent(event)}
            </div>
          ))}
          {dateEvents.length > 2 && (
            <Text type="secondary" style={{ fontSize: 10 }}>
              +{dateEvents.length - 2} more
            </Text>
          )}
        </div>
      </div>
    );
  };

  // Content
  const content = (
    <AntCalendar
      value={internalValue}
      onChange={handleDateChange}
      mode={currentMode}
      fullscreen={fullscreen}
      headerRender={headerRender || defaultHeaderRender}
      footerRender={footerRender}
      dateCellRender={dateCellRender}
      style={style}
      className={className}
    />
  );

  // Return with card if enabled
  if (card) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card
          title={
            <Space>
              <CalendarOutlined />
              Calendar
            </Space>
          }
          bodyStyle={{ padding: 0 }}
          style={{ borderRadius: 12 }}
        >
          {content}
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {content}
    </motion.div>
  );
};

// EventCalendar component (calendar with event list)
interface EventCalendarProps extends Omit<CalendarProps, 'events' | 'showEvents'> {
  events: CalendarEvent[];
  showEventList?: boolean;
  eventListPosition?: 'left' | 'right' | 'bottom';
}

export const EventCalendar: React.FC<EventCalendarProps> = ({
  events = [],
  showEventList = true,
  eventListPosition = 'right',
  ...props
}) => {
  const [selectedDate, setSelectedDate] = useState<dayjs.Dayjs | null>(null);

  // Handle date select
  const handleDateSelect = (date: dayjs.Dayjs) => {
    setSelectedDate(date);
    if (props.onSelect) {
      props.onSelect(date);
    }
  };

  // Get events for selected date
  const getSelectedDateEvents = () => {
    if (!selectedDate) return [];
    
    return events.filter(event => {
      const eventStart = dayjs(event.start);
      const eventEnd = event.end ? dayjs(event.end) : eventStart;
      
      return selectedDate.isSame(eventStart, 'day') || 
             selectedDate.isSame(eventEnd, 'day') ||
             (selectedDate.isAfter(eventStart, 'day') && selectedDate.isBefore(eventEnd, 'day'));
    });
  };

  // Render event list
  const renderEventList = () => {
    if (!showEventList) return null;

    const dateEvents = getSelectedDateEvents();

    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          flex: 1,
          maxWidth: eventListPosition === 'bottom' ? '100%' : 300,
          overflowY: 'auto',
        }}
      >
        <Title level={5} style={{ marginBottom: 16 }}>
          {selectedDate ? selectedDate.format('MMMM D, YYYY') : 'Select a date'}
        </Title>

        {dateEvents.length === 0 ? (
          <Text type="secondary" style={{ textAlign: 'center', display: 'block', padding: 24 }}>
            No events for this date
          </Text>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }}>
            {dateEvents.map((event, index) => (
              <motion.div
                key={event.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <Card
                  size="small"
                  style={{
                    borderLeft: `4px solid ${event.color || '#1890ff'}`,
                    borderRadius: 0,
                  }}
                  bodyStyle={{ padding: 12 }}
                >
                  <Space direction="vertical">
                    <Space>
                      <div
                        style={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          background: event.color || '#1890ff',
                          marginRight: 8,
                        }}
                      />
                      <Title level={5} style={{ margin: 0 }}>
                        {event.title}
                      </Title>
                    </Space>

                    {event.allDay ? (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        All day
                      </Text>
                    ) : (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {dayjs(event.start).format('h:mm A')} - {event.end ? dayjs(event.end).format('h:mm A') : ''}
                      </Text>
                    )}

                    {event.location && (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {event.location}
                      </Text>
                    )}

                    {event.description && (
                      <Text style={{ fontSize: 13, marginTop: 4 }}>
                        {event.description}
                      </Text>
                    )}
                  </Space>
                </Card>
              </motion.div>
            ))}
          </Space>
        )}
      </motion.div>
    );
  };

  // Layout based on position
  if (eventListPosition === 'bottom') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}
      >
        <Calendar
          {...props}
          onSelect={handleDateSelect}
          showEvents={false}
        />
        {renderEventList()}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: 16,
        alignItems: 'flex-start',
      }}
    >
      <div style={{ flex: 1 }}>
        <Calendar
          {...props}
          onSelect={handleDateSelect}
          showEvents={false}
        />
      </div>
      {renderEventList()}
    </motion.div>
  );
};

// ScheduleCalendar component (calendar with schedule view)
interface ScheduleCalendarProps extends Omit<CalendarProps, 'events'> {
  events: CalendarEvent[];
  showTime?: boolean;
  timeFormat?: string;
}

export const ScheduleCalendar: React.FC<ScheduleCalendarProps> = ({
  events = [],
  showTime = true,
  timeFormat = 'h:mm A',
  ...props
}) => {
  // Date cell render with time
  const dateCellRender = (date: dayjs.Dayjs) => {
    const dateEvents = events.filter(event => {
      const eventStart = dayjs(event.start);
      const eventEnd = event.end ? dayjs(event.end) : eventStart;
      
      return date.isSame(eventStart, 'day') || 
             date.isSame(eventEnd, 'day') ||
             (date.isAfter(eventStart, 'day') && date.isBefore(eventEnd, 'day'));
    });

    if (dateEvents.length === 0) {
      return date.date();
    }

    return (
      <div style={{ position: 'relative' }}>
        {date.date()}
        <div style={{ marginTop: 4 }}>
          {dateEvents.slice(0, 3).map((event, index) => (
            <Tooltip
              key={index}
              title={
                <div>
                  <div>{event.title}</div>
                  {showTime && (
                    <div>
                      {dayjs(event.start).format(timeFormat)} - {event.end ? dayjs(event.end).format(timeFormat) : ''}
                    </div>
                  )}
                  {event.location && <div>{event.location}</div>}
                </div>
              }
            >
              <div
                style={{
                  height: 4,
                  background: event.color || '#1890ff',
                  margin: '2px 0',
                  borderRadius: 2,
                }}
              />
            </Tooltip>
          ))}
          {dateEvents.length > 3 && (
            <Text type="secondary" style={{ fontSize: 10 }}>
              +{dateEvents.length - 3} more
            </Text>
          )}
        </div>
      </div>
    );
  };

  return (
    <Calendar
      {...props}
      dateCellRender={dateCellRender}
    />
  );
};

// WeekCalendar component (week view calendar)
interface WeekCalendarProps {
  value?: dayjs.Dayjs;
  onChange?: (date: dayjs.Dayjs) => void;
  events?: CalendarEvent[];
  hourFormat?: string;
  startHour?: number;
  endHour?: number;
  style?: React.CSSProperties;
  className?: string;
}

export const WeekCalendar: React.FC<WeekCalendarProps> = ({
  value,
  onChange,
  events = [],
  hourFormat = 'h A',
  startHour = 8,
  endHour = 18,
  style = {},
  className = '',
}) => {
  const [internalValue, setInternalValue] = useState(value || dayjs());

  // Sync value
  React.useEffect(() => {
    if (value) {
      setInternalValue(value);
    }
  }, [value]);

  // Get week dates
  const getWeekDates = () => {
    const startOfWeek = internalValue.startOf('week');
    const dates: dayjs.Dayjs[] = [];
    
    for (let i = 0; i < 7; i++) {
      dates.push(startOfWeek.add(i, 'day'));
    }
    
    return dates;
  };

  // Get events for a date
  const getEventsForDate = (date: dayjs.Dayjs) => {
    return events.filter(event => {
      const eventStart = dayjs(event.start);
      const eventEnd = event.end ? dayjs(event.end) : eventStart;
      
      return date.isSame(eventStart, 'day') || 
             date.isSame(eventEnd, 'day') ||
             (date.isAfter(eventStart, 'day') && date.isBefore(eventEnd, 'day'));
    });
  };

  // Get event position
  const getEventPosition = (event: CalendarEvent) => {
    const start = dayjs(event.start);
    const end = event.end ? dayjs(event.end) : start.add(1, 'hour');
    
    const startHour = start.hour();
    const endHour = end.hour();
    const duration = end.diff(start, 'hour');
    
    const top = ((startHour - startHour) / (endHour - startHour)) * 100;
    const height = (duration / (endHour - startHour)) * 100;
    
    return { top, height };
  };

  const weekDates = getWeekDates();
  const hours = Array.from({ length: endHour - startHour }, (_, i) => startHour + i);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        border: '1px solid var(--border-color)',
        borderRadius: 12,
        background: 'var(--card-bg)',
        overflow: 'hidden',
        ...style,
      }}
      className={className}
    >
      {/* Header with days */}
      <div style={{ display: 'grid', gridTemplateColumns: '60px repeat(7, 1fr)', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ padding: 8, textAlign: 'center', fontWeight: 'bold' }} />
        {weekDates.map((date, index) => (
          <div
            key={index}
            style={{
              padding: 8,
              textAlign: 'center',
              fontWeight: 'bold',
              fontSize: 12,
              background: date.isSame(internalValue, 'day') ? 'var(--bg-color-secondary)' : 'transparent',
            }}
          >
            {date.format('ddd')}
            <div style={{ fontSize: 10, color: 'var(--text-color-secondary)' }}>
              {date.format('D')}
            </div>
          </div>
        ))}
      </div>

      {/* Time slots */}
      <div style={{ display: 'grid', gridTemplateColumns: '60px repeat(7, 1fr)', height: 'calc(100% - 40px)', overflowY: 'auto' }}>
        {/* Time labels */}
        <div style={{ padding: 8, borderRight: '1px solid var(--border-color)' }}>
          {hours.map((hour, index) => (
            <div key={index} style={{ height: 40, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', paddingRight: 8, fontSize: 10 }}>
              {hour % 12 || 12}:00 {hour >= 12 ? 'PM' : 'AM'}
            </div>
          ))}
        </div>

        {/* Event cells */}
        {weekDates.map((date, dateIndex) => (
          <div
            key={dateIndex}
            style={{
              borderRight: dateIndex < 6 ? '1px solid var(--border-color)' : 'none',
              position: 'relative',
            }}
          >
            {hours.map((hour, hourIndex) => {
              const dateEvents = getEventsForDate(date);
              const hourEvents = dateEvents.filter(event => {
                const eventStart = dayjs(event.start);
                return eventStart.hour() === hour;
              });

              return (
                <div
                  key={hourIndex}
                  style={{
                    height: 40,
                    borderBottom: hourIndex < hours.length - 1 ? '1px solid var(--border-color)' : 'none',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {hourEvents.map((event, eventIndex) => (
                    <Tooltip
                      key={eventIndex}
                      title={
                        <div>
                          <div>{event.title}</div>
                          <div>{dayjs(event.start).format('h:mm A')} - {event.end ? dayjs(event.end).format('h:mm A') : ''}</div>
                          {event.location && <div>{event.location}</div>}
                        </div>
                      }
                    >
                      <div
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: event.color || '#1890ff',
                          opacity: 0.8,
                          borderRadius: 4,
                          margin: 2,
                        }}
                      />
                    </Tooltip>
                  ))}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </motion.div>
  );
};

// DateRangeCalendar component (calendar for selecting date ranges)
interface DateRangeCalendarProps {
  value?: [dayjs.Dayjs, dayjs.Dayjs];
  onChange?: (dates: [dayjs.Dayjs, dayjs.Dayjs]) => void;
  disabledDate?: (date: dayjs.Dayjs) => boolean;
  presets?: { label: string; value: [dayjs.Dayjs, dayjs.Dayjs] }[];
  style?: React.CSSProperties;
  className?: string;
}

export const DateRangeCalendar: React.FC<DateRangeCalendarProps> = ({
  value,
  onChange,
  disabledDate,
  presets = [],
  style = {},
  className = '',
}) => {
  const [internalValue, setInternalValue] = useState<[dayjs.Dayjs, dayjs.Dayjs] | undefined>(value);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);

  // Sync value
  React.useEffect(() => {
    if (value) {
      setInternalValue(value);
    }
  }, [value]);

  // Handle date change
  const handleDateChange = (dates: [dayjs.Dayjs, dayjs.Dayjs]) => {
    setInternalValue(dates);
    setSelectedPreset(null);
    if (onChange) {
      onChange(dates);
    }
  };

  // Handle preset select
  const handlePresetSelect = (presetValue: [dayjs.Dayjs, dayjs.Dayjs]) => {
    setInternalValue(presetValue);
    if (onChange) {
      onChange(presetValue);
    }
  };

  // Date cell render
  const dateCellRender = (date: dayjs.Dayjs) => {
    if (!internalValue) return date.date();

    const [start, end] = internalValue;
    
    if (date.isSame(start, 'day') && date.isSame(end, 'day')) {
      return (
        <div
          style={{
            background: '#1890ff',
            color: '#fff',
            borderRadius: 4,
            padding: '2px 4px',
          }}
        >
          {date.date()}
        </div>
      );
    }

    if (date.isSame(start, 'day')) {
      return (
        <div
          style={{
            background: '#1890ff',
            color: '#fff',
            borderTopLeftRadius: 4,
            borderBottomLeftRadius: 4,
            padding: '2px 4px',
          }}
        >
          {date.date()}
        </div>
      );
    }

    if (date.isSame(end, 'day')) {
      return (
        <div
          style={{
            background: '#1890ff',
            color: '#fff',
            borderTopRightRadius: 4,
            borderBottomRightRadius: 4,
            padding: '2px 4px',
          }}
        >
          {date.date()}
        </div>
      );
    }

    if (date.isAfter(start, 'day') && date.isBefore(end, 'day')) {
      return (
        <div
          style={{
            background: 'rgba(24, 144, 255, 0.1)',
            padding: '2px 4px',
          }}
        >
          {date.date()}
        </div>
      );
    }

    return date.date();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: 16,
        ...style,
      }}
      className={className}
    >
      {/* Presets */}
      {presets.length > 0 && (
        <div style={{ width: 200 }}>
          <Title level={5} style={{ marginBottom: 16 }}>
            Presets
          </Title>
          <Space direction="vertical">
            {presets.map((preset, index) => (
              <motion.div
                key={index}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  type={selectedPreset === preset.label ? 'primary' : 'default'}
                  onClick={() => handlePresetSelect(preset.value)}
                  block
                  size="small"
                >
                  {preset.label}
                </Button>
              </motion.div>
            ))}
          </Space>
        </div>
      )}

      {/* Calendar */}
      <div style={{ flex: 1 }}>
        <Calendar
          value={internalValue?.[0]}
          onChange={(date) => {
            if (!internalValue) {
              handleDateChange([date, date]);
            } else {
              const [start] = internalValue;
              if (date.isBefore(start, 'day')) {
                handleDateChange([date, start]);
              } else {
                handleDateChange([start, date]);
              }
            }
          }}
          mode="month"
          dateCellRender={dateCellRender}
          disabledDate={disabledDate}
        />

        {/* Selected range display */}
        {internalValue && (
          <div style={{ marginTop: 16, padding: 16, background: 'var(--bg-color-secondary)', borderRadius: 8 }}>
            <Space>
              <Text strong>Selected Range:</Text>
              <Text>{internalValue[0].format('MMM D, YYYY')}</Text>
              <Text type="secondary">to</Text>
              <Text>{internalValue[1].format('MMM D, YYYY')}</Text>
            </Space>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default Calendar;
