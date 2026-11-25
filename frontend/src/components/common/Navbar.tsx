import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Rocket, Shield, LogOut, User as UserIcon, BookOpen, Cpu, Orbit } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-16 border-b border-space-700 bg-space-900/90 backdrop-blur-md sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cosmic-violet to-cosmic-purple flex items-center justify-center shadow-lg shadow-purple-500/20 group-hover:scale-105 transition-transform">
            <Rocket className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold text-base tracking-wider text-white">MISSIONMIND</span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-cosmic-purple/20 text-cosmic-purple border border-cosmic-purple/30">AI</span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-tight hidden sm:block">NASA & ISRO Cited Lessons Learned</p>
          </div>
        </Link>
      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400 bg-space-850 px-3 py-1.5 rounded-full border border-space-700">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Knowledge Base: <b>NASA & ISRO Public Records</b></span>
        </div>

        {user ? (
          <div className="flex items-center space-x-3">
            <Link
              to="/settings"
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-space-850 border border-space-700 hover:border-cosmic-purple/50 text-xs text-slate-200 transition-colors"
            >
              <UserIcon className="w-3.5 h-3.5 text-cosmic-purple" />
              <span>{user.name.split(' ')[0]}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-space-700 text-slate-300 font-mono uppercase">{user.role}</span>
            </Link>
            <button
              onClick={() => { logout(); navigate('/'); }}
              className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-space-800 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <Link
              to="/login"
              className="text-xs px-3.5 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-space-800 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-xs px-3.5 py-1.5 rounded-lg bg-cosmic-violet hover:bg-cosmic-purple text-white font-medium shadow-md shadow-purple-600/20 transition-all"
            >
              Access Flight Deck
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};
