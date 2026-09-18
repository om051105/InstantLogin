import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Mail, Lock, User, Zap, CheckCircle2, ShieldCheck } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { InputField } from '../components/InputField'
import { Button } from '../components/Button'
import { Alert } from '../components/Alert'

const passwordStrength = (pwd) => {
  if (!pwd) return { score: 0, label: '', color: '' }
  let score = 0
  if (pwd.length >= 8) score++
  if (pwd.length >= 12) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd)) score++
  if (/[^A-Za-z0-9]/.test(pwd)) score++
  if (score <= 1) return { score, label: 'Weak', color: 'bg-red-500' }
  if (score <= 2) return { score, label: 'Fair', color: 'bg-amber-500' }
  if (score <= 3) return { score, label: 'Good', color: 'bg-brand-400' }
  return { score, label: 'Strong', color: 'bg-emerald-500' }
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})

  const strength = passwordStrength(form.password)

  const set = (key) => (e) => {
    setForm((f) => ({ ...f, [key]: e.target.value }))
    if (fieldErrors[key]) setFieldErrors((f) => ({ ...f, [key]: '' }))
  }

  const validate = () => {
    const errs = {}
    if (!form.name.trim() || form.name.trim().length < 2) errs.name = 'Name must be at least 2 characters'
    if (!form.email.trim()) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Enter a valid email'
    if (!form.password || form.password.length < 8) errs.password = 'Password must be at least 8 characters'
    if (form.password !== form.confirm) errs.confirm = 'Passwords do not match'
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    setError(null)
    try {
      await register(form.name, form.email, form.password)
      setSuccess(true)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'string' && detail.includes('already')) {
        setError({ title: 'Email Already Registered', message: 'An account with this email already exists. Please log in instead.', type: 'warning' })
      } else {
        setError({ title: 'Registration Failed', message: detail || 'Something went wrong. Please try again.', type: 'error' })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-accent-600/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-brand-600/10 rounded-full blur-[100px]" />
      </div>

      <div className="relative w-full max-w-md animate-slide-up">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 to-accent-600 flex items-center justify-center mb-4 glow-brand">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gradient">InstantLogin</h1>
          <p className="text-white/40 text-sm mt-1">Create your account</p>
        </div>

        <div className="glass-card p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-white">Get started</h2>
            <p className="text-white/40 text-sm mt-1">Set up your InstantLogin account</p>
          </div>

          {success && (
            <Alert
              type="success"
              title="Account Created!"
              message="Your account has been created successfully. Redirecting to login…"
              className="mb-5"
            />
          )}

          {error && (
            <Alert
              type={error.type}
              title={error.title}
              message={error.message}
              onDismiss={() => setError(null)}
              className="mb-5"
            />
          )}

          {!success && (
            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              <InputField
                id="register-name"
                label="Full name"
                type="text"
                value={form.name}
                onChange={set('name')}
                placeholder="Jane Smith"
                autoComplete="name"
                error={fieldErrors.name}
                icon={User}
                disabled={loading}
              />
              <InputField
                id="register-email"
                label="Email address"
                type="email"
                value={form.email}
                onChange={set('email')}
                placeholder="you@example.com"
                autoComplete="email"
                error={fieldErrors.email}
                icon={Mail}
                disabled={loading}
              />
              <div className="space-y-2">
                <InputField
                  id="register-password"
                  label="Password"
                  type="password"
                  value={form.password}
                  onChange={set('password')}
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                  error={fieldErrors.password}
                  icon={Lock}
                  disabled={loading}
                />
                {/* Password strength meter */}
                {form.password.length > 0 && (
                  <div className="space-y-1 animate-fade-in">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4].map((i) => (
                        <div
                          key={i}
                          className={`h-1 flex-1 rounded-full transition-all duration-300 ${
                            strength.score >= i ? strength.color : 'bg-white/10'
                          }`}
                        />
                      ))}
                    </div>
                    <p className={`text-xs font-medium ${
                      strength.label === 'Weak' ? 'text-red-400' :
                      strength.label === 'Fair' ? 'text-amber-400' :
                      strength.label === 'Good' ? 'text-brand-400' :
                      'text-emerald-400'
                    }`}>{strength.label}</p>
                  </div>
                )}
              </div>
              <InputField
                id="register-confirm"
                label="Confirm password"
                type="password"
                value={form.confirm}
                onChange={set('confirm')}
                placeholder="Repeat your password"
                autoComplete="new-password"
                error={fieldErrors.confirm}
                icon={Lock}
                disabled={loading}
              />

              <div className="pt-2">
                <Button
                  id="register-submit-btn"
                  type="submit"
                  variant="primary"
                  loading={loading}
                  disabled={loading}
                >
                  <ShieldCheck size={16} />
                  Create Account
                </Button>
              </div>
            </form>
          )}

          <div className="divider">
            <span className="text-xs text-white/30">Already have an account?</span>
          </div>

          <Link to="/login">
            <Button id="go-to-login-btn" variant="secondary">
              Sign in instead
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
