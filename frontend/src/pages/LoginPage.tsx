import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Rocket, Lock, Mail, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (type: 'admin' | 'researcher') => {
    if (type === 'admin') {
      setEmail('admin@missionmind.ai');
      setPassword('Aerospace@2026');
    } else {
      setEmail('researcher@missionmind.ai');
      setPassword('Aerospace@2026');
    }
  };

  return (
    <div className="min-h-screen bg-space-950 flex flex-col justify-center items-center px-4 relative">
      <div className="w-full max-w-md bg-space-900 border border-space-700 rounded-3xl p-8 shadow-2xl relative z-10">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cosmic-violet to-cosmic-purple flex items-center justify-center mx-auto shadow-lg shadow-purple-500/20 mb-3">
            <Rocket className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-white">MISSIONMIND AI</h2>
          <p className="text-xs text-slate-400 mt-1">Flight Deck Sign In</p>
        </div>

        {error && <div className="mb-4"><ErrorMessage message={error} /></div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              ENGINEER EMAIL
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="engineer@agency.gov"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              SECURITY KEY / PASSWORD
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple transition-colors"
              />
            </div>
          </div>

          <Button
            type="submit"
            variant="primary"
            className="w-full py-2.5 text-xs font-bold"
            isLoading={loading}
          >
            Authenticate & Enter
          </Button>
        </form>

        {/* Quick Demo Credentials for Hackathon Evaluator */}
        <div className="mt-6 pt-5 border-t border-space-800">
          <p className="text-[10px] text-slate-400 font-mono text-center mb-2 uppercase">
            Hackathon One-Click Test Accounts
          </p>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('admin')}
              className="py-1.5 px-2 rounded-lg bg-space-850 hover:bg-space-800 border border-space-700 text-[11px] text-cosmic-purple font-mono transition-colors"
            >
              Demo Admin
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('researcher')}
              className="py-1.5 px-2 rounded-lg bg-space-850 hover:bg-space-800 border border-space-700 text-[11px] text-cosmic-cyan font-mono transition-colors"
            >
              Demo Analyst
            </button>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          New researcher?{' '}
          <Link to="/register" className="text-cosmic-purple font-semibold hover:underline">
            Register Account
          </Link>
        </p>
      </div>
    </div>
  );
};
