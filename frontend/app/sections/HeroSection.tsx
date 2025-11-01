"use client";

import React from 'react';
import { AnimatedButton } from '../components';

interface HeroSectionProps {
  isVisible: boolean;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ isVisible }) => {
  return (
    <div className={`text-center space-y-8 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
      <div className="inline-block px-4 py-2 bg-blue-500/20 border border-blue-400/30 rounded-full backdrop-blur-sm">
        <span className="text-blue-300 text-sm font-medium">✨ Bem-vindo à nova era da tecnologia</span>
      </div>
      
      <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold leading-tight">
        <span className="block text-white mb-2">Construindo o</span>
        <span className="block bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-gradient">
          Futuro Digital
        </span>
      </h1>

      <p className="text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
        Transformamos ideias em experiências digitais extraordinárias.
        <br />
        Inovação, criatividade e tecnologia de ponta ao seu alcance.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
        <AnimatedButton variant="primary">
          Começar Agora
        </AnimatedButton>
        
        <AnimatedButton variant="secondary">
          Saber Mais →
        </AnimatedButton>
      </div>
    </div>
  );
};

