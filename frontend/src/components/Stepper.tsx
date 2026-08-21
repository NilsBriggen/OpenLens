/**
 * Stepper Component for OpenLens
 * 
 * A customizable stepper component for multi-step processes
 */

import React, { useState } from 'react';
import { Steps, Button, Space, Typography, Card, Row, Col } from 'antd';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

interface StepItem {
  key: string;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  content?: React.ReactNode;
  disabled?: boolean;
  [key: string]: any;
}

interface StepperProps {
  items: StepItem[];
  current?: number;
  onChange?: (current: number) => void;
  direction?: 'horizontal' | 'vertical';
  size?: 'small' | 'default';
  status?: 'wait' | 'process' | 'finish' | 'error';
  type?: 'default' | 'navigation' | 'inline';
  progressDot?: boolean | ((icon: React.ReactNode, status: string) => React.ReactNode);
  responsive?: boolean;
  style?: React.CSSProperties;
  className?: string;
  showNavigation?: boolean;
  nextText?: string;
  prevText?: string;
  finishText?: string;
  onFinish?: () => void;
  showContent?: boolean;
  contentStyle?: React.CSSProperties;
}

const Stepper: React.FC<StepperProps> = ({
  items = [],
  current = 0,
  onChange,
  direction = 'horizontal',
  size = 'default',
  status,
  type = 'default',
  progressDot,
  responsive = true,
  style = {},
  className = '',
  showNavigation = true,
  nextText = 'Next',
  prevText = 'Previous',
  finishText = 'Finish',
  onFinish,
  showContent = true,
  contentStyle = {},
}) => {
  const [internalCurrent, setInternalCurrent] = useState(current);

  // Sync current
  React.useEffect(() => {
    setInternalCurrent(current);
  }, [current]);

  // Handle change
  const handleChange = (newCurrent: number) => {
    setInternalCurrent(newCurrent);
    if (onChange) {
      onChange(newCurrent);
    }
  };

  // Handle next
  const handleNext = () => {
    if (internalCurrent < items.length - 1) {
      handleChange(internalCurrent + 1);
    } else if (onFinish) {
      onFinish();
    }
  };

  // Handle prev
  const handlePrev = () => {
    if (internalCurrent > 0) {
      handleChange(internalCurrent - 1);
    }
  };

  // Get step status
  const getStepStatus = (index: number): 'wait' | 'process' | 'finish' | 'error' => {
    if (status) return status;
    if (index < internalCurrent) return 'finish';
    if (index === internalCurrent) return 'process';
    return 'wait';
  };

  // Build steps
  const buildSteps = () => {
    return items.map((item, index) => ({
      key: item.key,
      title: item.title,
      description: item.description,
      icon: item.icon,
      disabled: item.disabled,
      status: getStepStatus(index),
    }));
  };

  // Build content
  const buildContent = () => {
    if (!showContent) return null;

    const currentItem = items[internalCurrent];
    if (!currentItem) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          marginTop: 24,
          padding: 24,
          background: 'var(--card-bg)',
          borderRadius: 12,
          border: '1px solid var(--border-color)',
          ...contentStyle,
        }}
      >
        {currentItem.content}
      </motion.div>
    );
  };

  // Build navigation
  const buildNavigation = () => {
    if (!showNavigation) return null;

    const isFirst = internalCurrent === 0;
    const isLast = internalCurrent === items.length - 1;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        style={{ marginTop: 24, textAlign: 'right' }}
      >
        <Space>
          {!isFirst && (
            <Button onClick={handlePrev} size={size}>
              {prevText}
            </Button>
          )}
          
          {isLast ? (
            <Button type="primary" onClick={handleNext} size={size}>
              {finishText}
            </Button>
          ) : (
            <Button type="primary" onClick={handleNext} size={size}>
              {nextText}
            </Button>
          )}
        </Space>
      </motion.div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={style}
      className={className}
    >
      <Steps
        current={internalCurrent}
        onChange={handleChange}
        direction={direction}
        size={size}
        status={status}
        type={type}
        progressDot={progressDot}
        responsive={responsive}
        items={buildSteps()}
      />

      {buildContent()}
      {buildNavigation()}
    </motion.div>
  );
};

// VerticalStepper component
interface VerticalStepperProps extends Omit<StepperProps, 'direction'> {
  labelPlacement?: 'horizontal' | 'vertical';
}

