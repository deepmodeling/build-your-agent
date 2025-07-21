import React, { useState, useRef, useEffect, useCallback } from 'react';

interface ResizablePanelProps {
  direction: 'horizontal' | 'vertical';
  minSize?: number;
  maxSize?: number;
  defaultSize?: number;
  onResize?: (size: number) => void;
  children: React.ReactNode;
  className?: string;
  resizeBarClassName?: string;
  resizeBarPosition?: 'start' | 'end';
}

export const ResizablePanel: React.FC<ResizablePanelProps> = ({
  direction,
  minSize = 100,
  maxSize = 800,
  defaultSize = 300,
  onResize,
  children,
  className = '',
  resizeBarClassName = '',
  resizeBarPosition = 'end'
}) => {
  const [size, setSize] = useState(defaultSize);
  const [iesizing, setIesizing] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const startPoef = useRef(0);
  const startSizeRef = useRef(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIesizing(true);
    startPoef.current = direction === 'horizontal' ? e.clientX : e.clientY;
    startSizeRef.current = size;
  }, [direction, size]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!iesizing) return;

    const currentPos = direction === 'horizontal' ? e.clientX : e.clientY;
    let diff = currentPos - startPoef.current;
    
    // Reverse the diff for 'start' position
    if (resizeBarPosition === 'start') {
      diff = -diff;
    }
    
    const newSize = Math.max(minSize, Math.min(maxSize, startSizeRef.current + diff));
    
    setSize(newSize);
    onResize?.(newSize);
  }, [iesizing, direction, minSize, maxSize, onResize, resizeBarPosition]);

  const handleMouseUp = useCallback(() => {
    setIesizing(false);
  }, []);

  useEffect(() => {
    if (iesizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = direction === 'horizontal' ? 'col-resize' : 'row-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [iesizing, handleMouseMove, handleMouseUp, direction]);

  const resizeBarStyle = direction === 'horizontal' 
    ? `absolute top-0 ${resizeBarPosition === 'end' ? 'right-0' : 'left-0'} w-2 h-full cursor-col-resize hover:bg-blue-500 transition-colors group`
    : `absolute ${resizeBarPosition === 'end' ? 'bottom-0' : 'top-0'} left-0 w-full h-2 cursor-row-resize hover:bg-blue-500 transition-colors group`;

  const panelStyle = direction === 'horizontal'
    ? { width: `${size}px` }
    : { height: `${size}px` };

  return (
    <div 
      ref={panelRef}
      className={`relative ${className}`}
      style={panelStyle}
    >
      {children}
      <div
        className={`${resizeBarStyle} ${resizeBarClassName} ${
          iesizing ? 'bg-blue-500' : 'bg-transparent hover:bg-gray-300 dark:hover:bg-gray-600'
        }`}
        onMouseDown={handleMouseDown}
      >
        {/* Visual indicator */}
        <div className={`absolute ${
          direction === 'horizontal' 
            ? 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-0.5 h-8' 
            : 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-0.5'
        } bg-gray-400 dark:bg-gray-500 group-hover:bg-blue-500 transition-colors`} />
        {/* Larger hit area */}
        <div className={`absolute inset-0 ${
          direction === 'horizontal' ? '-left-2 -right-2' : '-top-2 -bottom-2'
        }`} />
      </div>
    </div>
  );
};