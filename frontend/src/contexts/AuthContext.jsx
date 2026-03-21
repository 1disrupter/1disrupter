/**
 * AlphaAI Authentication Context
 * Manages user authentication state, JWT tokens, and 2FA
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokens, setTokens] = useState(() => {
    const stored = localStorage.getItem('alphaai_tokens');
    return stored ? JSON.parse(stored) : null;
  });

  // Configure axios interceptor for auth headers
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        if (tokens?.access_token && config.url.startsWith(API)) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => axios.interceptors.request.eject(interceptor);
  }, [tokens]);

  // Response interceptor for token refresh
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry && tokens?.refresh_token) {
          originalRequest._retry = true;
          
          try {
            const response = await axios.post(`${API}/auth/refresh`, {
              refresh_token: tokens.refresh_token
            });
            
            const newTokens = {
              access_token: response.data.access_token,
              refresh_token: response.data.refresh_token
            };
            
            setTokens(newTokens);
            localStorage.setItem('alphaai_tokens', JSON.stringify(newTokens));
            setUser(response.data.user);
            
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
            return axios(originalRequest);
          } catch (refreshError) {
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );

    return () => axios.interceptors.response.eject(interceptor);
  }, [tokens]);

  // Load user on mount if tokens exist
  useEffect(() => {
    const loadUser = async () => {
      if (tokens?.access_token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${tokens.access_token}` }
          });
          setUser(response.data);
        } catch (error) {
          console.error('Failed to load user:', error);
          // Token might be expired, try refresh
          if (tokens.refresh_token) {
            try {
              const refreshResponse = await axios.post(`${API}/auth/refresh`, {
                refresh_token: tokens.refresh_token
              });
              
              const newTokens = {
                access_token: refreshResponse.data.access_token,
                refresh_token: refreshResponse.data.refresh_token
              };
              
              setTokens(newTokens);
              localStorage.setItem('alphaai_tokens', JSON.stringify(newTokens));
              setUser(refreshResponse.data.user);
            } catch {
              logout();
            }
          } else {
            logout();
          }
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  const register = async (email, password, name) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        name
      });
      
      const newTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      };
      
      setTokens(newTokens);
      localStorage.setItem('alphaai_tokens', JSON.stringify(newTokens));
      setUser(response.data.user);
      
      toast.success('Account created! Please check your email to verify.');
      return { success: true, user: response.data.user };
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const login = async (email, password, totpCode = null) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password,
        totp_code: totpCode
      });
      
      const newTokens = {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token
      };
      
      setTokens(newTokens);
      localStorage.setItem('alphaai_tokens', JSON.stringify(newTokens));
      setUser(response.data.user);
      
      toast.success('Welcome back!');
      return { success: true, user: response.data.user };
    } catch (error) {
      const detail = error.response?.data?.detail;
      
      // Check if 2FA is required
      if (detail?.requires_2fa) {
        return { success: false, requires2FA: true };
      }
      
      const message = typeof detail === 'string' ? detail : 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const logout = useCallback(async () => {
    try {
      if (tokens?.access_token) {
        await axios.post(`${API}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${tokens.access_token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    setUser(null);
    setTokens(null);
    localStorage.removeItem('alphaai_tokens');
    toast.info('Logged out');
  }, [tokens]);

  const forgotPassword = async (email) => {
    try {
      await axios.post(`${API}/auth/forgot-password`, { email });
      toast.success('If an account exists, a reset link has been sent');
      return { success: true };
    } catch (error) {
      toast.error('Failed to send reset email');
      return { success: false };
    }
  };

  const resetPassword = async (token, newPassword) => {
    try {
      await axios.post(`${API}/auth/reset-password`, {
        token,
        new_password: newPassword
      });
      toast.success('Password reset successfully! Please login.');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Password reset failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const verifyEmail = async (token) => {
    try {
      await axios.post(`${API}/auth/verify-email`, { token });
      
      // Refresh user data
      if (tokens?.access_token) {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
      }
      
      toast.success('Email verified!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Verification failed';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const linkWallet = async (walletAddress) => {
    try {
      await axios.post(`${API}/auth/link-wallet`, { wallet_address: walletAddress });
      
      // Refresh user data
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      
      toast.success('Wallet linked successfully!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to link wallet';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const enable2FA = async () => {
    try {
      const response = await axios.post(`${API}/auth/2fa/enable`);
      return { 
        success: true, 
        secret: response.data.secret,
        qrCode: response.data.qr_code,
        backupCodes: response.data.backup_codes
      };
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to enable 2FA';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const verify2FA = async (totpCode) => {
    try {
      await axios.post(`${API}/auth/2fa/verify`, { totp_code: totpCode });
      
      // Refresh user data
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      
      toast.success('2FA enabled successfully!');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Invalid verification code';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const disable2FA = async (totpCode) => {
    try {
      await axios.post(`${API}/auth/2fa/disable`, { totp_code: totpCode });
      
      // Refresh user data
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      
      toast.success('2FA disabled');
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || 'Invalid verification code';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  const refreshUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to refresh user:', error);
      return null;
    }
  };

  const value = {
    user,
    tokens,
    loading,
    isAuthenticated: !!user,
    isPro: user?.is_pro || user?.is_elite,
    isElite: user?.is_elite,
    register,
    login,
    logout,
    forgotPassword,
    resetPassword,
    verifyEmail,
    linkWallet,
    enable2FA,
    verify2FA,
    disable2FA,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