export const VerticalStepper: React.FC<VerticalStepperProps> = ({
  labelPlacement = 'horizontal',
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        gap: 40,
      }}
    >
      <div style={{ flex: 1 }}>
        <Steps
          current={props.current || 0}
          direction="vertical"
          size={props.size || 'default'}
          labelPlacement={labelPlacement}
          status={props.status}
          items={props.items.map((item, index) => ({
            key: item.key,
            title: item.title,
            description: item.description,
            icon: item.icon,
            status: index <= (props.current || 0) ? 'finish' : 'wait',
          }))}
        />
      </div>
      
      <div style={{ flex: 2 }}>
        {props.items[props.current || 0]?.content}
        
        {props.showNavigation && (
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Space>
              {(props.current || 0) > 0 && (
                <Button onClick={() => props.onChange && props.onChange((props.current || 0) - 1)}>
                  {props.prevText || 'Previous'}
                </Button>
              )}
              
              {(props.current || 0) < props.items.length - 1 ? (
                <Button
                  type="primary"
                  onClick={() => props.onChange && props.onChange((props.current || 0) + 1)}
                >
                  {props.nextText || 'Next'}
                </Button>
              ) : (
                <Button
                  type="primary"
                  onClick={props.onFinish}
                >
                  {props.finishText || 'Finish'}
                </Button>
              )}
            </Space>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// ProgressStepper component (stepper with progress bar)
interface ProgressStepperProps extends StepperProps {
  showProgress?: boolean;
  progressColor?: string;
  progressBackground?: string;
}

export const ProgressStepper: React.FC<ProgressStepperProps> = ({
  showProgress = true,
  progressColor = '#1890ff',
  progressBackground = '#f0f0f0',
  ...props
}) => {
  const current = props.current || 0;
  const total = props.items.length;
  const progress = (current / (total - 1)) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={props.style}
      className={props.className}
    >
      {showProgress && (
        <div
          style={{
            height: 4,
            background: progressBackground,
            borderRadius: 2,
            overflow: 'hidden',
            marginBottom: 24,
          }}
        >
          <motion.div
            style={{
              height: '100%',
              background: progressColor,
              borderRadius: 2,
            }}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      )}

      <Stepper {...props} showProgress={false} />
    </motion.div>
  );
};

// TimelineStepper component (stepper with timeline appearance)
interface TimelineStepperProps extends StepperProps {
  lineStyle?: React.CSSProperties;
  dotStyle?: React.CSSProperties;
}

export const TimelineStepper: React.FC<TimelineStepperProps> = ({
  lineStyle = {},
  dotStyle = {},
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={props.style}
      className={props.className}
    >
      <Steps
        current={props.current || 0}
        direction={props.direction || 'horizontal'}
        size={props.size || 'default'}
        status={props.status}
        progressDot={(icon, status) => (
          <div
            style={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              background: status === 'finish' ? '#52c41a' : 
                         status === 'process' ? '#1890ff' : 
                         status === 'error' ? '#f5222d' : '#d9d9d9',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              ...dotStyle,
            }}
          >
            {icon}
          </div>
        )}
        items={props.items.map((item, index) => ({
          key: item.key,
          title: item.title,
          description: item.description,
          icon: item.icon,
          status: index <= (props.current || 0) ? 'finish' : 'wait',
        }))}
      />

      {props.showContent && props.items[props.current || 0]?.content && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          style={{
            marginTop: 24,
            ...props.contentStyle,
          }}
        >
          {props.items[props.current || 0].content}
        </motion.div>
      )}

      {props.showNavigation && (
        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Space>
            {(props.current || 0) > 0 && (
              <Button onClick={() => props.onChange && props.onChange((props.current || 0) - 1)}>
                {props.prevText || 'Previous'}
              </Button>
            )}
            
            {(props.current || 0) < props.items.length - 1 ? (
              <Button
                type="primary"
                onClick={() => props.onChange && props.onChange((props.current || 0) + 1)}
              >
                {props.nextText || 'Next'}
              </Button>
            ) : (
              <Button
                type="primary"
                onClick={props.onFinish}
              >
                {props.finishText || 'Finish'}
              </Button>
            )}
          </Space>
        </div>
      )}
    </motion.div>
  );
};

// OnboardingStepper component (stepper for onboarding flows)
interface OnboardingStepperProps extends StepperProps {
  title?: string;
  description?: string;
  finishButtonText?: string;
  onClose?: () => void;
}

export const OnboardingStepper: React.FC<OnboardingStepperProps> = ({
  title,
  description,
  finishButtonText = 'Get Started',
  onClose,
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        maxWidth: 800,
        margin: '0 auto',
        ...props.style,
      }}
      className={props.className}
    >
      {title && (
        <Title level={2} style={{ textAlign: 'center', marginBottom: 8 }}>
          {title}
        </Title>
      )}

      {description && (
        <Text type="secondary" style={{ textAlign: 'center', display: 'block', marginBottom: 24 }}>
          {description}
        </Text>
      )}

      <ProgressStepper
        {...props}
        finishText={finishButtonText}
      />

      {onClose && (
        <div style={{ textAlign: 'center', marginTop: 24 }}>
          <Button onClick={onClose}>
            Skip Tutorial
          </Button>
        </div>
      )}
    </motion.div>
  );
};

export default Stepper;
