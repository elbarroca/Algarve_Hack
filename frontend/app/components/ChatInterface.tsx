// Beautiful Chat Interface - Modern & Appealing
"use client";

import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, PropertyListing, ChatResponse } from '../types/api';
import { realAPI } from '../services/api';

interface ChatInterfaceProps {
  onPropertiesFound?: (properties: PropertyListing[]) => void;
  onMessageReceived?: (message: string, isComplete: boolean) => void;
  onRawSearchResults?: (results: any[]) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onPropertiesFound,
  onMessageReceived,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Olá! 👋 Sou o seu assistente de procura de casa no Algarve.\n\nPosso ajudá-lo a encontrar a propriedade perfeita. Como posso ajudá-lo hoje?',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
    checkConnection();
  }, [messages]);

  const checkConnection = async () => {
    const connected = await realAPI.healthCheck();
    setIsConnected(connected);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const query = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await realAPI.sendChatMessage(query);

      if (response.status === 'error') {
        throw new Error(response.data.message || 'Erro ao processar mensagem');
      }

      const agentMessage = response.data.search_summary || response.data.message || 'Desculpe, não consegui processar sua mensagem.';
      
      // Parse properties from raw_search_results or properties array
      let properties: PropertyListing[] = [];
      const responseData = response.data as ChatResponse['data'];
      
      if (responseData.raw_search_results && responseData.raw_search_results.length > 0) {
        // Convert raw_search_results to PropertyListing format
        properties = responseData.raw_search_results.map((result: any) => ({
          address: result.title || result.address || 'Endereço não disponível',
          city: result.location || extractCityFromTitle(result.title || ''),
          price: extractPrice(result.title || result.description || ''),
          bedrooms: extractBedrooms(result.title || result.description || ''),
          bathrooms: extractBathrooms(result.description || ''),
          description: result.description || '',
          url: result.link || result.url || '',
          latitude: result.latitude,
          longitude: result.longitude,
          image_url: result.image_url,
        }));
      } else if (responseData.properties && responseData.properties.length > 0) {
        properties = responseData.properties;
      }
      
      const isComplete = responseData.is_complete || false;

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: agentMessage,
        timestamp: new Date(),
        properties: properties.length > 0 ? properties : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (properties.length > 0 && onPropertiesFound) {
        onPropertiesFound(properties);
      }

      if (onMessageReceived) {
        onMessageReceived(agentMessage, isComplete);
      }
    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Desculpe, ocorreu um erro: ${error.message || 'Erro desconhecido'}. Verifique se o backend está rodando na porta 8080.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Helper functions to parse property data from search results
  const extractCityFromTitle = (title: string): string => {
    // Comprehensive Algarve municipalities + major localities/resorts
    const cities = [
      // Municipalities (16)
      'Albufeira','Alcoutim','Aljezur','Castro Marim','Faro','Lagoa','Lagos','Loulé','Monchique','Olhão','Portimão','São Brás de Alportel','Silves','Tavira','Vila do Bispo','Vila Real de Santo António',
      // Major localities & resorts often used in listings
      'Vilamoura','Quarteira','Almancil','Quinta do Lago','Vale do Lobo','Armação de Pêra','Porches','Carvoeiro','Ferragudo','Estômbar','Parchal','Alvor','Praia da Rocha','Mexilhoeira Grande','Meia Praia',
      'Luz','Praia da Luz','Burgau','Salema','Sagres','Budens','Monte Gordo','Altura','Manta Rota','Cacela','Cabanas de Tavira','Cabanas','Santa Luzia','Conceição de Tavira','Conceição',
      'Santa Catarina da Fonte do Bispo','Moncarapacho','Fuseta','Odiáxere','Bensafrim','Barão de São João','Marmelete','Alferce','São Marcos da Serra','São Bartolomeu de Messines','Pêra','Algoz','Tunes',
      'Ferreiras','Guia','Paderne','Boliqueime','Benafim','Querença','Tôr','Salir','Ameixial'
    ];

    // Normalize to compare without diacritics and case
    const normalize = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const normTitle = normalize(title);

    for (const city of cities) {
      if (normTitle.includes(normalize(city))) {
        return city; // return the canonical label as listed above
      }
    }
    return 'Algarve';
  };

  const extractPrice = (text: string): number | undefined => {
    const match = text.match(/(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*€/i) || text.match(/(\d{1,4})\s*euros?/i);
    if (match) {
      return parseInt(match[1].replace(/\./g, '').replace(',', ''));
    }
    return undefined;
  };

  const extractBedrooms = (text: string): number | undefined => {
    const tMatch = text.match(/\bT([0-5])\b/i);
    if (tMatch) {
      return parseInt(tMatch[1]);
    }
    const quartosMatch = text.match(/(\d+)\s*quarto/i);
    if (quartosMatch) {
      return parseInt(quartosMatch[1]);
    }
    return undefined;
  };

  const extractBathrooms = (text: string): number | undefined => {
    const match = text.match(/(\d+)\s*(?:wc|casas?\s*de\s*banho|banheiro)/i);
    if (match) {
      return parseInt(match[1]);
    }
    return undefined;
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-green-300 animate-pulse' : 'bg-red-300'}`}></div>
            <span className="text-white text-sm font-medium">
              {isConnected ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          <button
            onClick={() => {
              realAPI.resetSession();
              setMessages([{
                id: '1',
                role: 'assistant',
                content: 'Sessão reiniciada. Como posso ajudá-lo?',
                timestamp: new Date(),
              }]);
            }}
            className="text-white/80 hover:text-white text-xs font-medium transition-colors"
          >
            Reiniciar
          </button>
        </div>
        <h3 className="text-white font-semibold text-lg">Chat de Procura</h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gradient-to-b from-gray-50 to-white">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white'
                  : 'bg-white text-gray-900 border border-gray-200'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              {message.properties && message.properties.length > 0 && (
                <div className="mt-2 pt-2 border-t border-white/20 text-xs text-white/90 flex items-center gap-1">
                  <span>✅</span>
                  <span>{message.properties.length} propriedades encontradas</span>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-in fade-in">
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-gray-200">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-5 bg-white border-t border-gray-200">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Descreva o que procura..."
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
          >
            Enviar
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          💡 Dica: Seja específico sobre localização, tipo e orçamento
        </p>
      </div>
    </div>
  );
};
