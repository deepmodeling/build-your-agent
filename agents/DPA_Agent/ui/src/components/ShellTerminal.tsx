import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Terminal, X, Maximize2, Minimize2 } from 'lucide-react';

interface ShellTerminalProps {
  isOpen: boolean;
  onClose: () => void;
  onExecuteCommand: (command: string) => void;
  output: Array<{ type: 'command' | 'output' | 'error'; content: string; timestamp: Date }>;
}

export const ShellTerminal: React.FC<ShellTerminalProps> = ({
  isOpen,
  onClose,
  onExecuteCommand,
  output
}) => {
  const [input, setInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isMaximized, setIsMaximized] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(384); // 默认高度 384px (h-96)
  const [iesizing, setIesizing] = useState(false);
  const outputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const startHeightRef = useRef(0);
  const startYRef = useRef(0);

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [output]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && input.trim()) {
      executeCommand(input.trim());
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      navigateHistory('up');
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      navigateHistory('down');
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      handleClear();
    } else if (e.key === 'c' && e.ctrlKey) {
      e.preventDefault();
      setInput('');
    }
  };

  const executeCommand = (command: string) => {
    if (command === 'clear' || command === 'cls') {
      handleClear();
      return;
    }

    setCommandHistory(prev => [...prev, command]);
    setHistoryIndex(-1);
    onExecuteCommand(command);
    setInput('');
  };

  const navigateHistory = (direction: 'up' | 'down') => {
    if (commandHistory.length === 0) return;

    let newIndex = historyIndex;
    if (direction === 'up') {
      newIndex = historyIndex === -1 ? commandHistory.length - 1 : Math.max(0, historyIndex - 1);
    } else {
      newIndex = historyIndex === commandHistory.length - 1 ? -1 : historyIndex + 1;
    }

    setHistoryIndex(newIndex);
    setInput(newIndex === -1 ? '' : commandHistory[newIndex]);
  };

  const handleClear = () => {
    onExecuteCommand('__clear__');
  };

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIesizing(true);
    startYRef.current = e.clientY;
    startHeightRef.current = terminalHeight;
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!iesizing) return;
      
      const deltaY = startYRef.current - e.clientY;
      const newHeight = Math.max(200, Math.min(window.innerHeight - 100, startHeightRef.current + deltaY));
      setTerminalHeight(newHeight);
    };

    const handleMouseUp = () => {
      setIesizing(false);
    };

    if (iesizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'row-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [iesizing]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-700 transition-width duration-300"
      style={{ height: isMaximized ? '100vh' : `${terminalHeight}px` }}
    >
      {/* Resize Handle */}
      <div
        className={`absolute top-0 left-0 right-0 h-1 cursor-row-resize hover:bg-blue-500 transition-colors ${
          iesizing ? 'bg-blue-500' : 'bg-transparent'
        }`}
        onMouseDown={handleResizeStart}
      >
        <div className="absolute inset-0 -top-1 -bottom-1" />
      </div>
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-green-400" />
          <span className="text-sm font-mono text-gray-300">Terminal</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMaximized(!isMaximized)}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
            title={isMaximized ? "Restore" : "Maximize"}
          >
            {isMaximized ? (
              <Minimize2 className="w-4 h-4 text-gray-400" />
            ) : (
              <Maximize2 className="w-4 h-4 text-gray-400" />
            )}
          </button>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
            title="Close"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      <div className="flex flex-col h-full">
        <div 
          ref={outputRef}
          className="flex-1 overflow-y-auto p-4 font-mono text-sm terminal-output"
        >
          {output.map((line, index) => (
            <div key={index} className="mb-1">
              {line.type === 'command' && (
                <div className="flex items-start">
                  <span className="text-green-400 mr-2">$</span>
                  <span className="text-gray-100">{line.content}</span>
                </div>
              )}
              {line.type === 'output' && (
                <pre className="text-gray-300 whitespace-pre-wrap pl-4">{line.content}</pre>
              )}
              {line.type === 'error' && (
                <pre className="text-red-400 whitespace-pre-wrap pl-4">{line.content}</pre>
              )}
            </div>
          ))}
        </div>

        <div className="border-t border-gray-700 px-4 py-4">
          <div className="flex items-center">
            <span className="text-green-400 mr-2 font-mono">$</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent text-gray-100 font-mono text-base outline-none placeholder-gray-500 py-1"
              placeholder="Type a command..."
              autoComplete="off"
              spellCheck={false}
            />
          </div>
          <div className="mt-2 text-xs text-gray-500 font-mono">
            Press ↑/↓ for history • Ctrl+C to cancel • Ctrl+L to clear
          </div>
        </div>
      </div>
    </div>
  );
};