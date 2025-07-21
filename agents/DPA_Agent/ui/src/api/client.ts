import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface Task {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused'
  type: 'research' | 'py' | 'summarize' | 'iteration'
  progress: number
  startTime?: string
  endTime?: string
  result?: any
  error?: string
}

export interface CreateTaskRequest {
  name: string
  type: string
  dataPath: string
}

export interface Stats {
  totalTasks: number
  completedTasks: number
  runningTasks: number
  totalIterations: number
}

export interface RecentFile {
  name: string
  path: string
  size: number
  modified: string
}

// API methods
export const api = {
  // Files
  async getFile(path: string): Promise<string> {
    const response = await apiClient.get(`/api/files/${path}`, {
      responseType: 'text',
    })
    return response.data
  },

  async getRecentFiles(): Promise<RecentFile[]> {
    const response = await apiClient.get('/api/recent-files')
    return response.data
  },

  // Tasks
  async getTasks(): Promise<Task[]> {
    const response = await apiClient.get('/api/tasks')
    return response.data
  },

  async getTask(id: string): Promise<Task> {
    const response = await apiClient.get(`/api/tasks/${id}`)
    return response.data
  },

  async createTask(data: CreateTaskRequest): Promise<Task> {
    const response = await apiClient.post('/api/tasks', data)
    return response.data
  },

  async startTask(id: string): Promise<void> {
    await apiClient.put(`/api/tasks/${id}/start`)
  },

  async pauseTask(id: string): Promise<void> {
    await apiClient.put(`/api/tasks/${id}/pause`)
  },

  async deleteTask(id: string): Promise<void> {
    await apiClient.delete(`/api/tasks/${id}`)
  },

  // Stats
  async getStats(): Promise<Stats> {
    const response = await apiClient.get('/api/stats')
    return response.data
  },
}

// WebSocket connection
export class WSClient {
  private ws: WebSocket | null = null
  private reconnectTimeout: NodeJS.Timeout | null = null
  private listeners: Map<string, Set<Function>> = new Map()

  connect() {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws'
    
    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.emit('connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.emit('disconnected')
      this.reconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', error)
    }
  }

  private reconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
    }

    this.reconnectTimeout = setTimeout(() => {
      console.log('Attempting to reconnect WebSocket...')
      this.connect()
    }, 5000)
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: Function) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.delete(callback)
    }
  }

  private emit(event: string, data?: any) {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.forEach(callback => callback(data))
    }
  }
}

export const wsClient = new WSClient()