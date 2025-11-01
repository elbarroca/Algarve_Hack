import React from 'react';

interface AnimatedButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

export const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  onClick,
  className = '',
  disabled = false,
}) => {
  const baseStyles = 'relative overflow-hidden font-semibold rounded-xl transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100';
  
  const variantStyles = {
    primary: 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50 hover:shadow-blue-500/80',
    secondary: 'bg-slate-800/50 backdrop-blur-sm border border-slate-700 text-white hover:bg-slate-800 hover:border-slate-600',
    outline: 'border-2 border-blue-500 text-blue-400 hover:bg-blue-500/10',
  };
  
  const sizeStyles = {
    small: 'px-4 py-2 text-sm',
    medium: 'px-8 py-4 text-base',
    large: 'px-10 py-5 text-lg',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      <span className="relative z-10">{children}</span>
      {variant === 'primary' && (
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-700 rounded-xl opacity-0 hover:opacity-100 transition-opacity duration-300" />
      )}
    </button>
  );
};

