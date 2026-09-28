import React, { useState } from 'react';
import { Mail, Lock, User, Eye, EyeOff, Sparkles, ShieldCheck, ArrowRight } from 'lucide-react';
import { loginUser, signupUser } from '../api/authApi';

function AuthScreen({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let res;
      if (isLogin) {
        res = await loginUser(email, password);
      } else {
        res = await signupUser(name, email, password);
      }
      if (res?.user) {
        onAuthSuccess(res.user);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = async () => {
    setLoading(true);
    try {
      const res = await loginUser('balkisu@docta.ng', 'demo1234');
      if (res?.user) {
        onAuthSuccess(res.user);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f7f8fa] flex flex-col justify-between px-4 py-8 max-w-md mx-auto animate-fade-in select-none">
      {/* 1. Brand Logo & Headline */}
      <div className="text-center pt-4 pb-6">
        <div className="flex items-center justify-center mb-3">
          <img
            src="/docta-logo.svg"
            alt="docta"
            className="h-12 sm:h-14 object-contain"
            onError={(e) => {
              // Fallback text logo if image is loading
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <h1 className="text-4xl font-extrabold text-[#16a34a] tracking-tight hidden" style={{ display: 'none' }}>
            docta
          </h1>
        </div>
        <p className="text-[13px] text-gray-500 font-medium">
          African Multimodal Dietary Intelligence
        </p>
      </div>

      {/* 2. Main Authentication Card */}
      <div className="bg-white rounded-[28px] p-6 sm:p-7 shadow-xs border border-gray-100/70 w-full mb-6">
        {/* Toggle Pill Switcher */}
        <div className="bg-gray-100/80 p-1 rounded-full flex gap-1 mb-6">
          <button
            type="button"
            onClick={() => {
              setIsLogin(true);
              setError(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all duration-200 ${
              isLogin
                ? 'bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-xs scale-100'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Log In
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLogin(false);
              setError(null);
            }}
            className={`flex-1 py-2 text-xs font-bold rounded-full transition-all duration-200 ${
              !isLogin
                ? 'bg-gradient-to-tr from-[#bef264] to-[#d9f99d] text-gray-950 shadow-xs scale-100'
                : 'text-gray-500 hover:text-gray-900'
            }`}
          >
            Sign Up
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-4 bg-rose-50 border border-rose-200/80 text-rose-700 text-xs px-3.5 py-2.5 rounded-2xl font-semibold animate-fade-in">
            {error}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {/* Full Name for Sign Up */}
          {!isLogin && (
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-1.5 px-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Balkisu Habib"
                  className="w-full pl-11 pr-4 py-3 bg-[#f8fafc] border border-gray-100 rounded-2xl text-[14px] text-gray-900 placeholder:text-gray-400 outline-none focus:bg-white focus:ring-2 focus:ring-lime-300/40 focus:border-lime-400 transition-all font-medium"
                />
              </div>
            </div>
          )}

          {/* Email Address */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-1.5 px-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@domain.com"
                className="w-full pl-11 pr-4 py-3 bg-[#f8fafc] border border-gray-100 rounded-2xl text-[14px] text-gray-900 placeholder:text-gray-400 outline-none focus:bg-white focus:ring-2 focus:ring-lime-300/40 focus:border-lime-400 transition-all font-medium"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-1.5 px-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-11 pr-11 py-3 bg-[#f8fafc] border border-gray-100 rounded-2xl text-[14px] text-gray-900 placeholder:text-gray-400 outline-none focus:bg-white focus:ring-2 focus:ring-lime-300/40 focus:border-lime-400 transition-all font-medium"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Primary Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gray-950 hover:bg-black text-white font-bold py-3.5 rounded-full text-[14px] shadow-lg shadow-black/10 transition-transform active:scale-98 disabled:opacity-50 mt-2 flex items-center justify-center gap-2"
          >
            <span>{loading ? 'Processing...' : isLogin ? 'Sign In' : 'Create Account'}</span>
            {!loading && <ArrowRight className="w-4 h-4 stroke-[2.5]" />}
          </button>
        </form>

        {/* Quick Demo Access Divider */}
        <div className="relative my-5 text-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-100" />
          </div>
          <span className="relative bg-white px-3 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
            or explore
          </span>
        </div>

        {/* Quick 1-Click Demo Login */}
        <button
          type="button"
          onClick={handleQuickDemo}
          disabled={loading}
          className="w-full bg-[#e3f79e] hover:bg-[#d5ee8c] text-gray-950 font-bold py-3 rounded-full text-[13px] shadow-2xs transition-transform active:scale-98 flex items-center justify-center gap-1.5"
        >
          <Sparkles className="w-4 h-4 text-gray-900 stroke-[2.2]" />
          <span>Quick Demo Sign In</span>
        </button>
      </div>

      {/* 3. Security & WAFCT Footnote */}
      <div className="text-center pb-4">
        <div className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-gray-400 bg-white px-3 py-1.5 rounded-full border border-gray-100 shadow-2xs">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Active Learning & WAFCT Encrypted</span>
        </div>
      </div>
    </div>
  );
}

export default AuthScreen;
