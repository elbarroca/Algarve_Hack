import React from 'react';

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  gradient: string;
  isActive?: boolean;
  onHover?: (isHovered: boolean) => void;
  delay?: number;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  gradient,
  isActive = false,
  onHover,
  delay = 0,
}) => {
  return (
    <div
      onMouseEnter={() => onHover?.(true)}
      onMouseLeave={() => onHover?.(false)}
      className={`group relative p-6 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-slate-600 transform hover:scale-105 transition-all duration-500 cursor-pointer ${
        isActive ? 'shadow-2xl shadow-blue-500/30' : ''
      }`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity duration-500`} />
      
      <div className="relative z-10 space-y-4">
        <div className="text-5xl transform group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors duration-300">
          {title}
        </h3>
        <p className="text-slate-400 leading-relaxed">
          {description}
        </p>
      </div>

      <div className={`absolute -bottom-1 left-0 right-0 h-1 bg-gradient-to-r ${gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-full`} />
    </div>
  );
};

