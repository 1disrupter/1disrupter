/**
 * AlphaAI Authentication Pages
 * Login, Register, Forgot Password, Reset Password
 */
import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  Brain, Mail, Lock, User, Eye, EyeOff, ArrowRight, 
  Sparkles, Shield, Zap, Check, AlertCircle, Loader2
} from 'lucide-react';

// Brand Lockup Component for Auth Pages
const AuthBrandLockup = ({ showSubtitle = true }) => (
  <div className="flex flex-col items-center" data-testid="auth-brand-lockup">
    <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center mb-3">
      <Brain className="w-8 h-8 text-white" />
    </div>
    <span className="text-2xl font-bold font-['Outfit'] tracking-tight">My-AlphaAI</span>
    {showSubtitle && (
      <span className="text-xs text-zinc-400 font-light tracking-[0.2em] uppercase mt-1">
        Signal Intelligence System
      </span>
    )}
  </div>
);

// Login Page
export const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [error, setError] = useState('');

  const location = useLocation();
  const redirectTo = location.state?.from || '/dashboard';

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectTo);
    }
  }, [isAuthenticated, navigate, redirectTo]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const result = await login(email, password, requires2FA ? totpCode : null);
    
    if (result.success) {
      navigate(redirectTo);
    } else if (result.requires2FA) {
      setRequires2FA(true);
    } else {
      setError(result.error || 'Login failed');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20" data-testid="login-page">
      <div className="w-full max-w-md">
        {/* Brand Lockup */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link to="/">
            <AuthBrandLockup showSubtitle={true} />
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="glass-card border-zinc-800" data-testid="login-card">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Welcome Back</CardTitle>
              <CardDescription>Sign in to access your AI trading signals</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <AnimatePresence mode="wait">
                  {!requires2FA ? (
                    <motion.div
                      key="credentials"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      className="space-y-4"
                    >
                      <div className="space-y-2">
                        <label className="text-sm text-zinc-400">Email</label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                          <Input
                            type="email"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="pl-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                            required
                            data-testid="login-email-input"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <label className="text-sm text-zinc-400">Password</label>
                          <Link 
                            to="/forgot-password" 
                            className="text-xs text-[#7B61FF] hover:underline"
                            data-testid="forgot-password-link"
                          >
                            Forgot password?
                          </Link>
                        </div>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                          <Input
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="pl-10 pr-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                            required
                            data-testid="login-password-input"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                          >
                            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="2fa"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="space-y-4"
                    >
                      <div className="text-center mb-4">
                        <Shield className="w-12 h-12 mx-auto text-[#7B61FF] mb-2" />
                        <p className="text-sm text-zinc-400">
                          Enter the 6-digit code from your authenticator app
                        </p>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm text-zinc-400">2FA Code</label>
                        <Input
                          type="text"
                          placeholder="000000"
                          value={totpCode}
                          onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                          className="text-center text-2xl tracking-widest bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                          maxLength={6}
                          required
                          autoFocus
                          data-testid="login-2fa-input"
                        />
                      </div>
                      <button
                        type="button"
                        onClick={() => setRequires2FA(false)}
                        className="text-sm text-zinc-500 hover:text-zinc-300"
                      >
                        Use a different account
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    data-testid="login-error"
                  >
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </motion.div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-11"
                  data-testid="login-submit-btn"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      Sign In
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center text-sm text-zinc-500">
                Don't have an account?{' '}
                <Link to="/register" className="text-[#7B61FF] hover:underline" data-testid="register-link">
                  Sign up
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 grid grid-cols-3 gap-4"
        >
          {[
            { icon: Zap, label: 'Real-time Signals' },
            { icon: Shield, label: 'Secure Auth' },
            { icon: Sparkles, label: 'AI-Powered' }
          ].map((item, i) => (
            <div key={i} className="text-center">
              <div className="w-10 h-10 mx-auto rounded-lg bg-zinc-800/50 flex items-center justify-center mb-2">
                <item.icon className="w-5 h-5 text-zinc-400" />
              </div>
              <p className="text-xs text-zinc-500">{item.label}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

// Register Page
export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const passwordStrength = () => {
    if (password.length < 8) return { level: 0, text: 'Too short', color: 'bg-red-500' };
    
    let score = 0;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 1) return { level: 25, text: 'Weak', color: 'bg-red-500' };
    if (score === 2) return { level: 50, text: 'Fair', color: 'bg-yellow-500' };
    if (score === 3) return { level: 75, text: 'Good', color: 'bg-blue-500' };
    return { level: 100, text: 'Strong', color: 'bg-[#00FF94]' };
  };

  const strength = passwordStrength();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    
    setLoading(true);
    const result = await register(email, password, name);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error || 'Registration failed');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20" data-testid="register-page">
      <div className="w-full max-w-md">
        {/* Brand Lockup */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link to="/">
            <AuthBrandLockup showSubtitle={true} />
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="glass-card border-zinc-800" data-testid="register-card">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Create Account</CardTitle>
              <CardDescription>Start your AI trading journey today</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm text-zinc-400">Name</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <Input
                      type="text"
                      placeholder="Your name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                      required
                      data-testid="register-name-input"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-zinc-400">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                      required
                      data-testid="register-email-input"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-zinc-400">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Create a strong password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                      required
                      minLength={8}
                      data-testid="register-password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  
                  {/* Password strength indicator */}
                  {password && (
                    <div className="space-y-1">
                      <div className="h-1 rounded-full bg-zinc-800 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${strength.level}%` }}
                          className={`h-full ${strength.color}`}
                        />
                      </div>
                      <p className="text-xs text-zinc-500">{strength.text}</p>
                    </div>
                  )}
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    data-testid="register-error"
                  >
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </motion.div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-11"
                  data-testid="register-submit-btn"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      Create Account
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>

                <p className="text-xs text-zinc-500 text-center">
                  By signing up, you agree to our Terms of Service and Privacy Policy
                </p>
              </form>

              <div className="mt-6 text-center text-sm text-zinc-500">
                Already have an account?{' '}
                <Link to="/login" className="text-[#7B61FF] hover:underline" data-testid="login-link">
                  Sign in
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Benefits */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 space-y-3"
        >
          {[
            'Access to AI-powered trading signals',
            '15-minute delayed signals (Free tier)',
            'Paper trading with $10,000 virtual balance'
          ].map((benefit, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-zinc-400">
              <Check className="w-4 h-4 text-[#00FF94]" />
              {benefit}
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

// Forgot Password Page
export const ForgotPasswordPage = () => {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await forgotPassword(email);
    if (result.success) {
      setSent(true);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20" data-testid="forgot-password-page">
      <div className="w-full max-w-md">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link to="/">
            <AuthBrandLockup showSubtitle={true} />
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="glass-card border-zinc-800" data-testid="forgot-password-card">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Reset Password</CardTitle>
              <CardDescription>Enter your email to receive a reset link</CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatePresence mode="wait">
                {!sent ? (
                  <motion.form
                    key="form"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onSubmit={handleSubmit}
                    className="space-y-4"
                  >
                    <div className="space-y-2">
                      <label className="text-sm text-zinc-400">Email</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <Input
                          type="email"
                          placeholder="you@example.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="pl-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                          required
                          data-testid="forgot-email-input"
                        />
                      </div>
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-11"
                      data-testid="forgot-submit-btn"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Send Reset Link'
                      )}
                    </Button>
                  </motion.form>
                ) : (
                  <motion.div
                    key="success"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-4"
                  >
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#00FF94]/20 flex items-center justify-center">
                      <Check className="w-8 h-8 text-[#00FF94]" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Check Your Email</h3>
                    <p className="text-sm text-zinc-400 mb-4">
                      If an account exists for {email}, you'll receive a password reset link shortly.
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => setSent(false)}
                      className="border-zinc-700"
                    >
                      Send Again
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="mt-6 text-center text-sm text-zinc-500">
                Remember your password?{' '}
                <Link to="/login" className="text-[#7B61FF] hover:underline">
                  Sign in
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

// Reset Password Page
export const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { resetPassword } = useAuth();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const token = searchParams.get('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    const result = await resetPassword(token, password);
    
    if (result.success) {
      navigate('/login');
    } else {
      setError(result.error || 'Password reset failed');
    }
    
    setLoading(false);
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-20">
        <Card className="glass-card border-zinc-800 max-w-md w-full">
          <CardContent className="text-center py-8">
            <AlertCircle className="w-12 h-12 mx-auto text-red-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Invalid Reset Link</h3>
            <p className="text-sm text-zinc-400 mb-4">
              This password reset link is invalid or has expired.
            </p>
            <Link to="/forgot-password">
              <Button className="bg-[#7B61FF]">Request New Link</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20" data-testid="reset-password-page">
      <div className="w-full max-w-md">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link to="/">
            <AuthBrandLockup showSubtitle={true} />
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="glass-card border-zinc-800" data-testid="reset-password-card">
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl">Set New Password</CardTitle>
              <CardDescription>Choose a strong password for your account</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm text-zinc-400">New Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Create a new password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                      required
                      minLength={8}
                      data-testid="reset-password-input"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-zinc-400">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="pl-10 bg-[#050505] border-zinc-800 focus:border-[#7B61FF]"
                      required
                      data-testid="reset-confirm-password-input"
                    />
                  </div>
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    data-testid="reset-error"
                  >
                    <AlertCircle className="w-4 h-4" />
                    {error}
                  </motion.div>
                )}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-11"
                  data-testid="reset-submit-btn"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    'Reset Password'
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

// Email Verification Page
export const VerifyEmailPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { verifyEmail, isAuthenticated } = useAuth();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [error, setError] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus('error');
        setError('Invalid verification link');
        return;
      }

      const result = await verifyEmail(token);
      if (result.success) {
        setStatus('success');
      } else {
        setStatus('error');
        setError(result.error || 'Verification failed');
      }
    };

    verify();
  }, [token, verifyEmail]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-20" data-testid="verify-email-page">
      <Card className="glass-card border-zinc-800 max-w-md w-full">
        <CardContent className="text-center py-8">
          <AnimatePresence mode="wait">
            {status === 'verifying' && (
              <motion.div
                key="verifying"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Loader2 className="w-12 h-12 mx-auto animate-spin text-[#7B61FF] mb-4" />
                <h3 className="text-lg font-semibold mb-2">Verifying Email</h3>
                <p className="text-sm text-zinc-400">Please wait...</p>
              </motion.div>
            )}

            {status === 'success' && (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#00FF94]/20 flex items-center justify-center">
                  <Check className="w-8 h-8 text-[#00FF94]" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Email Verified!</h3>
                <p className="text-sm text-zinc-400 mb-4">
                  Your email has been successfully verified.
                </p>
                <Button
                  onClick={() => navigate(isAuthenticated ? '/dashboard' : '/login')}
                  className="bg-[#7B61FF]"
                >
                  {isAuthenticated ? 'Go to Dashboard' : 'Sign In'}
                </Button>
              </motion.div>
            )}

            {status === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <AlertCircle className="w-12 h-12 mx-auto text-red-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Verification Failed</h3>
                <p className="text-sm text-zinc-400 mb-4">{error}</p>
                <Link to="/login">
                  <Button className="bg-[#7B61FF]">Go to Login</Button>
                </Link>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </div>
  );
};
