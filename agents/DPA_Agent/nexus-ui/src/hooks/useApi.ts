import { useState, useEffect, useCallback } from 'react'
import { api, wsClient, Task, Stats, RecentFile } from '../api/client'

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api.getTasks()
      setTasks(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTasks()

    // WebSocket listeners
    const handleTaskCreated = (data: any) => {
      setTasks(prev => [...prev, data.task])
    }

    const handleTaskUpdated = (data: any) => {
      setTasks(prev => prev.map(task => 
        task.id === data.task.id ? data.task : task
      ))
    }

    const handleTaskProgress = (data: any) => {
      setTasks(prev => prev.map(task => 
        task.id === data.taskId ? { ...task, progress: data.progress } : task
      ))
    }

    const handleTaskDeleted = (data: any) => {
      setTasks(prev => prev.filter(task => task.id !== data.taskId))
    }

    wsClient.on('task_created', handleTaskCreated)
    wsClient.on('task_updated', handleTaskUpdated)
    wsClient.on('task_progress', handleTaskProgress)
    wsClient.on('task_deleted', handleTaskDeleted)

    return () => {
      wsClient.off('task_created', handleTaskCreated)
      wsClient.off('task_updated', handleTaskUpdated)
      wsClient.off('task_progress', handleTaskProgress)
      wsClient.off('task_deleted', handleTaskDeleted)
    }
  }, [])

  return { tasks, loading, error, refetch: fetchTasks }
}

export function useStats() {
  const [stats, setStats] = useState<Stats>({
    totalTasks: 0,
    completedTasks: 0,
    runningTasks: 0,
    totalIterations: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  return { stats, loading }
}

export function useRecentFiles() {
  const [files, setFiles] = useState<RecentFile[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const data = await api.getRecentFiles()
        setFiles(data)
      } catch (error) {
        console.error('Failed to fetch recent files:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchFiles()

    // Listen for file changes
    const handleFileChanged = () => {
      fetchFiles()
    }

    wsClient.on('file_changed', handleFileChanged)

    return () => {
      wsClient.off('file_changed', handleFileChanged)
    }
  }, [])

  return { files, loading }
}

export function useFile(path: string) {
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!path) {
      setLoading(false)
      return
    }

    const fetchFile = async () => {
      try {
        setLoading(true)
        const data = await api.getFile(path)
        setContent(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load file')
        setContent('')
      } finally {
        setLoading(false)
      }
    }

    fetchFile()

    // Listen for file changes
    const handleFileChanged = (data: any) => {
      if (data.path.includes(path)) {
        fetchFile()
      }
    }

    wsClient.on('file_changed', handleFileChanged)

    return () => {
      wsClient.off('file_changed', handleFileChanged)
    }
  }, [path])

  return { content, loading, error }
}

export function useWebSocket() {
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    wsClient.connect()

    const handleConnected = () => setConnected(true)
    const handleDisconnected = () => setConnected(false)

    wsClient.on('connected', handleConnected)
    wsClient.on('disconnected', handleDisconnected)

    return () => {
      wsClient.off('connected', handleConnected)
      wsClient.off('disconnected', handleDisconnected)
      wsClient.disconnect()
    }
  }, [])

  return { connected }
}