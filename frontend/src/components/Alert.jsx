import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react'

const icons = {
  error: AlertCircle,
  success: CheckCircle2,
  info: Info,
  warning: AlertTriangle,
}

const classes = {
  error: 'alert-error',
  success: 'alert-success',
  info: 'alert-info',
  warning: 'alert-warning',
}

export function Alert({ type = 'info', title, message, onDismiss, className = '' }) {
  const Icon = icons[type]
  return (
    <div className={`${classes[type]} animate-slide-up ${className}`} role="alert">
      <Icon size={18} className="flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        {title && <p className="font-semibold mb-0.5">{title}</p>}
        {message && <p className="opacity-90 leading-relaxed">{message}</p>}
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity focus:outline-none"
          aria-label="Dismiss"
        >
          <X size={16} />
        </button>
      )}
    </div>
  )
}
