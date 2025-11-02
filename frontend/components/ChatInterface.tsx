'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  role: 'user' | 'agent' | 'system';
  content: string;
  agent?: string;
}

interface ChatInterfaceProps {
  onPropertiesFound?: (properties: any[]) => void;
  onTopResultCoordinates?: (coords: { latitude: number; longitude: number; address: string; image_url?: string } | null) => void;
  onRawSearchResults?: (results: any[]) => void;
  onCommunityAnalysis?: (analysis: any) => void;
  sessionId?: string;
  onListingSelect?: (index: number) => void;
  currentListingIndex?: number;
  onTopResultDetails?: (details: any) => void;
}

// Preset search messages
const PRESET_SEARCHES = [
  {
    icon: '🏠',
    label: 'T1 Olhão até €800 com Varanda (para festas :D)',
    message: 'Procuro um T1 em Olhão até 800 euros com varanda'
  },
  {
    icon: '🏡',
    label: 'T2 em Albufeira até €1500',
    message: 'Procuro um T2 em Albufeira até 1500 euros'
  }
];

export default function ChatInterface({ onPropertiesFound, onTopResultCoordinates, onRawSearchResults, onCommunityAnalysis, sessionId, onListingSelect, currentListingIndex = 0, onTopResultDetails }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: Date.now(), role: 'agent', content: 'Olá! Posso ajudá-lo a encontrar uma casa no Algarve. Que tipo de propriedade procura?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const [loadingStage, setLoadingStage] = useState<string>('');
  const [rawSearchResults, setRawSearchResults] = useState<any[]>([]);
  const [searchLocation, setSearchLocation] = useState<string>('Faro');
  const [showGridView, setShowGridView] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const loadingStageTimersRef = useRef<NodeJS.Timeout[]>([]);

  // Generate unique session ID on mount
  const [actualSessionId] = useState(() => sessionId || `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  // Handle preset search button click
  const handlePresetSearch = async (message: string) => {
    const userMsg: Message = { id: Date.now(), role: 'user', content: message };
    setMessages(prev => [...prev, userMsg]);

    // Extract location from the preset message
    const locationKeywords = ['Faro', 'Loulé', 'Portimão', 'Lagos', 'Tavira', 'Olhão', 'Albufeira'];
    const detectedLocation = locationKeywords.find(loc =>
      message.toLowerCase().includes(loc.toLowerCase())
    );
    if (detectedLocation) {
      setSearchLocation(detectedLocation);
    }

    // Call the main API with the preset message
    await sendMessageToAPI(message);
  };

  const sendMessageToAPI = async (message: string) => {
    const requestId = `${Date.now()}_${Math.random()}`;

    console.log(`[ChatInterface] Sending message (${requestId}):`, message);

    setInput('');
    setLoading(true);
    setStreamingMessage('A compreender os seus requisitos...');
    setLoadingStage('scoping');

    // Clear any existing loading stage timers
    loadingStageTimersRef.current.forEach(timer => clearTimeout(timer));
    loadingStageTimersRef.current = [];

    // Dynamic loading stages based on agent activity
    const stages = [
      { stage: 'scoping', message: 'A compreender os seus requisitos...', delay: 0 },
      { stage: 'research', message: 'A pesquisar listagens de propriedades...', delay: 2000 },
      { stage: 'extracting', message: 'A extrair propriedades das listagens...', delay: 5000 },
      { stage: 'scraping-1', message: 'A recolher detalhes das propriedades (1-3)...', delay: 8000 },
      { stage: 'scraping-2', message: 'A recolher detalhes das propriedades (4-6)...', delay: 12000 },
      { stage: 'scraping-3', message: 'A recolher detalhes das propriedades (7-10)...', delay: 16000 },
      { stage: 'community', message: 'A analisar dados do bairro...', delay: 20000 },
      { stage: 'geocoding', message: 'A geocodificar localizações...', delay: 23000 },
      { stage: 'poi', message: 'A descobrir pontos de interesse próximos...', delay: 26000 },
      { stage: 'finalizing', message: 'A finalizar resultados...', delay: 29000 },
    ];

    // Start stage progression
    const timers: NodeJS.Timeout[] = [];
    stages.forEach((stage, index) => {
      if (index > 0) {
        const timer = setTimeout(() => {
          setLoadingStage(stage.stage);
          setStreamingMessage(stage.message);
        }, stage.delay);
        timers.push(timer);
      }
    });

    // Store timers for cleanup
    loadingStageTimersRef.current = timers;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, sessionId: actualSessionId }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setStreamingMessage('');
      setLoadingStage('');

      // Clear loading stage timers
      loadingStageTimersRef.current.forEach(timer => clearTimeout(timer));
      loadingStageTimersRef.current = [];

      console.log(`[ChatInterface] Received response (${requestId}):`, {
        status: data.status,
        search_summary: data.data?.search_summary,
        properties_count: data.data?.properties?.length || 0
      });

      if (data.status === 'success' && data.data) {
        const { properties, search_summary, top_result_coordinates, raw_search_results, community_analysis, formatted_properties_json } = data.data;

        // Add agent's response
        const agentMsg: Message = {
          id: Date.now() + 1,
          role: 'agent',
          content: search_summary || 'A processar...'
        };

        console.log('[ChatInterface] Adding agent message:', agentMsg.content.substring(0, 100));
        setMessages(prev => [...prev, agentMsg]);

        // Store ALL raw search results in parent with location filtering
        if (raw_search_results && raw_search_results.length > 0 && onRawSearchResults) {
          console.log('[ChatInterface] Storing raw search results:', raw_search_results.length);

          // Filter results by location
          const filteredResults = raw_search_results.filter((result: any) => {
            const address = (result.address || result.title || '').toLowerCase();
            const location = searchLocation.toLowerCase();

            // Handle location as object with full_address, city, address fields
            const locationStr = typeof result.location === 'string'
              ? result.location
              : (result.location?.full_address || result.location?.city || result.location?.address || '');

            // Check address/title contains location name
            const addressMatch = address.includes(location) || locationStr.toLowerCase().includes(location);

            // Coordinate-based filtering for Faro region (approximately 37.0, -7.9)
            if (searchLocation.toLowerCase() === 'faro' && result.latitude && result.longitude) {
              // Faro is around 37.0, -7.9, exclude results too far away (like Braga at 41.5, -8.1)
              const latDiff = Math.abs(result.latitude - 37.0);
              const lonDiff = Math.abs(result.longitude - (-7.9));
              // Only include if within ~0.5 degree (approximately 50km) OR address matches
              const inFaroRegion = latDiff < 0.5 && lonDiff < 0.5;
              return addressMatch || inFaroRegion;
            }

            // For other locations with coordinates, check proximity
            if (result.latitude && result.longitude) {
              // Define location centers (approximate)
              const locationCenters: Record<string, [number, number]> = {
                'faro': [37.0194, -7.9322],
                'loulé': [37.1377, -8.0244],
                'portimão': [37.1366, -8.5337],
                'lagos': [37.1020, -8.6758],
                'tavira': [37.1266, -7.6486],
                'olhão': [37.0261, -7.8411],
                'albufeira': [37.0889, -8.2503],
              };

              const center = locationCenters[location];
              if (center) {
                const latDiff = Math.abs(result.latitude - center[0]);
                const lonDiff = Math.abs(result.longitude - center[1]);
                const inRegion = latDiff < 0.5 && lonDiff < 0.5;
                return addressMatch || inRegion;
              }
            }

            // For locations without coordinates or no match, rely on address match
            return addressMatch;
          });

          console.log(`[ChatInterface] Filtered ${filteredResults.length} results for location: ${searchLocation} (from ${raw_search_results.length} total)`);

          // Store filtered results locally
          setRawSearchResults(filteredResults);

          // Pass to parent
          onRawSearchResults(filteredResults);
        }

        // If top result coordinates found, pass to parent
        if (top_result_coordinates && onTopResultCoordinates) {
          console.log('[ChatInterface] Top result coordinates:', top_result_coordinates);
          onTopResultCoordinates(top_result_coordinates);
        }

        // If community analysis found, pass to parent
        if (community_analysis && onCommunityAnalysis) {
          console.log('[ChatInterface] Community analysis:', community_analysis);
          onCommunityAnalysis(community_analysis);
        }

        // Use individual property data if available, otherwise fall back to generic properties
        const propertyData = formatted_properties_json || properties;
        console.log('[ChatInterface] Using property data:', {
          individual_properties: formatted_properties_json?.length || 0,
          generic_properties: properties?.length || 0,
          using_individual: !!formatted_properties_json
        });

        // If properties found, pass to map - prefer individual property data
        if (propertyData && propertyData.length > 0 && onPropertiesFound) {
          onPropertiesFound(propertyData);
        }

      } else if (data.status === 'error') {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'system',
          content: `Erro: ${data.data?.message || 'Erro desconhecido'}`
        }]);
      }

    } catch (error) {
      console.error('Chat error:', error);
      setStreamingMessage('');
      setLoadingStage('');

      // Clear loading stage timers
      loadingStageTimersRef.current.forEach(timer => clearTimeout(timer));
      loadingStageTimersRef.current = [];

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'system',
        content: 'Desculpe, houve um erro. Tente novamente.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg: Message = { id: Date.now(), role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMsg]);

    await sendMessageToAPI(input.trim());
  };

  return (
    <div className="flex h-full flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="border-b border-slate-700/50 bg-black/30 p-4">
        <h1 className="text-white font-semibold">🏠 YooseAI</h1>
        <p className="text-xs text-slate-400 mt-1">
          Contruido na Buildathon 2025
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
              msg.role === 'user'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                : msg.role === 'system'
                ? 'bg-red-900/30 text-red-200 border border-red-600/30'
                : 'bg-slate-800/50 text-gray-100 border border-slate-600/30'
            }`}>
              {msg.agent && (
                <div className="text-xs text-blue-400 mb-1 font-semibold">
                  {msg.agent}
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {/* Streaming message indicator with dynamic stages */}
        {streamingMessage && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 border border-slate-600/30 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <div className="flex flex-col">
                  <p className="text-sm text-slate-300 font-medium">{streamingMessage}</p>
                  {loadingStage && (
                    <div className="flex items-center gap-2 mt-1">
                      <div className="h-1 bg-slate-700 rounded-full flex-1 overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full animate-pulse ${
                            loadingStage === 'scoping' ? 'w-[10%]' :
                            loadingStage === 'research' ? 'w-[20%]' :
                            loadingStage === 'extracting' ? 'w-[30%]' :
                            loadingStage === 'scraping-1' ? 'w-[40%]' :
                            loadingStage === 'scraping-2' ? 'w-[55%]' :
                            loadingStage === 'scraping-3' ? 'w-[70%]' :
                            loadingStage === 'community' ? 'w-[80%]' :
                            loadingStage === 'geocoding' ? 'w-[85%]' :
                            loadingStage === 'poi' ? 'w-[92%]' :
                            loadingStage === 'finalizing' ? 'w-[98%]' :
                            'w-full'
                          }`}
                          style={{ transition: 'width 0.5s ease-in-out' }}
                        />
                      </div>
                      <span className="text-xs text-slate-400 capitalize">{loadingStage}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {loading && !streamingMessage && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 border border-slate-600/30 rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Preset Search Buttons */}
      {messages.length === 1 && !loading && (
        <div className="px-4 py-2 border-t border-slate-700/50 bg-black/20">
          <p className="text-xs text-slate-400 mb-2">Pesquisas rápidas:</p>
          <div className="flex gap-2">
            {PRESET_SEARCHES.map((preset, index) => (
              <button
                key={index}
                onClick={() => handlePresetSearch(preset.message)}
                className="flex items-center gap-2 bg-slate-800/50 hover:bg-slate-700/50 border border-slate-600/30 hover:border-slate-500/50 rounded-xl px-3 py-2 text-white text-xs transition-all"
                disabled={loading}
              >
                <span className="text-base">{preset.icon}</span>
                <span className="font-medium">{preset.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Grid View Modal */}
      {showGridView && rawSearchResults && rawSearchResults.length > 0 && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden border border-slate-700/50 shadow-2xl">
            <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-black/30">
              <div>
                <h3 className="text-lg font-bold text-white">Todas as Listagens</h3>
                <p className="text-sm text-slate-400">{rawSearchResults.length} propriedades encontradas em {searchLocation}</p>
              </div>
              <button
                onClick={() => setShowGridView(false)}
                className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="overflow-y-auto p-4" style={{ maxHeight: 'calc(90vh - 80px)' }}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {rawSearchResults.map((listing: any, index: number) => (
                  <div
                    key={index}
                    onClick={() => {
                      setShowGridView(false);
                      if (onListingSelect) {
                        onListingSelect(index);
                      }
                      if (listing.latitude && listing.longitude && onTopResultCoordinates) {
                        onTopResultCoordinates({
                          latitude: listing.latitude,
                          longitude: listing.longitude,
                          address: listing.address || listing.title || 'Morada Desconhecida',
                          image_url: listing.image_url
                        });
                      }
                      if (onTopResultDetails) {
                        onTopResultDetails(listing);
                      }
                    }}
                    className={`bg-slate-800/50 border rounded-xl overflow-hidden cursor-pointer transition-all hover:scale-[1.02] ${
                      index === currentListingIndex
                        ? 'border-blue-500 shadow-lg shadow-blue-500/20'
                        : 'border-slate-600/30 hover:border-slate-500/50'
                    }`}
                  >
                    {(() => {
                      // Get image URL from listing (check images array first, then image_url)
                      const imageUrl = listing.images && listing.images.length > 0 && listing.images[0]
                        ? listing.images[0]
                        : listing.image_url;

                      return imageUrl ? (
                        <div className="w-full h-48 bg-slate-700 relative overflow-hidden">
                          <img
                            src={imageUrl}
                            alt={listing.title || 'Propriedade'}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              (e.target as HTMLImageElement).style.display = 'none';
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-full h-48 bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                          <svg className="w-16 h-16 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                          </svg>
                        </div>
                      );
                    })()}
                    <div className="p-4">
                      <h3 className="text-base font-bold text-white mb-2 line-clamp-2">
                        {listing.title || listing.address || `Listagem ${index + 1}`}
                      </h3>
                      {listing.price && (
                        <p className="text-lg text-green-400 font-bold mb-2">
                          €{typeof listing.price === 'object' ? (listing.price.amount?.toLocaleString() || 'N/A') : (typeof listing.price === 'number' ? listing.price.toLocaleString() : listing.price)}
                          {(listing.price?.is_rent || listing.price_type === 'monthly') ? '/mês' : ''}
                        </p>
                      )}
                      {/* Property Type Badge */}
                      {listing.property_type && (
                        <div className="mb-2">
                          <span className="bg-blue-500/20 text-blue-300 text-xs px-2 py-1 rounded-full border border-blue-500/30">
                            {listing.property_type}
                          </span>
                        </div>
                      )}

                      {/* Property Details Grid */}
                      <div className="grid grid-cols-2 gap-2 mb-3">
                        {listing.bedrooms && (
                          <div className="bg-slate-800/30 rounded-lg px-2 py-1.5 border border-slate-700/30">
                            <div className="text-xs text-slate-400">Quartos</div>
                            <div className="text-sm text-white font-semibold flex items-center gap-1">
                              <span>🛏️</span> {listing.bedrooms}
                            </div>
                          </div>
                        )}
                        {(listing.area_m2 || listing.property_details?.area_m2 || listing.sqft) && (
                          <div className="bg-slate-800/30 rounded-lg px-2 py-1.5 border border-slate-700/30">
                            <div className="text-xs text-slate-400">Área</div>
                            <div className="text-sm text-white font-semibold flex items-center gap-1">
                              <span>📏</span> {listing.area_m2 || listing.property_details?.area_m2 || listing.sqft}m²
                            </div>
                          </div>
                        )}
                      </div>
                      {listing.address && (
                        <div className="text-xs text-slate-400 mb-2 flex items-start gap-1">
                          <span className="flex-shrink-0">📍</span>
                          <span className="line-clamp-2">{listing.address}</span>
                        </div>
                      )}
                      {listing.link && (
                        <a
                          href={listing.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-400 hover:text-blue-300 mb-2 flex items-center gap-1 hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <span>🔗</span>
                          <span className="line-clamp-1">Ver anúncio original</span>
                        </a>
                      )}
                      {listing.description && (
                        <p className="text-xs text-slate-400 line-clamp-3 mb-3">
                          {listing.description}
                        </p>
                      )}
                      {listing.pois && listing.pois.length > 0 && (
                        <div className="border-t border-slate-700/50 pt-3 mt-3">
                          <div className="text-xs font-semibold text-blue-400 mb-2">
                            📍 {listing.pois.length} Locais Próximos
                          </div>
                          <div className="space-y-1">
                            {listing.pois.slice(0, 3).map((poi: any, poiIdx: number) => (
                              <div key={poiIdx} className="text-xs text-slate-400 flex items-center gap-1">
                                <span className="text-slate-500">•</span>
                                <span className="line-clamp-1">{poi.name || poi.type}</span>
                                {poi.distance && (
                                  <span className="text-slate-500 ml-auto">{poi.distance}m</span>
                                )}
                              </div>
                            ))}
                            {listing.pois.length > 3 && (
                              <div className="text-xs text-blue-400">
                                +{listing.pois.length - 3} mais
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      {listing.negotiation_score && (
                        <div className="border-t border-slate-700/50 pt-3 mt-3">
                          <div className="text-xs text-slate-400 flex items-center justify-between">
                            <span>Potencial de Negociação</span>
                            <span className="font-bold text-yellow-400">{listing.negotiation_score}/10</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Horizontal Listings Grid */}
      {rawSearchResults && rawSearchResults.length > 0 && (
        <div className="border-t border-slate-700/50 bg-black/40 p-3 flex-shrink-0">
          <div className="flex items-center gap-2 mb-2 justify-between">
            <span className="text-xs font-semibold text-slate-300">
              Encontradas {rawSearchResults.length} listagens em {searchLocation}
            </span>
            <button
              onClick={() => setShowGridView(true)}
              className="text-xs bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-400 px-3 py-1 rounded-lg transition-colors flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Ver Todas
            </button>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
            {rawSearchResults.map((listing: any, index: number) => (
              <div
                key={index}
                onClick={() => {
                  if (onListingSelect) {
                    onListingSelect(index);
                  }
                  // Also update top result coordinates and details
                  if (listing.latitude && listing.longitude && onTopResultCoordinates) {
                    onTopResultCoordinates({
                      latitude: listing.latitude,
                      longitude: listing.longitude,
                      address: listing.address || listing.title || 'Morada Desconhecida',
                      image_url: listing.image_url
                    });
                  }
                  if (onTopResultDetails) {
                    onTopResultDetails(listing);
                  }
                }}
                className={`flex-shrink-0 w-48 bg-slate-800/50 border rounded-lg overflow-hidden cursor-pointer transition-all ${
                  index === currentListingIndex
                    ? 'border-blue-500 shadow-lg shadow-blue-500/20 scale-105'
                    : 'border-slate-600/30 hover:border-slate-500/50'
                }`}
              >
                {(() => {
                  // Get image URL from listing (check images array first, then image_url)
                  const imageUrl = listing.images && listing.images.length > 0 && listing.images[0]
                    ? listing.images[0]
                    : listing.image_url;

                  return imageUrl ? (
                    <div className="w-full h-32 bg-slate-700 relative overflow-hidden">
                      <img
                        src={imageUrl}
                        alt={listing.title || 'Propriedade'}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    </div>
                  ) : (
                    <div className="w-full h-32 bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center">
                      <svg className="w-12 h-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                    </div>
                  );
                })()}
                <div className="p-3">
                  <h3 className="text-sm font-semibold text-white truncate mb-1">
                    {listing.title || listing.address || `Listagem ${index + 1}`}
                  </h3>
                  {listing.price && (
                    <p className="text-xs text-green-400 font-bold mb-1">
                      €{typeof listing.price === 'object' ? (listing.price.amount?.toLocaleString() || 'N/A') : (typeof listing.price === 'number' ? listing.price.toLocaleString() : listing.price)}
                      {(listing.price?.is_rent || listing.price_type === 'monthly') ? '/mês' : ''}
                    </p>
                  )}
                  <div className="flex gap-2 text-xs text-slate-400">
                    {listing.bedrooms && <span>🛏️ {listing.bedrooms} quartos</span>}
                    {(listing.area_m2 || listing.property_details?.area_m2) && <span>📏 {listing.area_m2 || listing.property_details?.area_m2}m²</span>}
                  </div>
                  {listing.pois && listing.pois.length > 0 && (
                    <div className="mt-2 text-xs text-blue-400">
                      📍 {listing.pois.length} locais próximos
                    </div>
                  )}
                  {listing.address && (
                    <div className="mt-1 text-xs text-slate-500 truncate">
                      📍 {listing.address}
                    </div>
                  )}
                  {listing.link && (
                    <a
                      href={listing.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <span>🔗</span>
                      <span className="truncate">Ver original</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-slate-700/50 bg-black/30 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escreva uma mensagem..."
            className="flex-1 bg-slate-800/50 border border-slate-600/30 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition-all"
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
