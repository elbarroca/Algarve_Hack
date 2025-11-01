"use client";

import React from 'react';

export const AboutSection: React.FC = () => {
  const values = [
    {
      icon: '💡',
      title: 'Inovação',
      description: 'Buscamos constantemente novas soluções e abordagens criativas',
    },
    {
      icon: '🤝',
      title: 'Colaboração',
      description: 'Trabalhamos em equipa para alcançar os melhores resultados',
    },
    {
      icon: '🎯',
      title: 'Excelência',
      description: 'Comprometidos com a qualidade em cada projeto',
    },
  ];

  return (
    <section id="about" className="relative py-32 px-8 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Sobre Nós
        </h2>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          Somos uma equipa apaixonada por tecnologia, dedicada a transformar ideias em soluções digitais inovadoras
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
        {values.map((value, index) => (
          <div
            key={index}
            className="text-center space-y-4 p-8 bg-slate-800/30 backdrop-blur-sm rounded-2xl border border-slate-700/30 hover:border-slate-600 hover:scale-105 transition-all duration-300"
          >
            <div className="text-6xl">{value.icon}</div>
            <h3 className="text-2xl font-bold text-white">{value.title}</h3>
            <p className="text-slate-400">{value.description}</p>
          </div>
        ))}
      </div>

      <div className="mt-20 p-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl backdrop-blur-sm">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h3 className="text-3xl font-bold text-white mb-4">Nossa Missão</h3>
            <p className="text-slate-300 leading-relaxed">
              Capacitar empresas e indivíduos através da tecnologia, criando soluções que 
              fazem a diferença no mundo real. Acreditamos que a inovação surge quando 
              criatividade e tecnologia se encontram.
            </p>
          </div>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                <span className="text-2xl">✓</span>
              </div>
              <span className="text-slate-300">Soluções personalizadas</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                <span className="text-2xl">✓</span>
              </div>
              <span className="text-slate-300">Tecnologias de ponta</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center">
                <span className="text-2xl">✓</span>
              </div>
              <span className="text-slate-300">Suporte dedicado</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

