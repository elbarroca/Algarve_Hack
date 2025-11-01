"use client";

import { useState, useEffect } from "react";
import {
  FeatureCard,
  NavigationBar,
  StatCard,
  BackgroundEffects,
  Footer
} from "./components";
import {
  HeroSection,
  AboutSection,
  ServicesSection,
  ContactSection
} from "./sections";

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);
  const [activeCard, setActiveCard] = useState<number | null>(null);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const features = [
    {
      icon: "🚀",
      title: "Inovação Rápida",
      description: "Desenvolvimento ágil com as tecnologias mais modernas do mercado",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: "🎯",
      title: "Foco em Resultados",
      description: "Soluções práticas e eficientes que geram impacto real",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: "🌊",
      title: "Espírito Algarve",
      description: "Combinando a criatividade local com alcance global",
      gradient: "from-emerald-500 to-teal-500"
    },
    {
      icon: "⚡",
      title: "Performance",
      description: "Otimizado para velocidade e escalabilidade máximas",
      gradient: "from-orange-500 to-red-500"
    }
  ];

  const stats = [
    { value: "100+", label: "Projetos" },
    { value: "50+", label: "Clientes" },
    { value: "24/7", label: "Suporte" },
    { value: "99%", label: "Satisfação" }
  ];

  return (
    <div className="relative min-h-screen w-full bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 overflow-hidden">
      <BackgroundEffects />
      <NavigationBar />

      {/* Hero Section */}
      <main id="home" className="relative z-10 flex flex-col items-center justify-center px-8 pt-32 pb-32 max-w-7xl mx-auto">
        <HeroSection isVisible={isVisible} />

        {/* Features Grid */}
        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-32 w-full transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              gradient={feature.gradient}
              isActive={activeCard === index}
              onHover={(isHovered) => setActiveCard(isHovered ? index : null)}
              delay={index * 100}
            />
          ))}
        </div>

        {/* Stats Section */}
        <div className={`grid grid-cols-2 md:grid-cols-4 gap-8 mt-32 w-full transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
          {stats.map((stat, index) => (
            <StatCard
              key={index}
              value={stat.value}
              label={stat.label}
              delay={index * 100}
            />
          ))}
        </div>
      </main>

      {/* Additional Sections */}
      <AboutSection />
      <ServicesSection />
      <ContactSection />

      <Footer />
    </div>
  );
}
