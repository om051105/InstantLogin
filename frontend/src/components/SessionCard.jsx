import { Monitor, Smartphone, Tablet, Globe, Trash2, Clock } from 'lucide-react'
import { Button } from './Button'

const deviceIcon = (device) => {
  if (!device) return <Globe size={18} />
  const d = device.toLowerCase()
  if (d === 'mobile') return <Smartphone size={18} />
  if (d === 'tablet') return <Tablet size={18} />
  return <Monitor size={18} />
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function SessionCard({ session, onRevoke, isRevoking }) {
  const isActive = session.status === 'active'
  return (
    <div className="glass-card p-4 flex items-center gap-4 animate-slide-up">
      {/* Device Icon */}
      <div className={`p-2.5 rounded-xl ${isActive ? 'bg-brand-500/15 text-brand-400' : 'bg-white/5 text-white/30'}`}>
        {deviceIcon(session.device)}
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sm text-white truncate">
            {session.browser || 'Unknown Browser'}
          </span>
          <span className={isActive ? 'status-dot-active' : 'status-dot-inactive'} />
          <span className={`text-xs font-medium ${isActive ? 'text-emerald-400' : 'text-white/40'}`}>
            {isActive ? 'Active' : session.status}
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-white/40">
          {session.ip_address && (
            <span className="flex items-center gap-1">
              <Globe size={11} />
              {session.ip_address}
            </span>
          )}
          <span className="flex items-center gap-1">
            <Clock size={11} />
            {formatDate(session.created_at)}
          </span>
        </div>
      </div>

      {/* Revoke Button */}
      {isActive && (
        <Button
          variant="danger"
          onClick={() => onRevoke(session.session_id)}
          loading={isRevoking}
          className="shrink-0 !w-auto"
          id={`revoke-session-${session.session_id}`}
        >
          <Trash2 size={14} />
          Revoke
        </Button>
      )}
    </div>
  )
}
