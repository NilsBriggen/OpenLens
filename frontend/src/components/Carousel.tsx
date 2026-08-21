/**
 * Carousel Component for OpenLens
 * 
 * A customizable carousel component for displaying slides or cards
 */

import React, { useState, useRef, useEffect } from 'react';
import { Carousel as AntCarousel, Button, Space, Typography, Card } from 'antd';
import { LeftOutlined, RightOutlined, PauseOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Title, Text } = Typography;

interface CarouselItem {
  key?: string;
  title?: string;
  description?: string;
  image?: string;
  color?: string;
  content?: React.ReactNode;
  [key: string]: any;
}

interface CarouselProps {
  items: CarouselItem[];
  autoPlay?: boolean;
  autoPlaySpeed?: number;
  dots?: boolean;
  arrows?: boolean;
  fade?: boolean;
  vertical?: boolean;
  infinite?: boolean;
  centerMode?: boolean;
  centerPadding?: string;
  slidesToShow?: number;
  slidesToScroll?: number;
  responsive?: Array<{
    breakpoint: number;
    settings: {
      slidesToShow?: number;
      slidesToScroll?: number;
      infinite?: boolean;
      dots?: boolean;
    };
  }>;
  beforeChange?: (from: number, to: number) => void;
  afterChange?: (current: number) => void;
  style?: React.CSSProperties;
  className?: string;
  height?: number | string;
  showIndicators?: boolean;
  indicatorType?: 'dots' | 'numbers' | 'progress';
}

