import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

// 默认主机始终被允许
const defaultHosts = ['localhost', '127.0.0.1', '0.0.0.0']

// 读取 agent-config.json 配置
let serverConfig = {
  port: 50002,
  allowedHosts: defaultHosts
}

try {
  const configPath = path.resolve(__dirname, '../config/agent-config.json')
  const configData = fs.readFileSync(configPath, 'utf-8')
  const config = JSON.parse(configData)
  if (config.server) {
    // 合并默认主机和用户定义的额外主机
    const userHosts = config.server.allowedHosts || []
    const allHosts = [...new Set([...defaultHosts, ...userHosts])]
    
    serverConfig = {
      port: config.server.port || 50002,
      allowedHosts: allHosts
    }
  }
} catch (error) {
  console.warn('Failed to load agent-config.json, using defaults:', error)
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: parseInt(process.env.FRONTEND_PORT || String(serverConfig.port)),
    allowedHosts: serverConfig.allowedHosts,
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true,
      }
    }
  }
}) // 添加缺失的闭合括号