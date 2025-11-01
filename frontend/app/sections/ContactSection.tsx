"use client";

import React from 'react';
import { ContactForm } from '../components';

export const ContactSection: React.FC = () => {
  return (
    <section id="contact" className="relative py-32 px-8 max-w-7xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
          Entre em Contacto
        </h2>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          Tem um projeto em mente? Vamos conversar e transformá-lo em realidade
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Contact Information */}
        <div className="space-y-8">
          <div className="p-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl">
            <h3 className="text-2xl font-bold text-white mb-6">Informações</h3>
            
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl">📍</span>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-1">Localização</h4>
                  <p className="text-slate-400">Algarve, Portugal</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl">📧</span>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-1">Email</h4>
                  <p className="text-slate-400">info@algarvehack.pt</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl">📱</span>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-1">Telefone</h4>
                  <p className="text-slate-400">+351 XXX XXX XXX</p>
                </div>
              </div>

              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl">⏰</span>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-1">Horário</h4>
                  <p className="text-slate-400">Segunda a Sexta: 9h - 18h</p>
                </div>
              </div>
            </div>
          </div>

          <div className="p-8 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-2xl backdrop-blur-sm">
            <h3 className="text-xl font-bold text-white mb-4">💬 Resposta Rápida</h3>
            <p className="text-slate-300">
              Respondemos a todas as mensagens em até 24 horas. 
              Para questões urgentes, contacte-nos por telefone.
            </p>
          </div>
        </div>

        {/* Contact Form */}
        <div className="p-8 bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-2xl">
          <h3 className="text-2xl font-bold text-white mb-6">Envie uma Mensagem</h3>
          <ContactForm />
        </div>
      </div>
    </section>
  );
};

