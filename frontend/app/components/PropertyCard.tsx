// Beautiful Property Card - Modern & Appealing
"use client";

import React from 'react';
import { PropertyListing } from '../types/api';

interface PropertyCardProps {
  property: PropertyListing;
  index: number;
}

export const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  index,
}) => {
  const formatPrice = (price?: number) => {
    if (!price) return 'Preço sob consulta';
    return new Intl.NumberFormat('pt-PT', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="group bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
      {/* Image */}
      <div className="relative h-56 bg-gradient-to-br from-blue-100 to-purple-100 overflow-hidden">
        {property.image_url ? (
          <img
            src={property.image_url}
            alt={property.address || 'Propriedade'}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-6xl opacity-30">🏠</div>
          </div>
        )}
        <div className="absolute top-4 left-4 px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-semibold text-gray-700 shadow-sm">
          #{index + 1}
        </div>
        {property.price && property.price < 700 && (
          <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-white rounded-full text-xs font-semibold shadow-lg">
            💰 Oportunidade
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* Title */}
        <h3 className="font-bold text-gray-900 text-lg line-clamp-2 group-hover:text-blue-600 transition-colors">
          {property.address || 'Endereço não disponível'}
        </h3>

        {/* Location */}
        {property.city && (
          <div className="flex items-center gap-2 text-gray-600">
            <span className="text-blue-500">📍</span>
            <span className="text-sm font-medium">{property.city}, Algarve</span>
          </div>
        )}

        {/* Price */}
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {formatPrice(property.price)}
          </span>
          {property.price && (
            <span className="text-sm text-gray-500">/mês</span>
          )}
        </div>

        {/* Features */}
        <div className="flex flex-wrap gap-2">
          {property.bedrooms !== undefined && (
            <div className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold flex items-center gap-1">
              <span>🛏️</span>
              <span>{property.bedrooms === 0 ? 'T0' : `${property.bedrooms} ${property.bedrooms === 1 ? 'quarto' : 'quartos'}`}</span>
            </div>
          )}
          {property.bathrooms !== undefined && (
            <div className="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-xs font-semibold flex items-center gap-1">
              <span>🚿</span>
              <span>{property.bathrooms} WC</span>
            </div>
          )}
          {property.sqft && (
            <div className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-xs font-semibold flex items-center gap-1">
              <span>📐</span>
              <span>{property.sqft}m²</span>
            </div>
          )}
        </div>

        {/* Description */}
        {property.description && (
          <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
            {property.description}
          </p>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          {property.url && (
            <a
              href={property.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-center text-sm font-semibold rounded-lg transition-all shadow-md hover:shadow-lg"
            >
              Ver Anúncio →
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
