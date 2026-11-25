import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Rocket, User as UserIcon, Mail, Lock, Shield } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/common/Button';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('analyst');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({ name, email, password, role });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Email may already be in use.');
    } finally {
      setLoading(false);
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
          <p className="text-xs text-slate-400 mt-1">Create Researcher Profile</p>
        </div>

        {error && <div className="mb-4"><ErrorMessage message={error} /></div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              FULL NAME & CALLSIGN
            </label>
            <div className="relative">
              <UserIcon className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Dr. Vikram Sarabhai"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              OFFICIAL EMAIL
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="sarabhai@isro.gov.in"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              ROLE CLASSIFICATION
            </label>
            <div className="relative">
              <Shield className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-space-850 border border-space-700 text-xs text-white focus:outline-none focus:border-cosmic-purple transition-colors cursor-pointer"
              >
                <option value="analyst">Aerospace Research Analyst</option>
                <option value="admin">Mission Safety Director (Admin)</option>
                <option value="student">Graduate Aerospace Student</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono">
              SECURITY KEY
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
            Register Aerospace Profile
          </Button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          Already registered?{' '}
          <Link to="/login" className="text-cosmic-purple font-semibold hover:underline">
            Sign In Here
          </Link>
        </p>
      </div>
    </div>
  );
};
