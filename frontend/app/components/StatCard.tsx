import React from 'react';

interface StatCardProps {
  value: string;
  label: string;
  delay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({ value, label, delay = 0 }) => {
  return (
    <div
      className="text-center space-y-2 p-6 bg-slate-800/30 backdrop-blur-sm rounded-xl border border-slate-700/30 hover:border-slate-600 transition-all duration-300 hover:scale-105"
      style={{ transitionDelay: `${delay}ms` }}
    >
      <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
        {value}
      </div>
      <div className="text-slate-400 font-medium">
        {label}
      </div>
    </div>
  );
};

