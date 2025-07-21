import React, { useState } from 'react'
import Card from '../components/Card'
import Button from '../components/Button'
import Badge from '../components/Badge'
import { 
  Settings as SettingsIcon, 
  Brain, 
  Database, 
  Zap,
  Globe,
  Save,
  RefreshCw,
  Check
} from 'lucide-react'
import { motion } from 'framer-motion'

interface SettingsState {
  general: {
    language: string
    theme: string
    autoSave: boolean
  }
  model: {
    provider: string
    modelName: string
    apiKey: string
    temperature: number
    maxTokens: number
  }
  py: {
    populations: number
    iterations: number
    maxSize: number
    maxDepth: number
    binaryOperators: string[]
    unaryOperators: string[]
  }
  api: {
    backendUrl: string
    websocketUrl: string
    timeout: number
  }
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsState>({
    general: {
      language: 'zh-CN',
      theme: 'light',
      autoSave: true,
    },
    model: {
      provider: 'openai',
      modelName: 'gpt-4o-mini',
      apiKey: '••••••••••••••••',
      temperature: 0.7,
      maxTokens: 4096,
    },
    py: {
      populations: 50,
      iterations: 1000,
      maxSize: 20,
      maxDepth: 5,
      binaryOperators: ['+', '-', '*', '/'],
      unaryOperators: ['square', 'cube', 'exp', 'log', 'sqrt'],
    },
    api: {
      backendUrl: 'http://localhost:8000',
      websocketUrl: 'ws://localhost:8000',
      timeout: 30000,
    },
  })

  const [saved, setSaved] = useState(false)
  const [activeTab, setActiveTab] = useState<'general' | 'model' | 'py' | 'api'>('general')

  const handleSave = () => {
    // Save settings logic here
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    // Reset to default settings
    if (window.confirm('确定要重置所有设置吗？')) {
      // Reset logic here
    }
  }