const Carousel: React.FC<CarouselProps> = ({
  items = [],
  autoPlay = true,
  autoPlaySpeed = 3000,
  dots = true,
  arrows = true,
  fade = false,
  vertical = false,
  infinite = true,
  centerMode = false,
  centerPadding = '50px',
  slidesToShow = 1,
  slidesToScroll = 1,
  responsive,
  beforeChange,
  afterChange,
  style = {},
  className = '',
  height,
  showIndicators = true,
  indicatorType = 'dots',
}) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const carouselRef = useRef<any>(null);

  // Handle before change
  const handleBeforeChange = (from: number, to: number) => {
    setCurrentSlide(to);
    if (beforeChange) {
      beforeChange(from, to);
    }
  };

  // Handle after change
  const handleAfterChange = (current: number) => {
    setCurrentSlide(current);
    if (afterChange) {
      afterChange(current);
    }
  };

  // Handle play/pause
  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
    if (carouselRef.current) {
      if (isPlaying) {
        carouselRef.current.goTo(currentSlide, false);
      } else {
        carouselRef.current.goTo(currentSlide, true);
      }
    }
  };

  // Handle next
  const handleNext = () => {
    if (carouselRef.current) {
      carouselRef.current.next();
    }
  };

  // Handle prev
  const handlePrev = () => {
    if (carouselRef.current) {
      carouselRef.current.prev();
    }
  };

  // Handle indicator click
  const handleIndicatorClick = (index: number) => {
    if (carouselRef.current) {
      carouselRef.current.goTo(index);
    }
  };

  // Get responsive settings
  const getResponsiveSettings = () => {
    if (!responsive) return undefined;
    
    return responsive.map(setting => ({
      breakpoint: setting.breakpoint,
      settings: {
        slidesToShow: setting.settings.slidesToShow || slidesToShow,
        slidesToScroll: setting.settings.slidesToScroll || slidesToScroll,
        infinite: setting.settings.infinite !== undefined ? setting.settings.infinite : infinite,
        dots: setting.settings.dots !== undefined ? setting.settings.dots : dots,
      },
    }));
  };

  // Render indicators
  const renderIndicators = () => {
    if (!showIndicators) return null;

    switch (indicatorType) {
      case 'numbers':
        return (
          <Space style={{ justifyContent: 'center', marginTop: 16 }}>
            {items.map((_, index) => (
              <Button
                key={index}
                type={currentSlide === index ? 'primary' : 'text'}
                onClick={() => handleIndicatorClick(index)}
                size="small"
                style={{ width: 32 }}
              >
                {index + 1}
              </Button>
            ))}
          </Space>
        );

      case 'progress':
        return (
          <div style={{ marginTop: 16 }}>
            <div
              style={{
                height: 4,
                background: '#f0f0f0',
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              <motion.div
                style={{
                  height: '100%',
                  background: '#1890ff',
                  borderRadius: 2,
                }}
                initial={{ width: 0 }}
                animate={{ width: `${((currentSlide + 1) / items.length) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <Space style={{ justifyContent: 'space-between', marginTop: 8 }}>
              {items.map((_, index) => (
                <Button
                  key={index}
                  type="text"
                  onClick={() => handleIndicatorClick(index)}
                  size="small"
                  style={{
                    color: currentSlide === index ? '#1890ff' : '#666',
                  }}
                >
                  {index + 1}
                </Button>
              ))}
            </Space>
          </div>
        );

      case 'dots':
      default:
        return (
          <Space style={{ justifyContent: 'center', marginTop: 16 }}>
            {items.map((_, index) => (
              <Button
                key={index}
                type={currentSlide === index ? 'primary' : 'text'}
                onClick={() => handleIndicatorClick(index)}
                size="small"
                shape="circle"
                style={{ width: 12, height: 12, padding: 0 }}
              />
            ))}
          </Space>
        );
    }
  };

  // Get carousel height
  const getHeight = () => {
    if (height) return height;
    if (vertical) return 400;
    return 'auto';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'relative',
        ...style,
      }}
      className={className}
    >
      <AntCarousel
        ref={carouselRef}
        autoplay={autoPlay && isPlaying}
        autoplaySpeed={autoPlaySpeed}
        dots={false}
        arrows={false}
        fade={fade}
        vertical={vertical}
        infinite={infinite}
        centerMode={centerMode}
        centerPadding={centerPadding}
        slidesToShow={slidesToShow}
        slidesToScroll={slidesToScroll}
        responsive={getResponsiveSettings()}
        beforeChange={handleBeforeChange}
        afterChange={handleAfterChange}
        style={{
          height: getHeight(),
        }}
      >
        {items.map((item, index) => (
          <motion.div
            key={item.key || index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3 }}
            style={{
              height: getHeight(),
              padding: 16,
              position: 'relative',
            }}
          >
            {item.content || (
              <Card
                title={item.title}
                style={{
                  height: '100%',
                  background: item.color || 'var(--card-bg)',
                  border: 'none',
                }}
                bodyStyle={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  height: 'calc(100% - 48px)',
                }}
              >
                {item.image && (
                  <img
                    src={item.image}
                    alt={item.title}
                    style={{
                      maxWidth: '100%',
                      maxHeight: '100%',
                      objectFit: 'contain',
                    }}
                  />
                )}
                
                {item.description && (
                  <Text type="secondary" style={{ marginTop: 16, textAlign: 'center' }}>
                    {item.description}
                  </Text>
                )}
              </Card>
            )}
          </motion.div>
        ))}
      </AntCarousel>

      {/* Arrows */}
      {arrows && !vertical && (
        <>
          <Button
            type="text"
            icon={<LeftOutlined />}
            onClick={handlePrev}
            size="large"
            style={{
              position: 'absolute',
              left: 16,
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 1,
              background: 'rgba(0, 0, 0, 0.5)',
              color: '#fff',
              border: 'none',
              borderRadius: '50%',
              width: 40,
              height: 40,
            }}
          />
          
          <Button
            type="text"
            icon={<RightOutlined />}
            onClick={handleNext}
            size="large"
            style={{
              position: 'absolute',
              right: 16,
              top: '50%',
              transform: 'translateY(-50%)',
              zIndex: 1,
              background: 'rgba(0, 0, 0, 0.5)',
              color: '#fff',
              border: 'none',
              borderRadius: '50%',
              width: 40,
              height: 40,
            }}
          />
        </>
      )}

      {/* Play/Pause button */}
      {autoPlay && (
        <Button
          type="text"
          icon={isPlaying ? <PauseOutlined /> : <PlayCircleOutlined />}
          onClick={handlePlayPause}
          size="large"
          style={{
            position: 'absolute',
            bottom: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1,
            background: 'rgba(0, 0, 0, 0.5)',
            color: '#fff',
            border: 'none',
            borderRadius: '50%',
            width: 40,
            height: 40,
          }}
        />
      )}

      {/* Indicators */}
      {renderIndicators()}
    </motion.div>
  );
};

// CardCarousel component (carousel with cards)
interface CardCarouselProps extends Omit<CarouselProps, 'items' | 'height'> {
  items: CarouselItem[];
  cardHeight?: number | string;
  cardWidth?: number | string;
  gutter?: number;
}

export const CardCarousel: React.FC<CardCarouselProps> = ({
  items = [],
  cardHeight = 300,
  cardWidth,
  gutter = 16,
  ...props
}) => {
  // Get slides to show
  const slidesToShow = props.slidesToShow || 3;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={props.style}
      className={props.className}
    >
      <Carousel
        {...props}
        height={cardHeight}
        slidesToShow={slidesToShow}
        responsive={[
          {
            breakpoint: 1024,
            settings: {
              slidesToShow: Math.min(3, slidesToShow),
            },
          },
          {
            breakpoint: 768,
            settings: {
              slidesToShow: Math.min(2, slidesToShow),
            },
          },
          {
            breakpoint: 480,
            settings: {
              slidesToShow: 1,
            },
          },
        ]}
      >
        {items.map((item, index) => (
          <motion.div
            key={item.key || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            style={{
              padding: `0 ${gutter / 2}px`,
              height: cardHeight,
            }}
          >
            <Card
              title={item.title}
              style={{
                height: '100%',
                background: item.color || 'var(--card-bg)',
                borderRadius: 12,
              }}
              bodyStyle={{
                display: 'flex',
                flexDirection: 'column',
                height: `calc(100% - 48px)`,
              }}
            >
              {item.image && (
                <img
                  src={item.image}
                  alt={item.title}
                  style={{
                    width: '100%',
                    height: '60%',
                    objectFit: 'cover',
                    borderTopLeftRadius: 12,
                    borderTopRightRadius: 12,
                  }}
                />
              )}
              
              <div style={{ flex: 1, padding: 16 }}>
                {item.description && (
                  <Text type="secondary" style={{ fontSize: 14 }}>
                    {item.description}
                  </Text>
                )}
                
                {item.content && (
                  <div style={{ marginTop: 16 }}>
                    {item.content}
                  </div>
                )}
              </div>
            </Card>
          </motion.div>
        ))}
      </Carousel>
    </motion.div>
  );
};

// ImageCarousel component (carousel for images)
interface ImageCarouselProps extends Omit<CarouselProps, 'items'> {
  images: string[];
  thumbnails?: boolean;
  thumbnailWidth?: number;
  thumbnailHeight?: number;
  showCaptions?: boolean;
  captions?: string[];
}

export const ImageCarousel: React.FC<ImageCarouselProps> = ({
  images = [],
  thumbnails = false,
  thumbnailWidth = 60,
  thumbnailHeight = 40,
  showCaptions = false,
  captions = [],
  ...props
}) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  // Handle after change
  const handleAfterChange = (current: number) => {
    setCurrentSlide(current);
    if (props.afterChange) {
      props.afterChange(current);
    }
  };

  // Handle thumbnail click
  const handleThumbnailClick = (index: number) => {
    if (props.carouselRef?.current) {
      props.carouselRef.current.goTo(index);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={props.style}
      className={props.className}
    >
      <Carousel
        {...props}
        afterChange={handleAfterChange}
        style={{
          height: props.height || 400,
        }}
      >
        {images.map((image, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.3 }}
            style={{
              height: props.height || 400,
              position: 'relative',
            }}
          >
            <img
              src={image}
              alt={captions[index] || `Image ${index + 1}`}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            
            {showCaptions && captions[index] && (
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  background: 'rgba(0, 0, 0, 0.5)',
                  color: '#fff',
                  padding: 16,
                }}
              >
                <Text style={{ color: '#fff' }}>
                  {captions[index]}
                </Text>
              </div>
            )}
          </motion.div>
        ))}
      </Carousel>

      {/* Thumbnails */}
      {thumbnails && images.length > 1 && (
        <Space style={{ marginTop: 16, justifyContent: 'center' }}>
          {images.map((image, index) => (
            <img
              key={index}
              src={image}
              alt={`Thumbnail ${index + 1}`}
              onClick={() => handleThumbnailClick(index)}
              style={{
                width: thumbnailWidth,
                height: thumbnailHeight,
                objectFit: 'cover',
                border: currentSlide === index ? '2px solid #1890ff' : '2px solid transparent',
                borderRadius: 4,
                cursor: 'pointer',
              }}
            />
          ))}
        </Space>
      )}
    </motion.div>
  );
};

// TestimonialCarousel component (carousel for testimonials)
interface Testimonial {
  key?: string;
  quote: string;
  author: string;
  title?: string;
  avatar?: string;
  company?: string;
  rating?: number;
}

interface TestimonialCarouselProps extends Omit<CarouselProps, 'items' | 'height'> {
  testimonials: Testimonial[];
  showRating?: boolean;
  ratingColor?: string;
}

export const TestimonialCarousel: React.FC<TestimonialCarouselProps> = ({
  testimonials = [],
  showRating = true,
  ratingColor = '#ffc600',
  ...props
}) => {
  // Render rating
  const renderRating = (rating: number = 5) => {
    return (
      <Space>
        {Array.from({ length: 5 }).map((_, index) => (
          <span
            key={index}
            style={{
              fontSize: 16,
              color: index < rating ? ratingColor : '#d9d9d9',
            }}
          >
            ★
          </span>
        ))}
      </Space>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={props.style}
      className={props.className}
    >
      <Carousel
        {...props}
        height={300}
      >
        {testimonials.map((testimonial, index) => (
          <motion.div
            key={testimonial.key || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            style={{
              padding: 24,
              textAlign: 'center',
            }}
          >
            <Card
              style={{
                height: '100%',
                border: 'none',
                background: 'transparent',
              }}
              bodyStyle={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100%',
              }}
            >
              {showRating && testimonial.rating && (
                <div style={{ marginBottom: 16 }}>
                  {renderRating(testimonial.rating)}
                </div>
              )}

              <Title level={4} style={{ marginBottom: 16 }}>
                {testimonial.quote}
              </Title>

              <Space direction="vertical" align="center">
                {testimonial.avatar && (
                  <img
                    src={testimonial.avatar}
                    alt={testimonial.author}
                    style={{
                      width: 64,
                      height: 64,
                      borderRadius: '50%',
                      objectFit: 'cover',
                    }}
                  />
                )}

                <Space direction="vertical" align="center">
                  <Title level={5} style={{ margin: 0 }}>
                    {testimonial.author}
                  </Title>
                  
                  {testimonial.title && (
                    <Text type="secondary">{testimonial.title}</Text>
                  )}
                  
                  {testimonial.company && (
                    <Text type="secondary">{testimonial.company}</Text>
                  )}
                </Space>
              </Space>
            </Card>
          </motion.div>
        ))}
      </Carousel>
    </motion.div>
  );
};

// HeroCarousel component (full-width hero carousel)
interface HeroCarouselProps extends Omit<CarouselProps, 'items' | 'height'> {
  items: CarouselItem[];
  overlay?: boolean;
  overlayColor?: string;
  textAlign?: 'left' | 'center' | 'right';
}

export const HeroCarousel: React.FC<HeroCarouselProps> = ({
  items = [],
  overlay = true,
  overlayColor = 'rgba(0, 0, 0, 0.5)',
  textAlign = 'center',
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 12,
        ...props.style,
      }}
      className={props.className}
    >
      <Carousel
        {...props}
        dots={props.dots !== undefined ? props.dots : true}
        arrows={props.arrows !== undefined ? props.arrows : true}
        style={{
          height: props.height || 500,
        }}
      >
        {items.map((item, index) => (
          <motion.div
            key={item.key || index}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.5 }}
            style={{
              height: props.height || 500,
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {item.image && (
              <img
                src={item.image}
                alt={item.title}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
            )}

            {overlay && (
              <div
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: overlayColor,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: textAlign,
                  padding: 40,
                  color: '#fff',
                }}
              >
                {item.title && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                  >
                    <Title level={2} style={{ color: '#fff', margin: 0 }}>
                      {item.title}
                    </Title>
                  </motion.div>
                )}

                {item.description && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                    style={{ maxWidth: 600 }}
                  >
                    <Text style={{ color: '#fff', fontSize: 16 }}>
                      {item.description}
                    </Text>
                  </motion.div>
                )}

                {item.content && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.6 }}
                    style={{ marginTop: 24 }}
                  >
                    {item.content}
                  </motion.div>
                )}
              </div>
            )}
          </motion.div>
        ))}
      </Carousel>
    </motion.div>
  );
};

// VerticalCarousel component (vertical carousel)
interface VerticalCarouselProps extends Omit<CarouselProps, 'vertical'> {
  items: CarouselItem[];
  itemHeight?: number | string;
}

export const VerticalCarousel: React.FC<VerticalCarouselProps> = ({
  items = [],
  itemHeight = 200,
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        height: props.height || 400,
        ...props.style,
      }}
      className={props.className}
    >
      <Carousel
        {...props}
        vertical={true}
        style={{
          height: '100%',
        }}
      >
        {items.map((item, index) => (
          <motion.div
            key={item.key || index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            style={{
              height: itemHeight,
              padding: 16,
            }}
          >
            <Card
              title={item.title}
              style={{
                height: '100%',
                background: item.color || 'var(--card-bg)',
                borderRadius: 8,
              }}
              bodyStyle={{
                display: 'flex',
                alignItems: 'center',
                height: `calc(100% - 48px)`,
              }}
            >
              {item.image && (
                <img
                  src={item.image}
                  alt={item.title}
                  style={{
                    width: 100,
                    height: 100,
                    objectFit: 'cover',
                    borderRadius: 8,
                    marginRight: 16,
                  }}
                />
              )}
              
              <div>
                {item.description && (
                  <Text type="secondary">{item.description}</Text>
                )}
                
                {item.content && (
                  <div style={{ marginTop: 16 }}>
                    {item.content}
                  </div>
                )}
              </div>
            </Card>
          </motion.div>
        ))}
      </Carousel>
    </motion.div>
  );
};

export default Carousel;
