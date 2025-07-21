import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { createCodeComponent } from './EnhancedCodeBlock';

interface MemoizedMarkdownProps {
  children: string;
  className?: string;
}

export const MemoizedMarkdown = React.memo<MemoizedMarkdownProps>(({ children, className }) => {
  return (
    <ReactMarkdown
      className={className}
      remarkPlugins={[remarkGfm]}
      components={{
        code: createCodeComponent(),
        a({ node, children, href, ...props }: any) {
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
              {...props}
            >
              {children}
            </a>
          );
        },
        p({ children }: any) {
          return <p>{children}</p>;
        }
      }}
    >
      {children}
    </ReactMarkdown>
  );
}, (prevProps, nextProps) => {
  // 只有当内容真正改变时才重新渲染
  return prevProps.children === nextProps.children;
});

MemoizedMarkdown.displayName = 'MemoizedMarkdown';