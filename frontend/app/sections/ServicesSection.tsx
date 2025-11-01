"use client";

import React from 'react';

export const ServicesSection: React.FC = () => {
  const services = [
    {
      icon: '🌐',
      title: 'Desenvolvimento Web',
      description: 'Websites e aplicações web modernas, responsivas e performáticas',
      features: ['React & Next.js', 'UI/UX Design', 'SEO Optimization'],
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: '📱',
      title: 'Apps Mobile',
      description: 'Aplicações móveis nativas e híbridas para iOS e Android',
      features: ['React Native', 'Flutter', 'App Store Deploy'],
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: '☁️',
      title: 'Cloud & DevOps',
      description: 'Infraestrutura cloud escalável e pipelines de CI/CD',
      features: ['AWS & Azure', 'Docker & K8s', 'Automation'],
      color: 'from-emerald-500 to-teal-500',
    },
    {
      icon: '🤖',
      title: 'AI & Machine Learning',
      description: 'Soluções inteligentes com inteligência artificial',
      features: ['NLP', 'Computer Vision', 'Predictive Analytics'],
      color: 'from-orange-500 to-red-500',
    },
  ];

  return (
    <section id="services" className="relative py-32 px-8 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Nossos Serviços
        </h2>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          Oferecemos uma gama completa de serviços de desenvolvimento tecnológico
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {services.map((service, index) => (
          <div
            key={index}
            className="group relative p-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl hover:border-slate-600 transform hover:scale-105 transition-all duration-500"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${service.color} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity duration-500`} />
            
            <div className="relative z-10 space-y-4">
              <div className="text-6xl">{service.icon}</div>
              
              <h3 className="text-2xl font-bold text-white group-hover:text-blue-300 transition-colors duration-300">
                {service.title}
              </h3>
              
              <p className="text-slate-400 leading-relaxed">
                {service.description}
              </p>

              <div className="flex flex-wrap gap-2 pt-4">
                {service.features.map((feature, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 text-xs font-medium bg-blue-500/10 text-blue-300 border border-blue-500/30 rounded-full"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>

            <div className={`absolute -bottom-1 left-0 right-0 h-1 bg-gradient-to-r ${service.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-full`} />
          </div>
        ))}
      </div>
    </section>
  );
};

