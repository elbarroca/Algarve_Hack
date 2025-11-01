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
}

export default function ChatInterface({ onPropertiesFound, onTopResultCoordinates, onRawSearchResults, onCommunityAnalysis, sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: Date.now(), role: 'agent', content: 'Hi! I can help you find a home in the Bay Area. Where would you like to live?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate unique session ID on mount
  const [actualSessionId] = useState(() => sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    const requestId = `${Date.now()}_${Math.random()}`;
    const userMsg: Message = { id: Date.now(), role: 'user', content: userMessage };

    console.log(`[ChatInterface] Sending message (${requestId}):`, userMessage);

    setInput('');
    setLoading(true);
    setStreamingMessage('Processing your request...');

    // Add user message immediately
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, sessionId: actualSessionId }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setStreamingMessage('');

      console.log(`[ChatInterface] Received response (${requestId}):`, {
        status: data.status,
        search_summary: data.data?.search_summary,
        properties_count: data.data?.properties?.length || 0
      });

      if (data.status === 'success' && data.data) {
        const { properties, search_summary, top_result_coordinates, raw_search_results, community_analysis } = data.data;

        // Add agent's response
        const agentMsg: Message = {
          id: Date.now() + 1,
          role: 'agent',
          content: search_summary || 'Processing...'
        };

        console.log('[ChatInterface] Adding agent message:', agentMsg.content.substring(0, 100));
        setMessages(prev => [...prev, agentMsg]);

        // Store ALL raw search results in parent
        if (raw_search_results && raw_search_results.length > 0 && onRawSearchResults) {
          console.log('[ChatInterface] Storing raw search results:', raw_search_results.length);
          onRawSearchResults(raw_search_results);
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

        // If properties found, pass to map
        if (properties && properties.length > 0 && onPropertiesFound) {
          onPropertiesFound(properties);
        }

      } else if (data.status === 'error') {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'system',
          content: `Error: ${data.data?.message || 'Unknown error'}`
        }]);
      }

    } catch (error) {
      console.error('Chat error:', error);
      setStreamingMessage('');
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'system',
        content: 'Sorry, there was an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="border-b border-slate-700/50 bg-black/30 p-4">
        <h2 className="text-white font-semibold">Homes.ai</h2>
        <p className="text-xs text-slate-400 mt-1">
          Powered by ASI:1 + uAgents
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

        {/* Streaming message indicator */}
        {streamingMessage && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 border border-slate-600/30 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
                <p className="text-sm text-slate-300">{streamingMessage}</p>
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

      <div className="border-t border-slate-700/50 bg-black/30 p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-slate-800/50 border border-slate-600/30 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 transition-all"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
