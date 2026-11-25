import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Brain,
  Layers,
  GitFork,
  FileText,
  FileBarChart,
  Settings,
  ShieldCheck,
  Compass,
  Radio
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();

  const links = [
    { to: '/dashboard', label: 'Command Deck', icon: LayoutDashboard },
    { to: '/assistant', label: 'AI Research Assistant', icon: Brain, badge: 'RAG' },
    { to: '/similar-failures', label: 'Similar Past Failures', icon: Layers, badge: 'Intelligence' },
    { to: '/failure-chain', label: 'Failure Chain Analyzer', icon: GitFork },
    { to: '/documents', label: 'Mission Document Library', icon: FileText },
    { to: '/reports', label: 'Research Reports', icon: FileBarChart, badge: 'PDF' },
    { to: '/settings', label: 'Settings & Security', icon: Settings },
  ];

  if (user?.role === 'admin') {
    links.push({ to: '/admin', label: 'Mission Operations Admin', icon: ShieldCheck, badge: 'Admin' });
  }

  return (
    <aside className="w-64 border-r border-space-700 bg-space-900/50 flex flex-col justify-between p-4 shrink-0 hidden lg:flex">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2 font-mono">
            FLIGHT DECK MODULES
          </p>
          <nav className="space-y-1">
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-cosmic-purple/15 text-cosmic-purple border border-cosmic-purple/30 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-space-850'
                    }`
                  }
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{link.label}</span>
                  </div>
                  {link.badge && (
                    <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-space-800 text-slate-300 border border-space-700">
                      {link.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="p-3.5 rounded-xl bg-space-850 border border-space-700 text-xs">
          <div className="flex items-center space-x-2 text-cosmic-cyan mb-1.5">
            <Radio className="w-4 h-4 animate-spin text-cosmic-cyan" />
            <span className="font-semibold tracking-wide uppercase text-[10px]">Verification Policy</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Strict evidence grounding active. Every citation verified against official NASA/ISRO report pages.
          </p>
        </div>
      </div>

      <div className="pt-4 border-t border-space-800 text-[11px] text-slate-500 flex items-center justify-between font-mono">
        <span>MISSIONMIND v1.0</span>
        <span className="text-emerald-400 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> ONLINE
        </span>
      </div>
    </aside>
  );
};
