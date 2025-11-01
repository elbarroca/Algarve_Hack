// Beautiful Home Page - Modern & Appealing Design
"use client";

import { useState } from "react";
import { ChatInterface, PropertyCard } from "./components";
import { PropertyListing } from "./types/api";

export default function HomesAIAlgarve() {
  const [properties, setProperties] = useState<PropertyListing[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handlePropertiesFound = (newProperties: PropertyListing[]) => {
    setProperties(newProperties);
    setIsSearching(false);
  };

  const handleMessageReceived = (message: string, isComplete: boolean) => {
    if (isComplete) {
      setIsSearching(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200/50 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg">
                <span className="text-2xl">🏠</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Homes AI Algarve
                </h1>
                <p className="text-sm text-gray-600">Procura inteligente de arrendamento</p>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-700 font-medium">Sistema Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Section */}
          <div className="lg:col-span-1">
            <div className="h-[calc(100vh-250px)]">
              <ChatInterface
                onPropertiesFound={handlePropertiesFound}
                onMessageReceived={handleMessageReceived}
              />
            </div>
          </div>

          {/* Properties Section */}
          <div className="lg:col-span-2">
            {isSearching && properties.length === 0 && (
              <div className="flex items-center justify-center h-64 bg-white rounded-2xl border border-gray-200 shadow-lg">
                <div className="text-center space-y-4">
                  <div className="relative">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-2xl">🔍</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-gray-700 font-medium">A procurar propriedades...</p>
                    <p className="text-sm text-gray-500 mt-1">Isto pode levar alguns segundos</p>
                  </div>
                </div>
              </div>
            )}

            {properties.length > 0 ? (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">
                      {properties.length} {properties.length === 1 ? 'Propriedade Encontrada' : 'Propriedades Encontradas'}
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">Resultados baseados na sua pesquisa</p>
                  </div>
                  <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
                    <span className="text-sm font-medium text-gray-700">✨ Ordenado por relevância</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {properties.map((property, index) => (
                    <PropertyCard
                      key={index}
                      property={property}
                      index={index}
                    />
                  ))}
                </div>
              </div>
            ) : !isSearching && (
              <div className="flex items-center justify-center h-96 bg-white rounded-2xl border border-gray-200 shadow-lg">
                <div className="text-center space-y-6 max-w-md px-8">
                  <div className="inline-block p-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl">
                    <span className="text-7xl">🏠</span>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">
                      Comece a procurar
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      Use o chat à esquerda para descrever o que procura.
                      <br />
                      <span className="text-blue-600 font-medium">Ex: "T2 em Faro até 900€"</span>
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2 justify-center pt-4">
                    <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">T2 em Faro</span>
                    <span className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-medium">Quarto em Loulé</span>
                    <span className="px-3 py-1 bg-pink-50 text-pink-700 rounded-full text-xs font-medium">T1 em Albufeira</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-lg border-t border-gray-200/50 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              © 2025 Homes AI Algarve. Made with ❤️ in Portugal 🇵🇹
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