  const tabs = [
    { id: 'general', name: '通用设置', icon: SettingsIcon },
    { id: 'model', name: 'AI 模型', icon: Brain },
    { id: 'py', name: '符号回归', icon: Zap },
    { id: 'api', name: 'API 配置', icon: Globe },
  ] as const

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-apple-gray-900">系统设置</h1>
          <p className="text-apple-gray-600 mt-1">
            配置 Agent 系统参数
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            icon={<RefreshCw className="w-4 h-4" />}
            onClick={handleReset}
          >
            重置
          </Button>
          <Button
            variant="primary"
            icon={saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            onClick={handleSave}
            className={saved ? 'bg-apple-green hover:bg-apple-green/90' : ''}
          >
            {saved ? '已保存' : '保存设置'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tabs */}
        <div className="lg:col-span-1">
          <Card className="p-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === tab.id
                      ? 'bg-apple-blue/10 text-apple-blue'
                      : 'text-apple-gray-600 hover:bg-apple-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.name}</span>
                </button>
              )
            })}
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Card>
              {activeTab === 'general' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-apple-gray-900">通用设置</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      界面语言
                    </label>
                    <select
                      className="input w-full max-w-xs"
                      value={settings.general.language}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, language: e.target.value },
                        })
                      }
                    >
                      <option value="zh-CN">中文（简体）</option>
                      <option value="en-US">English</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      主题
                    </label>
                    <div className="flex gap-3">
                      <button
                        className={`px-4 py-2 rounded-lg border ${
                          settings.general.theme === 'light'
                            ? 'border-apple-blue bg-apple-blue/10 text-apple-blue'
                            : 'border-apple-gray-300 text-apple-gray-600'
                        }`}
                        onClick={() =>
                          setSettings({
                            ...settings,
                            general: { ...settings.general, theme: 'light' },
                          })
                        }
                      >
                        浅色
                      </button>
                      <button
                        className={`px-4 py-2 rounded-lg border ${
                          settings.general.theme === 'dark'
                            ? 'border-apple-blue bg-apple-blue/10 text-apple-blue'
                            : 'border-apple-gray-300 text-apple-gray-600'
                        }`}
                        onClick={() =>
                          setSettings({
                            ...settings,
                            general: { ...settings.general, theme: 'dark' },
                          })
                        }
                      >
                        深色
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="flex items-center gap-3">
                      <input
                        type="checkbox"
                        className="w-5 h-5 rounded border-apple-gray-300 text-apple-blue focus:ring-apple-blue"
                        checked={settings.general.autoSave}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            general: { ...settings.general, autoSave: e.target.checked },
                          })
                        }
                      />
                      <span className="text-sm font-medium text-apple-gray-700">
                        自动保存设置
                      </span>
                    </label>
                  </div>
                </div>
              )}

              {activeTab === 'model' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-apple-gray-900">AI 模型配置</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      模型提供商
                    </label>
                    <select
                      className="input w-full max-w-xs"
                      value={settings.model.provider}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          model: { ...settings.model, provider: e.target.value },
                        })
                      }
                    >
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="google">Google</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      模型名称
                    </label>
                    <input
                      type="text"
                      className="input w-full max-w-md"
                      value={settings.model.modelName}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          model: { ...settings.model, modelName: e.target.value },
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      API Key
                    </label>
                    <input
                      type="password"
                      className="input w-full max-w-md"
                      value={settings.model.apiKey}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          model: { ...settings.model, apiKey: e.target.value },
                        })
                      }
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        Temperature
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="2"
                        step="0.1"
                        className="input w-full"
                        value={settings.model.temperature}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            model: { ...settings.model, temperature: parseFloat(e.target.value) },
                          })
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        Max Tokens
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="32000"
                        className="input w-full"
                        value={settings.model.maxTokens}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            model: { ...settings.model, maxTokens: parseInt(e.target.value) },
                          })
                        }
                      />
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'py' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-apple-gray-900">符号回归参数</h3>
                  
                  <div className="grid grid-cols-2 gap-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        种群数量
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="1000"
                        className="input w-full"
                        value={settings.py.populations}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            py: { ...settings.py, populations: parseInt(e.target.value) },
                          })
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        迭代次数
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="10000"
                        className="input w-full"
                        value={settings.py.iterations}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            py: { ...settings.py, iterations: parseInt(e.target.value) },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        最大表达式大小
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="100"
                        className="input w-full"
                        value={settings.py.maxSize}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            py: { ...settings.py, maxSize: parseInt(e.target.value) },
                          })
                        }
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                        最大深度
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="20"
                        className="input w-full"
                        value={settings.py.maxDepth}
                        onChange={(e) =>
                          setSettings({
                            ...settings,
                            py: { ...settings.py, maxDepth: parseInt(e.target.value) },
                          })
                        }
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      二元运算符
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {['+', '-', '*', '/', '**'].map((op) => (
                        <label key={op} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            className="w-4 h-4 rounded border-apple-gray-300 text-apple-blue focus:ring-apple-blue"
                            checked={settings.py.binaryOperators.includes(op)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSettings({
                                  ...settings,
                                  py: {
                                    ...settings.py,
                                    binaryOperators: [...settings.py.binaryOperators, op],
                                  },
                                })
                              } else {
                                setSettings({
                                  ...settings,
                                  py: {
                                    ...settings.py,
                                    binaryOperators: settings.py.binaryOperators.filter(
                                      (o) => o !== op
                                    ),
                                  },
                                })
                              }
                            }}
                          />
                          <code className="text-sm">{op}</code>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      一元运算符
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {['square', 'cube', 'exp', 'log', 'sqrt', 'neg', 'abs', 'sin', 'cos'].map(
                        (op) => (
                          <label key={op} className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-apple-gray-300 text-apple-blue focus:ring-apple-blue"
                              checked={settings.py.unaryOperators.includes(op)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSettings({
                                    ...settings,
                                    py: {
                                      ...settings.py,
                                      unaryOperators: [...settings.py.unaryOperators, op],
                                    },
                                  })
                                } else {
                                  setSettings({
                                    ...settings,
                                    py: {
                                      ...settings.py,
                                      unaryOperators: settings.py.unaryOperators.filter(
                                        (o) => o !== op
                                      ),
                                    },
                                  })
                                }
                              }}
                            />
                            <code className="text-sm">{op}</code>
                          </label>
                        )
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'api' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-medium text-apple-gray-900">API 配置</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      后端 API 地址
                    </label>
                    <input
                      type="text"
                      className="input w-full max-w-md"
                      value={settings.api.backendUrl}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          api: { ...settings.api, backendUrl: e.target.value },
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      WebSocket 地址
                    </label>
                    <input
                      type="text"
                      className="input w-full max-w-md"
                      value={settings.api.websocketUrl}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          api: { ...settings.api, websocketUrl: e.target.value },
                        })
                      }
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-apple-gray-700 mb-2">
                      请求超时时间 (毫秒)
                    </label>
                    <input
                      type="number"
                      min="1000"
                      max="300000"
                      step="1000"
                      className="input w-full max-w-xs"
                      value={settings.api.timeout}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          api: { ...settings.api, timeout: parseInt(e.target.value) },
                        })
                      }
                    />
                  </div>

                  <div className="pt-4">
                    <Badge variant="info">
                      <Database className="w-3 h-3 mr-1" />
                      API 连接正常
                    </Badge>
                  </div>
                </div>
              )}
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Settings