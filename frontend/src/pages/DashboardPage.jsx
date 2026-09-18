import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Zap, LogOut, Shield, Activity, Clock, CheckCircle2,
  XCircle, AlertTriangle, RefreshCw, ChevronRight, Server,
  Database, Cpu, User2
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { sessionsApi, healthApi } from '../api/auth'
import { SessionCard } from '../components/SessionCard'
import { Alert } from '../components/Alert'
import { Button } from '../components/Button'

const formatDate = (d) => d ? new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '—'
const formatDateTime = (d) => d ? new Date(d).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Never'

const attemptErrorLabel = (code) => {
  const map = {
    NONE: { label: 'Success', color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    INVALID_PASSWORD: { label: 'Wrong Password', color: 'text-red-400', bg: 'bg-red-400/10' },
    INVALID_USERNAME: { label: 'Unknown Email', color: 'text-red-400', bg: 'bg-red-400/10' },
    ACCOUNT_LOCKED: { label: 'Locked', color: 'text-amber-400', bg: 'bg-amber-400/10' },
    RATE_LIMITED: { label: 'Rate Limited', color: 'text-amber-400', bg: 'bg-amber-400/10' },
    SERVER_ERROR: { label: 'Server Error', color: 'text-red-400', bg: 'bg-red-400/10' },
  }
  return map[code] || { label: code, color: 'text-white/50', bg: 'bg-white/5' }
}

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [sessions, setSessions] = useState([])
  const [attempts, setAttempts] = useState([])
  const [health, setHealth] = useState(null)
  const [loadingSessions, setLoadingSessions] = useState(true)
  const [loadingAttempts, setLoadingAttempts] = useState(true)
  const [loadingHealth, setLoadingHealth] = useState(true)
  const [revokingId, setRevokingId] = useState(null)
  const [notification, setNotification] = useState(null)
  const [activeTab, setActiveTab] = useState('sessions')

  const fetchData = useCallback(async () => {
    try {
      const [sessRes, attRes] = await Promise.all([
        sessionsApi.list(),
        sessionsApi.attempts(10),
      ])
      setSessions(sessRes.data.sessions || [])
      setAttempts(attRes.data.attempts || [])
    } catch {
      // silently fail - token refresh handled by interceptor
    } finally {
      setLoadingSessions(false)
      setLoadingAttempts(false)
    }

    try {
      const healthRes = await healthApi.check()
      setHealth(healthRes.data)
    } catch {
      setHealth({ status: 'unhealthy', components: {} })
    } finally {
      setLoadingHealth(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleRevoke = async (sessionId) => {
    setRevokingId(sessionId)
    try {
      await sessionsApi.revoke(sessionId)
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
      setNotification({ type: 'success', message: 'Session revoked successfully.' })
    } catch {
      setNotification({ type: 'error', message: 'Failed to revoke session.' })
    } finally {
      setRevokingId(null)
      setTimeout(() => setNotification(null), 3000)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const successRate = attempts.length > 0
    ? Math.round((attempts.filter(a => a.success).length / attempts.length) * 100)
    : 100

  const stats = [
    {
      label: 'Active Sessions',
      value: sessions.length,
      icon: Shield,
      color: 'text-brand-400',
      bg: 'bg-brand-400/10',
    },
    {
      label: 'Recent Attempts',
      value: attempts.length,
      icon: Activity,
      color: 'text-accent-400',
      bg: 'bg-accent-400/10',
    },
    {
      label: 'Success Rate',
      value: `${successRate}%`,
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-400/10',
    },
    {
      label: 'Account Status',
      value: user?.account_status || 'active',
      icon: User2,
      color: 'text-brand-300',
      bg: 'bg-brand-300/10',
      capitalize: true,
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/3 w-96 h-96 bg-brand-600/8 rounded-full blur-[140px]" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-600/8 rounded-full blur-[120px]" />
      </div>

      <div className="relative max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center glow-brand">
              <Zap size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">InstantLogin</h1>
              <p className="text-xs text-white/40">Authentication Dashboard</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="glass-card px-4 py-2 flex items-center gap-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center text-xs font-bold">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-white leading-tight">{user?.name || 'User'}</p>
                <p className="text-xs text-white/40 leading-tight">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              id="logout-btn"
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm text-white/60 hover:text-white bg-white/5 hover:bg-red-500/15 border border-white/5 hover:border-red-500/30 transition-all duration-200"
            >
              <LogOut size={15} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>

        {/* Notification */}
        {notification && (
          <div className="mb-6 animate-slide-up">
            <Alert type={notification.type} message={notification.message} onDismiss={() => setNotification(null)} />
          </div>
        )}

        {/* Welcome bar */}
        <div className="glass-card p-5 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-slide-up">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'},{' '}
              <span className="text-gradient">{user?.name?.split(' ')[0] || 'User'}</span> 👋
            </h2>
            <p className="text-sm text-white/40 mt-0.5">
              Member since {formatDate(user?.created_at)} · Last login: {formatDateTime(user?.last_login)}
            </p>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5"
          >
            <RefreshCw size={12} />
            Refresh
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {stats.map((stat) => {
            const Icon = stat.icon
            return (
              <div key={stat.label} className="glass-card p-5 animate-slide-up">
                <div className={`w-9 h-9 rounded-xl ${stat.bg} flex items-center justify-center mb-3`}>
                  <Icon size={18} className={stat.color} />
                </div>
                <p className={`text-2xl font-bold text-white mb-1 ${stat.capitalize ? 'capitalize' : ''}`}>
                  {stat.value}
                </p>
                <p className="text-xs text-white/40">{stat.label}</p>
              </div>
            )
          })}
        </div>

        {/* System Health */}
        <div className="glass-card p-5 mb-6 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Server size={16} className="text-brand-400" />
              System Health
            </h3>
            <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
              health?.status === 'healthy' ? 'bg-emerald-400/15 text-emerald-400' :
              health?.status === 'degraded' ? 'bg-amber-400/15 text-amber-400' :
              'bg-red-400/15 text-red-400'
            }`}>
              {loadingHealth ? '...' : health?.status || 'Unknown'}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {['mysql', 'redis'].map((comp) => {
              const status = health?.components?.[comp]
              const isHealthy = status === 'healthy'
              return (
                <div key={comp} className="flex items-center gap-3 p-3 rounded-xl bg-white/3 border border-white/5">
                  {comp === 'mysql' ? <Database size={15} className="text-white/50" /> : <Cpu size={15} className="text-white/50" />}
                  <div>
                    <p className="text-sm font-medium text-white capitalize">{comp}</p>
                    <p className={`text-xs ${isHealthy ? 'text-emerald-400' : 'text-red-400'}`}>
                      {loadingHealth ? 'Checking…' : isHealthy ? 'Healthy' : 'Unavailable'}
                    </p>
                  </div>
                  <div className="ml-auto">
                    {loadingHealth ? (
                      <div className="skeleton w-4 h-4 rounded-full" />
                    ) : isHealthy ? (
                      <CheckCircle2 size={15} className="text-emerald-400" />
                    ) : (
                      <XCircle size={15} className="text-red-400" />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Tabs */}
        <div className="glass-card overflow-hidden animate-slide-up">
          <div className="flex border-b border-white/5">
            {[
              { id: 'sessions', label: 'Active Sessions', icon: Shield },
              { id: 'attempts', label: 'Login History', icon: Clock },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                id={`tab-${id}`}
                onClick={() => setActiveTab(id)}
                className={`flex-1 flex items-center justify-center gap-2 py-4 text-sm font-medium transition-all duration-200 ${
                  activeTab === id
                    ? 'text-brand-400 border-b-2 border-brand-500 bg-brand-500/5'
                    : 'text-white/40 hover:text-white/70 hover:bg-white/3'
                }`}
              >
                <Icon size={15} />
                {label}
              </button>
            ))}
          </div>

          <div className="p-5">
            {activeTab === 'sessions' && (
              <div className="space-y-3">
                {loadingSessions ? (
                  [1, 2].map((i) => <div key={i} className="skeleton h-20 w-full rounded-2xl" />)
                ) : sessions.length === 0 ? (
                  <div className="text-center py-10 text-white/30">
                    <Shield size={40} className="mx-auto mb-3 opacity-30" />
                    <p className="text-sm">No active sessions</p>
                  </div>
                ) : (
                  sessions.map((s) => (
                    <SessionCard
                      key={s.session_id}
                      session={s}
                      onRevoke={handleRevoke}
                      isRevoking={revokingId === s.session_id}
                    />
                  ))
                )}
              </div>
            )}

            {activeTab === 'attempts' && (
              <div className="space-y-2">
                {loadingAttempts ? (
                  [1, 2, 3].map((i) => <div key={i} className="skeleton h-14 w-full rounded-xl" />)
                ) : attempts.length === 0 ? (
                  <div className="text-center py-10 text-white/30">
                    <Clock size={40} className="mx-auto mb-3 opacity-30" />
                    <p className="text-sm">No login history yet</p>
                  </div>
                ) : (
                  attempts.map((a) => {
                    const badge = attemptErrorLabel(a.error_code)
                    return (
                      <div key={a.attempt_id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/3 transition-colors">
                        {a.success
                          ? <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                          : <XCircle size={16} className="text-red-400 shrink-0" />
                        }
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-white/80">
                            {a.browser || 'Unknown'} · {a.ip_address || 'Unknown IP'}
                          </p>
                          <p className="text-xs text-white/30">{formatDateTime(a.timestamp)}</p>
                        </div>
                        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${badge.bg} ${badge.color} shrink-0`}>
                          {badge.label}
                        </span>
                        {a.response_time_ms && (
                          <span className="text-xs text-white/30 hidden sm:block shrink-0">
                            {Math.round(a.response_time_ms)}ms
                          </span>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
