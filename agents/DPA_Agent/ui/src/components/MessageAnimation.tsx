import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TypewriterEffectProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  className?: string;
}

export const TypewriterEffect: React.FC<TypewriterEffectProps> = ({
  text,
  speed = 30,
  onComplete,
  className = ''
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (currentIndex < text.length) {
      intervalRef.current = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
    } else if (onComplete) {
      onComplete();
    }

    return () => {
      if (intervalRef.current) {
        clearTimeout(intervalRef.current);
      }
    };
  }, [currentIndex, text, speed, onComplete]);

  return (
    <span className={className}>
      {displayedText}
      {currentIndex < text.length && (
        <motion.span
          className="inline-block w-0.5 h-5 bg-gray-600 ml-0.5"
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
        />
      )}
    </span>
  );
};

interface MessageAnimationProps {
  children: React.ReactNode;
  isNew?: boolean;
  type?: 'user' | 'assistant' | 'tool' | 'system';
}

export const MessageAnimation: React.FC<MessageAnimationProps> = ({
  children,
  isNew = false,
  type = 'user'
}) => {
  const messageVariants = {
    initial: {
      opacity: 0,
      y: 20,
      scale: 0.95,
    },
    animate: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.3,
        ease: [0.22, 1, 0.36, 1], // Apple-style easing
      }
    },
    exit: {
      opacity: 0,
      scale: 0.95,
      transition: {
        duration: 0.2
      }
    }
  };

  const pulseVariants = {
    initial: { scale: 1 },
    pulse: {
      scale: [1, 1.02, 1],
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    }
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={isNew ? 'new' : 'old'}
        variants={messageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="message-animation-wrapper"
      >
        {isNew && type === 'assistant' && (
          <motion.div
            variants={pulseVariants}
            initial="initial"
            animate="pulse"
          >
            {children}
          </motion.div>
        )}
        {(!isNew || type !== 'assistant') && children}
      </motion.div>
    </AnimatePresence>
  );
};

interface StreamingTextProps {
  text: string;
  isStreaming: boolean;
  className?: string;
}

export const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  isStreaming,
  className = ''
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const textRef = useRef(text);

  useEffect(() => {
    if (text !== textRef.current) {
      const newChars = text.slice(textRef.current.length);
      if (newChars.length > 0) {
        setDisplayedText(prev => prev + newChars);
      }
      textRef.current = text;
    }
  }, [text]);

  useEffect(() => {
    setDisplayedText(text);
  }, []);

  return (
    <span className={className}>
      {displayedText}
      {isStreaming && (
        <motion.span
          className="inline-block w-2 h-4 bg-blue-500 ml-0.5 rounded-sm"
          animate={{ opacity: [1, 0, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </span>
  );
};

// Loading dots animation
export const LoadingDots: React.FC = () => {
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-gray-400 rounded-full"
          animate={{
            y: [0, -8, 0],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.1,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
};