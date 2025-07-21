import React, { useEffect, useState } from 'react'
import Card from '../components/Card'
import Badge from '../components/Badge'
import { 
  Brain, 
  TrendingUp, 
  Clock, 
  FileText,
  Activity,
  Sparkles,
  ArrowRight
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

interface Stats {
  totalTasks: number
  completedTasks: number
  runningTasks: number
  totalIterations: number
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats>({
    totalTasks: 0,
    completedTasks: 0,
    runningTasks: 0,
    totalIterations: 0,
  })

  const [recentFiles, setRecentFiles] = useState<string[]>([
    'deepresearch_report.md',
    'iteration_history.json',
    'summarize_report.md',
    'results.json',
    'best.txt',
  ])

  const statCards = [
    {
      title: 'Total Tasks',
      value: stats.totalTasks,
      icon: Brain,
      color: 'text-apple-blue',
      bgColor: 'bg-apple-blue/10',
    },
    {
      title: 'Completed',
      value: stats.completedTasks,
      icon: TrendingUp,
      color: 'text-apple-green',
      bgColor: 'bg-apple-green/10',
    },
    {
      title: 'Running',
      value: stats.runningTasks,
      icon: Activity,
      color: 'text-apple-yellow',
      bgColor: 'bg-apple-yellow/10',
    },
    {
      title: 'Iterations',
      value: stats.totalIterations,
      icon: Clock,
      color: 'text-apple-purple',
      bgColor: 'bg-apple-purple/10',
    },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-apple-gray-900">欢迎回来</h1>
          <p className="text-apple-gray-600 mt-1">
            Agent 符号回归系统运行状态
          </p>
        </div>
        <Badge variant="success" className="animate-pulse-subtle">
          <Activity className="w-3 h-3 mr-1" />
          系统正常
        </Badge>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-apple-gray-600">{stat.title}</p>
                    <p className="text-3xl font-semibold text-apple-gray-900 mt-1">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`${stat.bgColor} p-3 rounded-xl`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Files */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-apple-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-apple-gray-600" />
              最近文件
            </h3>
            <Link to="/files" className="text-sm text-apple-blue hover:underline">
              查看全部
            </Link>
          </div>
          <div className="space-y-2">
            {recentFiles.map((file, index) => (
              <motion.div
                key={file}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Link
                  to={`/files/output/${file}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-apple-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-apple-gray-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-4 h-4 text-apple-gray-600" />
                    </div>
                    <span className="text-sm font-medium text-apple-gray-700">
                      {file}
                    </span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-apple-gray-400" />
                </Link>
              </motion.div>
            ))}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-apple-gray-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-apple-gray-600" />
              快速操作
            </h3>
          </div>
          <div className="space-y-3">
            <Link
              to="/tasks"
              className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-apple-blue/10 to-apple-purple/10 hover:from-apple-blue/20 hover:to-apple-purple/20 transition-all"
            >
              <div className="flex items-center gap-3">
                <Brain className="w-5 h-5 text-apple-blue" />
                <div>
                  <p className="font-medium text-apple-gray-900">新建任务</p>
                  <p className="text-sm text-apple-gray-600">开始新的符号回归任务</p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-apple-gray-400" />
            </Link>
            
            <Link
              to="/files/output/deepresearch_report.md"
              className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-apple-green/10 to-apple-blue/10 hover:from-apple-green/20 hover:to-apple-blue/20 transition-all"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-apple-green" />
                <div>
                  <p className="font-medium text-apple-gray-900">查看报告</p>
                  <p className="text-sm text-apple-gray-600">最新的研究分析报告</p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-apple-gray-400" />
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard