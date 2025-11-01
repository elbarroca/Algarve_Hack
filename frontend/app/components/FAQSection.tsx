// Minimalist FAQ Section - Static Data (No API needed)
"use client";

import React, { useState } from 'react';
import { FAQItem } from '../types/api';

export const FAQSection: React.FC = () => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  
  const faqs: FAQItem[] = [
    {
      question: 'O que é caução e quanto devo pagar?',
      answer: 'A caução (depósito de segurança) é normalmente equivalente a 1-2 meses de renda. Deve ser devolvida no final do contrato, descontando eventuais danos.',
      links: [
        {
          title: 'Portal da Habitação - Caução',
          url: 'https://www.portaldahabitacao.pt/arrendamento',
        },
      ],
    },
    {
      question: 'Posso pedir recibo de renda eletrónico?',
      answer: 'Sim! O senhorio é obrigado a emitir recibos de renda. Pode ser em papel ou através do Portal das Finanças (e-fatura).',
      links: [
        {
          title: 'E-fatura - Portal das Finanças',
          url: 'https://faturas.portaldasfinancas.gov.pt/',
        },
      ],
    },
    {
      question: 'Qual a diferença entre AL e Arrendamento?',
      answer: 'AL (Alojamento Local) é para estadias curtas/turísticas. Arrendamento é para longa duração (mínimo 30 dias, normalmente 1 ano+).',
      links: [
        {
          title: 'Lei do Alojamento Local',
          url: 'https://www.turismodeportugal.pt/',
        },
      ],
    },
    {
      question: 'Preciso de fiador para arrendar?',
      answer: 'Depende do senhorio. Alguns pedem fiador (pessoa que garante o pagamento), especialmente para estudantes ou primeiro arrendamento.',
      links: [
        {
          title: 'Guia de Arrendamento',
          url: 'https://www.portaldahabitacao.pt/',
        },
      ],
    },
    {
      question: 'Quanto tempo demora o contrato?',
      answer: 'Contratos de arrendamento são normalmente de 1 ano mínimo. Podem ser renovados automaticamente ou por acordo.',
      links: [
        {
          title: 'NRAU - Novo Regime do Arrendamento Urbano',
          url: 'https://dre.pt/',
        },
      ],
    },
    {
      question: 'O que está incluído na renda?',
      answer: 'Normalmente a renda não inclui água, luz, gás e internet. Confirme sempre com o senhorio o que está incluído.',
    },
    {
      question: 'Posso rescindir o contrato antes do fim?',
      answer: 'Sim, com aviso prévio (normalmente 2-3 meses). Pode haver penalizações dependendo do contrato.',
      links: [
        {
          title: 'Rescisão de Contrato',
          url: 'https://www.portaldahabitacao.pt/arrendamento',
        },
      ],
    },
    {
      question: 'Como funciona o IRS no arrendamento?',
      answer: 'Como inquilino, pode deduzir parte da renda no IRS (até 15% com limite de €502). Guarde todos os recibos!',
      links: [
        {
          title: 'Benefícios Fiscais - Portal das Finanças',
          url: 'https://info.portaldasfinancas.gov.pt/',
        },
      ],
    },
  ];

  const toggleFAQ = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Perguntas Frequentes
        </h2>
        <p className="text-sm text-gray-600">
          Informações sobre arrendamento em Portugal
        </p>
      </div>

      {/* FAQ Items */}
      <div className="space-y-3">
        {faqs.map((faq, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg overflow-hidden transition-all hover:border-gray-300"
          >
            <button
              onClick={() => toggleFAQ(index)}
              className="w-full flex items-start gap-3 p-4 text-left hover:bg-gray-50 transition-colors"
            >
              <span className="text-blue-600 font-bold mt-0.5">
                {expandedIndex === index ? '▼' : '▶'}
              </span>
              <div className="flex-1">
                <h3 className="text-gray-900 font-medium">{faq.question}</h3>
              </div>
            </button>

            {expandedIndex === index && (
              <div className="px-4 pb-4 pl-11 space-y-3">
                <p className="text-gray-700 leading-relaxed text-sm">{faq.answer}</p>

                {faq.links && faq.links.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs text-gray-500 font-medium">
                      Links úteis:
                    </p>
                    {faq.links.map((link, linkIndex) => (
                      <a
                        key={linkIndex}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-700 hover:underline transition-colors"
                      >
                        → {link.title}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
        ⚠️ <strong>Aviso:</strong> Esta informação é apenas educativa e não constitui aconselhamento jurídico. 
        Para questões específicas, consulte um advogado especializado.
      </div>
    </div>
  );
};
