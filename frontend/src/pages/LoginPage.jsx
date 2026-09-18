import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, Zap, ShieldCheck, AlertCircle, Clock } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { InputField } from '../components/InputField'
import { Button } from '../components/Button'
import { Alert } from '../components/Alert'

// Maps backend error codes to user-friendly explanations
const ERROR_MESSAGES = {
  INVALID_USERNAME: {
    title: 'Account Not Found',
    message: 'No account exists with this email address. Please check your email or create a new account.',
    type: 'error',
  },
  INVALID_PASSWORD: {
    title: 'Incorrect Password',
    message: 'The password you entered is incorrect. Please try again.',
    type: 'error',
  },
  ACCOUNT_LOCKED: {
    title: 'Account Locked',
    message: 'Your account has been locked due to too many failed login attempts. Please contact support or try again later.',
    type: 'warning',
  },
  RATE_LIMITED: {
    title: 'Too Many Attempts',
    message: 'You have exceeded the login attempt limit. Please wait before trying again.',
    type: 'warning',
  },
}

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [retryAfter, setRetryAfter] = useState(null)
  const [fieldErrors, setFieldErrors] = useState({})

  const validate = () => {
    const errs = {}
    if (!email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = 'Enter a valid email address'
    if (!password) errs.password = 'Password is required'
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setLoading(true)
    setError(null)
    setRetryAfter(null)

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'object' && detail?.error) {
        const mapped = ERROR_MESSAGES[detail.error]
        if (mapped) {
          setError(mapped)
        } else {
          setError({ title: 'Login Failed', message: detail.message || 'An error occurred.', type: 'error' })
        }
        if (detail.retry_after) setRetryAfter(detail.retry_after)
      } else {
        setError({
          title: 'Connection Error',
          message: 'Unable to reach the server. Please check your connection and try again.',
          type: 'error',
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-accent-600/10 rounded-full blur-[100px]" />
      </div>

      <div className="relative w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center mb-4 glow-brand">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gradient">InstantLogin</h1>
          <p className="text-white/40 text-sm mt-1">Intelligent authentication system</p>
        </div>

        {/* Card */}
        <div className="glass-card p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white">Welcome back</h2>
            <p className="text-white/40 text-sm mt-1">Sign in to your account</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-5">
              <Alert
                type={error.type}
                title={error.title}
                message={error.message}
                onDismiss={() => setError(null)}
              />
              {retryAfter && (
                <div className="flex items-center gap-2 mt-2 text-xs text-amber-400">
                  <Clock size={12} />
                  <span>Retry available in {retryAfter} seconds</span>
                </div>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <InputField
              id="login-email"
              label="Email address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              error={fieldErrors.email}
              icon={Mail}
              disabled={loading}
            />
            <InputField
              id="login-password"
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
              error={fieldErrors.password}
              icon={Lock}
              disabled={loading}
            />

            <div className="pt-2">
              <Button
                id="login-submit-btn"
                type="submit"
                variant="primary"
                loading={loading}
                disabled={loading}
              >
                <ShieldCheck size={16} />
                Sign In
              </Button>
            </div>
          </form>

          {/* Rate limit info */}
          <div className="mt-5 p-3 rounded-xl bg-white/3 border border-white/5">
            <p className="text-xs text-white/30 flex items-center gap-1.5">
              <ShieldCheck size={11} className="text-brand-400" />
              Protected by ML-powered anomaly detection and rate limiting
            </p>
          </div>

          <div className="divider">
            <span className="text-xs text-white/30">New to InstantLogin?</span>
          </div>

          <Link to="/register">
            <Button id="go-to-register-btn" variant="secondary">
              Create an account
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
