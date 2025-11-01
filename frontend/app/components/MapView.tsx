"use client";

import React, { useEffect, useRef } from 'react';
import { PropertyListing } from '../types/api';

interface MapViewProps {
  properties: PropertyListing[];
  center?: { lat: number; lng: number };
  onPropertyClick?: (property: PropertyListing) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  properties,
  center = { lat: 37.0194, lng: -7.9322 }, // Faro center
  onPropertyClick,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);

  // Note: Full Mapbox integration requires API key and mapbox-gl library
  // This is a placeholder/mock component for demonstration
  // To implement: npm install mapbox-gl @types/mapbox-gl

  useEffect(() => {
    // Placeholder for Mapbox initialization
    // Would initialize map here with:
    // mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    // new mapboxgl.Map({ container: mapContainerRef.current, ... });
  }, []);

  return (
    <div className="relative w-full h-full bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl overflow-hidden">
      {/* Map Container - Would render actual Mapbox map */}
      <div
        ref={mapContainerRef}
        className="w-full h-full bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center"
      >
        <div className="text-center space-y-4 p-8">
          <div className="text-6xl">🗺️</div>
          <div>
            <h3 className="text-white font-semibold text-xl mb-2">
              Mapa Interativo do Algarve
            </h3>
            <p className="text-slate-300 text-sm max-w-md">
              Visualização de propriedades com Mapbox
              <br />
              (Requer integração com Mapbox GL JS)
            </p>
          </div>

          {/* Property List Overlay */}
          {properties.length > 0 && (
            <div className="mt-6 space-y-2 max-h-64 overflow-y-auto">
              <p className="text-slate-400 text-xs font-semibold">
                📍 {properties.length} Propriedades no mapa:
              </p>
              {properties.map((property, index) => (
                <button
                  key={index}
                  onClick={() => onPropertyClick && onPropertyClick(property)}
                  className="w-full px-4 py-2 bg-slate-900/60 hover:bg-slate-900/80 border border-slate-600/50 rounded-lg text-left transition-all"
                >
                  <div className="text-white text-sm font-medium line-clamp-1">
                    {property.address}
                  </div>
                  <div className="text-slate-400 text-xs">
                    {property.city} • {property.price}€/mês
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Map Controls Placeholder */}
      <div className="absolute top-4 right-4 space-y-2">
        <button className="w-10 h-10 bg-white/90 hover:bg-white rounded-lg shadow-lg flex items-center justify-center text-slate-700 font-bold transition-all">
          +
        </button>
        <button className="w-10 h-10 bg-white/90 hover:bg-white rounded-lg shadow-lg flex items-center justify-center text-slate-700 font-bold transition-all">
          −
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg">
        <div className="flex items-center gap-2 text-xs text-slate-700">
          <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
          <span>Propriedades disponíveis</span>
        </div>
      </div>
    </div>
  );
};


