import React, { useState, useEffect } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import Badge from '../components/Badge'
import { 
  Plus, 
  Play, 
  Pause, 
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Clock,
  Loader2,
  FileText,
  ChevronRight,
  Brain
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Task {
  id: string
  name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  type: 'research' | 'py' | 'summarize' | 'iteration'
  progress: number
  startTime?: Date
  endTime?: Date
  result?: any
  error?: string
}

interface NewTaskModal {
  isOpen: boolean
  taskName: string
  taskType: string
  dataPath: string
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      name: 'Deep Research Analysis',
      status: 'completed',
      type: 'research',
      progress: 100,
      startTime: new Date('2024-01-15T10:00:00'),
      endTime: new Date('2024-01-15T10:05:00'),
    },
    {
      id: '2',
      name: 'Symbolic Regression - Iteration 1',
      status: 'running',
      type: 'py',
      progress: 65,
      startTime: new Date('2024-01-15T10:10:00'),
    },
    {
      id: '3',
      name: 'Generate Summary Report',
      status: 'pending',
      type: 'summarize',
      progress: 0,
    },
  ])

  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const [newTaskModal, setNewTaskModal] = useState<NewTaskModal>({
    isOpen: false,
    taskName: '',
    taskType: 'py',
    dataPath: '',
  })

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-apple-green" />
      case 'running':
        return <Loader2 className="w-5 h-5 text-apple-blue animate-spin" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-apple-red" />
      default:
        return <Clock className="w-5 h-5 text-apple-gray-400" />
    }
  }

  const getStatusBadge = (status: Task['status']) => {
    const variants = {
      completed: 'success',
      running: 'info',
      failed: 'error',
      pending: 'warning',
    } as const

    const labels = {
      completed: '已完成',
      running: '运行中',
      failed: '失败',
      pending: '等待中',
    }

    return <Badge variant={variants[status]}>{labels[status]}</Badge>
  }

  const getTypeIcon = (type: Task['type']) => {
    switch (type) {
      case 'research':
        return <Brain className="w-4 h-4" />
      case 'py':
        return <Play className="w-4 h-4" />
      case 'summarize':
        return <FileText className="w-4 h-4" />
      case 'iteration':
        return <RotateCcw className="w-4 h-4" />
    }
  }

  const formatDuration = (start?: Date, end?: Date) => {
    if (!start) return '-'
    const endTime = end || new Date()
    const duration = endTime.getTime() - start.getTime()
    const seconds = Math.floor(duration / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`
    } else {
      return `${seconds}s`
    }
  }

  const handleCreateTask = () => {
    const newTask: Task = {
      id: Date.now().toString(),
      name: newTaskModal.taskName,
      status: 'pending',
      type: newTaskModal.taskType as Task['type'],
      progress: 0,
    }
    setTasks([...tasks, newTask])
    setNewTaskModal({ ...newTaskModal, isOpen: false, taskName: '', dataPath: '' })
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-apple-gray-900">任务管理</h1>
          <p className="text-apple-gray-600 mt-1">
            管理和监控符号回归任务
          </p>
        </div>
        <Button
          variant="primary"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => setNewTaskModal({ ...newTaskModal, isOpen: true })}
        >
          新建任务
        </Button>
      </div>

      {/* Task List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <AnimatePresence>
            {tasks.map((task, index) => (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card
                  hoverable
                  onClick={() => setSelectedTask(task)}
                  className={selectedTask?.id === task.id ? 'ring-2 ring-apple-blue' : ''}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {getStatusIcon(task.status)}
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium text-apple-gray-900">
                            {task.name}
                          </h3>
                          <div className="flex items-center gap-1 text-apple-gray-500">
                            {getTypeIcon(task.type)}
                            <span className="text-xs">{task.type}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-apple-gray-600">
                          <span>进度: {task.progress}%</span>
                          <span>•</span>
                          <span>
                            时长: {formatDuration(task.startTime, task.endTime)}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(task.status)}
                      <ChevronRight className="w-4 h-4 text-apple-gray-400" />
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="w-full bg-apple-gray-200 rounded-full h-2 overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-apple-blue to-apple-purple"
                        initial={{ width: 0 }}
                        animate={{ width: `${task.progress}%` }}
                        transition={{ duration: 0.5, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Task Details */}
        <div>
          <Card className="sticky top-6">
            <h3 className="text-lg font-medium text-apple-gray-900 mb-4">
              任务详情
            </h3>
            {selectedTask ? (
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-apple-gray-600">任务名称</p>
                  <p className="font-medium">{selectedTask.name}</p>
                </div>
                <div>
                  <p className="text-sm text-apple-gray-600">任务类型</p>
                  <p className="font-medium capitalize">{selectedTask.type}</p>
                </div>
                <div>
                  <p className="text-sm text-apple-gray-600">状态</p>
                  <div className="mt-1">{getStatusBadge(selectedTask.status)}</div>
                </div>
                <div>
                  <p className="text-sm text-apple-gray-600">开始时间</p>
                  <p className="font-medium">
                    {selectedTask.startTime
                      ? selectedTask.startTime.toLocaleString('zh-CN')
                      : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-apple-gray-600">结束时间</p>
                  <p className="font-medium">
                    {selectedTask.endTime
                      ? selectedTask.endTime.toLocaleString('zh-CN')
                      : '-'}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="pt-4 border-t border-apple-gray-200 space-y-2">
                  {selectedTask.status === 'running' && (
                    <Button
                      variant="secondary"
                      className="w-full"
                      icon={<Pause className="w-4 h-4" />}
                    >
                      暂停任务
                    </Button>
                  )}
                  {selectedTask.status === 'pending' && (
                    <Button
                      variant="primary"
                      className="w-full"
                      icon={<Play className="w-4 h-4" />}
                    >
                      开始任务
                    </Button>
                  )}
                  {selectedTask.status === 'completed' && (
                    <Button
                      variant="secondary"
                      className="w-full"
                      icon={<FileText className="w-4 h-4" />}
                    >
                      查看结果
                    </Button>
                  )}
                  {selectedTask.status === 'failed' && (
                    <Button
                      variant="secondary"
                      className="w-full"
                      icon={<RotateCcw className="w-4 h-4" />}
                    >
                      重试任务
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-apple-gray-500 text-center py-8">
                选择一个任务查看详情
              </p>
            )}
          </Card>
        </div>
      </div>

      {/* New Task Modal */}
      <AnimatePresence>
        {newTaskModal.isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setNewTaskModal({ ...newTaskModal, isOpen: false })}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-xl font-semibold text-apple-gray-900 mb-4">
                创建新任务
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-apple-gray-700 mb-1">
                    任务名称
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="输入任务名称"
                    value={newTaskModal.taskName}
                    onChange={(e) =>
                      setNewTaskModal({ ...newTaskModal, taskName: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-gray-700 mb-1">
                    任务类型
                  </label>
                  <select
                    className="input"
                    value={newTaskModal.taskType}
                    onChange={(e) =>
                      setNewTaskModal({ ...newTaskModal, taskType: e.target.value })
                    }
                  >
                    <option value="py">符号回归</option>
                    <option value="research">深度研究</option>
                    <option value="summarize">生成报告</option>
                    <option value="iteration">迭代优化</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-apple-gray-700 mb-1">
                    数据文件路径
                  </label>
                  <input
                    type="text"
                    className="input"
                    placeholder="/path/to/data.csv"
                    value={newTaskModal.dataPath}
                    onChange={(e) =>
                      setNewTaskModal({ ...newTaskModal, dataPath: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setNewTaskModal({ ...newTaskModal, isOpen: false })}
                >
                  取消
                </Button>
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={handleCreateTask}
                  disabled={!newTaskModal.taskName || !newTaskModal.dataPath}
                >
                  创建任务
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Tasks