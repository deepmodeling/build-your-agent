import React, { useState, useCallback } from 'react'
import { ChevronRight, ChevronDown, File, Folder, FileText, Loader2, X, Copy, Check, Maximize2, Minimize2 } from 'lucide-react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'

const API_BASE_URL = ''

interface FileNode {
  name: string
  path: string
  type: 'file' | 'directory'
  children?: FileNode[]
  isExpanded?: boolean
  size?: number
  modified?: string
}

interface FileExplorerProps {
  isOpen: boolean
  onClose: () => void
  fileTree: FileNode[]
  onFileTreeUpdate: (tree: FileNode[]) => void
  onLoadFileTree: () => void
}

const FileExplorer: React.FC<FileExplorerProps> = ({
  isOpen,
  onClose,
  fileTree,
  onFileTreeUpdate,
  onLoadFileTree
}) => {
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [selectedFileContent, setSelectedFileContent] = useState<string | null>(null)
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null)
  const [loadingFiles, setLoadingFiles] = useState<Set<string>>(new Set())
  const [fileContentCache, setFileContentCache] = useState<Map<string, string>>(new Map())
  const [isFileContentExpanded, setIsFileContentExpanded] = useState(false)
  const [copiedCode, setCopiedCode] = useState<string | null>(null)
  // 文件树宽度固定，不再需要调整
  const fileTreeWidth = 280 // 固定宽度

  const toggleDirectory = useCallback(async (path: string) => {
    onFileTreeUpdate(fileTree.map(node => {
      const toggleNode = (n: FileNode): FileNode => {
        if (n.path === path) {
          return { ...n, isExpanded: !n.isExpanded }
        }
        if (n.children) {
          return { ...n, children: n.children.map(toggleNode) }
        }
        return n
      }
      return toggleNode(node)
    }))

    const findNode = (nodes: FileNode[], targetPath: string): FileNode | null => {
      for (const node of nodes) {
        if (node.path === targetPath) return node
        if (node.children) {
          const found = findNode(node.children, targetPath)
          if (found) return found
        }
      }
      return null
    }

    const node = findNode(fileTree, path)
    if (node && node.type === 'directory' && !node.children) {
      await loadDirectoryChildren(path)
    }
  }, [fileTree, onFileTreeUpdate])

  const loadDirectoryChildren = async (dirPath: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/files/tree`, {
        params: { path: dirPath }
      })
      
      const children = response.data
      
      onFileTreeUpdate(fileTree.map(node => {
        const updateWithChildren = (n: FileNode): FileNode => {
          if (n.path === dirPath) {
            return { ...n, children }
          }
          if (n.children) {
            return { ...n, children: n.children.map(updateWithChildren) }
          }
          return n
        }
        return updateWithChildren(node)
      }))
    } catch (error) {
      console.error('Error loading directory children:', error)
    }
  }

  const selectFile = useCallback(async (path: string, node: FileNode) => {
    if (node.type === 'file') {
      setSelectedFilePath(path)
      
      if (fileContentCache.has(path)) {
        setSelectedFileContent(fileContentCache.get(path)!)
        return
      }
      
      if (loadingFiles.has(path)) return
      
      setLoadingFiles(prev => new Set(prev).add(path))
      
      try {
        const response = await axios.get(`${API_BASE_URL}/api/files/${path}`, {
          responseType: 'text'
        })
        
        setFileContentCache(prev => new Map(prev).set(path, response.data))
        setSelectedFileContent(response.data)
      } catch (error) {
        console.error('Error loading file:', error)
        const errorMsg = '加载文件失败: ' + (error as any).message
        setSelectedFileContent(errorMsg)
      } finally {
        setLoadingFiles(prev => {
          const newSet = new Set(prev)
          newSet.delete(path)
          return newSet
        })
      }
    }
  }, [fileContentCache, loadingFiles])

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    
    const colorMap: { [key: string]: string } = {
      'json': 'text-orange-500',
      'md': 'text-purple-500',
      'txt': 'text-blue-500',
      'csv': 'text-green-500',
      'py': 'text-yellow-500',
      'js': 'text-yellow-400',
      'ts': 'text-blue-600',
      'log': 'text-gray-500',
    }
    
    const color = colorMap[ext || ''] || 'text-gray-400'
    
    if (['md', 'txt', 'json', 'csv', 'log'].includes(ext || '')) {
      return <FileText className={`w-4 h-4 ${color}`} />
    }
    
    return <File className={`w-4 h-4 ${color}`} />
  }

  const handleCopyCode = useCallback((code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      setCopiedCode(code)
      setTimeout(() => setCopiedCode(null), 2000)
    })
  }, [])

  const renderFileContent = (content: string, filePath: string) => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    
    if (ext === 'json') {
      try {
        const jsonData = JSON.parse(content)
        return (
          <SyntaxHighlighter
            language="json"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              borderRadius: '0.5rem',
              fontSize: '0.875rem',
              lineHeight: '1.5'
            }}
            wrapLines={true}
            wrapLongLines={true}
          >
            {JSON.stringify(jsonData, null, 2)}
          </SyntaxHighlighter>
        )
      } catch {
        // Fall through to default
      }
    }
    
    if (ext === 'md') {
      return (
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              pre({ node, children, ...props }: any) {
                return (
                  <pre className="overflow-x-auto bg-gray-900 text-gray-100 p-4 rounded-lg" {...props}>
                    {children}
                  </pre>
                )
              },
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    customStyle={{
                      margin: 0,
                      fontSize: '0.875rem',
                      lineHeight: '1.5'
                    }}
                    wrapLines={true}
                    wrapLongLines={true}
                    showLineNumbers={true}
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm" {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )
    }
    
    const languageMap: { [key: string]: string } = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'csv': 'csv',
      'log': 'log'
    }
    
    const language = languageMap[ext || ''] || 'text'
    
    return (
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        customStyle={{
          margin: 0,
          borderRadius: '0.5rem',
          fontSize: '0.875rem',
          lineHeight: '1.5'
        }}
        showLineNumbers
        wrapLines={true}
        wrapLongLines={true}
      >
        {content}
      </SyntaxHighlighter>
    )
  }

  const renderFileTree = (nodes: FileNode[], level = 0) => {
    return nodes.map((node) => (
      <motion.div
        key={node.path}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -10 }}
        transition={{ duration: 0.2, delay: level * 0.02 }}
      >
        <motion.div
          className={`flex items-center gap-2 px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer rounded-md transition-colors ${
            selectedFilePath === node.path ? 'bg-blue-100 dark:bg-blue-900/30 ring-1 ring-blue-500/20' : ''
          }`}
          style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
          onClick={() => node.type === 'directory' ? toggleDirectory(node.path) : selectFile(node.path, node)}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          {node.type === 'directory' && (
            <motion.div
              animate={{ rotate: node.isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronRight className="w-4 h-4 text-gray-500" />
            </motion.div>
          )}
          {node.type === 'directory' ? (
            <motion.div
              animate={{ scale: node.isExpanded ? 1.1 : 1 }}
              transition={{ duration: 0.2 }}
            >
              <Folder className={`w-4 h-4 ${node.isExpanded ? 'text-blue-600' : 'text-gray-500'}`} />
            </motion.div>
          ) : (
            getFileIcon(node.name)
          )}
          <span className="text-sm text-gray-700 dark:text-gray-300 truncate flex-1">
            {node.name}
          </span>
          {loadingFiles.has(node.path) && (
            <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
          )}
        </motion.div>
        <AnimatePresence>
          {node.type === 'directory' && node.isExpanded && node.children && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              style={{ overflow: 'hidden' }}
            >
              {renderFileTree(node.children, level + 1)}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    ))
  }

  return (
    <div className="h-full bg-white dark:bg-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">输出文件</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={onLoadFileTree}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            title="刷新"
          >
            <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Tree - Fixed Width */}
        <div 
          className="border-r border-gray-200 dark:border-gray-700 overflow-y-auto bg-gray-50 dark:bg-gray-900"
          style={{ width: `${fileTreeWidth}px`, flexShrink: 0 }}
        >
          <div className="p-4">
            <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider mb-2">文件列表</h4>
            {fileTree.length > 0 ? (
              renderFileTree(fileTree)
            ) : (
              <div className="text-center text-sm text-gray-500 mt-8">
                <Folder className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>暂无文件</p>
              </div>
            )}
          </div>
        </div>

        {/* File Content */}
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900" style={{ minWidth: '400px' }}>
          {selectedFileContent ? (
            <>
              <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getFileIcon(selectedFilePath?.split('/').pop() || '')}
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {selectedFilePath?.split('/').pop()}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopyCode(selectedFileContent)}
                    className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
                    title="复制内容"
                  >
                    {copiedCode === selectedFileContent ? (
                      <Check className="w-4 h-4 text-green-500" />
                    ) : (
                      <Copy className="w-4 h-4 text-gray-500" />
                    )}
                  </button>
                  <button
                    onClick={() => setIsFileContentExpanded(!isFileContentExpanded)}
                    className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
                    title={isFileContentExpanded ? '收起' : '展开'}
                  >
                    {isFileContentExpanded ? (
                      <Minimize2 className="w-4 h-4 text-gray-500" />
                    ) : (
                      <Maximize2 className="w-4 h-4 text-gray-500" />
                    )}
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-6 bg-white dark:bg-gray-800">
                <div className="max-w-none">
                  {renderFileContent(selectedFileContent, selectedFilePath || '')}
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p className="text-sm">选择文件查看内容</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default FileExplorer