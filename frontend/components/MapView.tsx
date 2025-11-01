'use client';

import { useEffect, useRef, useState } from 'react';
import Map, { Marker, Popup, Source, Layer } from 'react-map-gl/mapbox';
import { Property } from '@/lib/mockData';
import NeighborhoodStats from './NeighborhoodStats';
import { NegotiationModal } from './NegotiationModal';
import { createCircle, fetchRoute, fetchDistanceMatrix, formatDistance, formatDuration } from '@/lib/mapUtils';
import 'mapbox-gl/dist/mapbox-gl.css';

interface MapViewProps {
  selectedProperty: Property | null;
  allProperties: Property[];
  topResultCoords?: { latitude: number; longitude: number; address: string; image_url?: string } | null;
  topResultDetails?: any;
  rawSearchResults?: any[];
  onNextListing?: () => void;
  currentListingIndex?: number;
  communityAnalysis?: any;
}

// Helper function to get icon and color for POI categories
const getPOIStyle = (category: string) => {
  const styles: Record<string, { emoji: string; color: string; bgColor: string }> = {
    school: { emoji: '🏫', color: '#3B82F6', bgColor: 'bg-blue-500' },
    hospital: { emoji: '🏥', color: '#EF4444', bgColor: 'bg-red-500' },
    grocery: { emoji: '🏪', color: '#F97316', bgColor: 'bg-orange-500' },
    restaurant: { emoji: '🍽️', color: '#F59E0B', bgColor: 'bg-amber-500' },
    park: { emoji: '🏞️', color: '#10B981', bgColor: 'bg-emerald-500' },
    transit_station: { emoji: '🚇', color: '#8B5CF6', bgColor: 'bg-purple-500' },
    cafe: { emoji: '☕', color: '#D97706', bgColor: 'bg-yellow-600' },
    gym: { emoji: '🏋️', color: '#EC4899', bgColor: 'bg-pink-500' },
  };
  return styles[category] || { emoji: '📍', color: '#6B7280', bgColor: 'bg-gray-500' };
};

export default function MapView({ selectedProperty, allProperties, topResultCoords, topResultDetails, rawSearchResults, onNextListing, currentListingIndex, communityAnalysis }: MapViewProps) {
  const mapRef = useRef<any>(null);
  const [showPopup, setShowPopup] = useState(false);
  const [selectedPOI, setSelectedPOI] = useState<any>(null);
  const [showNegotiationModal, setShowNegotiationModal] = useState(false);
  const [viewState, setViewState] = useState({
    longitude: -122.4331,
    latitude: 37.7505,
    zoom: 10,
  });
  const [radiusCircle, setRadiusCircle] = useState<any>(null);
  const [routes, setRoutes] = useState<any[]>([]);
  const [poiDistances, setPoiDistances] = useState<Record<number, { distance: number; duration: number }>>({});
  const [isLoadingRoutes, setIsLoadingRoutes] = useState(false);
  const [currentRadiusMeters, setCurrentRadiusMeters] = useState<number>(0);

  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_API_KEY || 'pk.eyJ1Ijoic3RldmVkdXN0eSIsImEiOiJjbWd4am05Z2IxZXhyMmtwdTg1cnU4cmYxIn0.zpfFRf-6xH6ivorwg_ZJ3w';

  // Extract current listing's POIs
  const currentPOIs = topResultDetails?.pois || [];

  // Debug: Log POI data
  useEffect(() => {
    console.log('[MapView] Current listing index:', currentListingIndex);
    console.log('[MapView] Top result details:', topResultDetails);
    console.log('[MapView] Current POIs:', currentPOIs);
  }, [currentListingIndex, topResultDetails]);

  useEffect(() => {
    if (selectedProperty && mapRef.current) {
      // Animate to selected property
      mapRef.current.flyTo({
        center: [selectedProperty.longitude, selectedProperty.latitude],
        zoom: 14,
        duration: 2000,
      });
      setShowPopup(true);
    }
  }, [selectedProperty]);

  // Fly to top result when coordinates are received or listing changes
  useEffect(() => {
    if (topResultCoords && mapRef.current) {
      console.log('[MapView] Flying to listing', (currentListingIndex ?? 0) + 1, ':', topResultCoords);
      mapRef.current.flyTo({
        center: [topResultCoords.longitude, topResultCoords.latitude],
        zoom: 15,
        duration: 1500,
      });
    }
    // Clear selected POI when listing changes
    setSelectedPOI(null);
  }, [topResultCoords, currentListingIndex]);

  // Create radius circle and fetch routes when top result changes
  useEffect(() => {
    if (!topResultCoords || currentPOIs.length === 0) {
      setRadiusCircle(null);
      setRoutes([]);
      setPoiDistances({});
      return;
    }

    const center: [number, number] = [topResultCoords.longitude, topResultCoords.latitude];

    // Fetch routes and distances
    const loadRoutesAndDistances = async () => {
      setIsLoadingRoutes(true);

      try {
        // First, get distance matrix for all POIs
        const poiCoords: [number, number][] = currentPOIs.map((poi: any) => [poi.longitude, poi.latitude]);
        const matrixData = await fetchDistanceMatrix([center], poiCoords, 'driving', mapboxToken);

        if (matrixData) {
          // Store distances
          const distanceMap: Record<number, { distance: number; duration: number }> = {};

          matrixData.distances[0].forEach((distance: number, index: number) => {
            distanceMap[index] = {
              distance,
              duration: matrixData.durations[0][index]
            };
          });
          setPoiDistances(distanceMap);

          // Calculate straight-line distance to farthest POI for circle radius
          let maxStraightLineDistance = 0;
          currentPOIs.forEach((poi: any) => {
            const poiLat = poi.latitude;
            const poiLng = poi.longitude;

            // Calculate straight-line distance using Haversine formula
            const R = 6371000; // Earth's radius in meters
            const dLat = ((poiLat - center[1]) * Math.PI) / 180;
            const dLon = ((poiLng - center[0]) * Math.PI) / 180;
            const a =
              Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos((center[1] * Math.PI) / 180) *
                Math.cos((poiLat * Math.PI) / 180) *
                Math.sin(dLon / 2) *
                Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const distance = R * c;

            if (distance > maxStraightLineDistance) {
              maxStraightLineDistance = distance;
            }
          });

          // Create circle with radius based on farthest POI (add small buffer)
          const radiusMeters = maxStraightLineDistance * 1.05;
          const circle = createCircle(center, radiusMeters);
          setRadiusCircle(circle);
          setCurrentRadiusMeters(radiusMeters);
        }

        // Then fetch individual routes for visualization
        const routePromises = currentPOIs.map(async (poi: any) => {
          const destination: [number, number] = [poi.longitude, poi.latitude];
          const routeData = await fetchRoute(center, destination, 'driving', mapboxToken);

          if (routeData) {
            return {
              type: 'Feature',
              geometry: routeData.geometry,
              properties: {
                distance: routeData.distance,
                duration: routeData.duration,
                poiName: poi.name,
                poiCategory: poi.category
              }
            };
          }
          return null;
        });

        const routeResults = await Promise.all(routePromises);
        const validRoutes = routeResults.filter(r => r !== null);
        setRoutes(validRoutes);
      } catch (error) {
        console.error('[MapView] Error fetching routes:', error);
      } finally {
        setIsLoadingRoutes(false);
      }
    };

    loadRoutesAndDistances();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topResultCoords, topResultDetails, mapboxToken]);

  return (
    <div className="relative h-full w-full">
      {/* Stats Container */}
      <div className="absolute top-0 left-0 right-0 z-10">
        <NeighborhoodStats
          location={communityAnalysis?.location || "San Francisco Bay Area"}
          propertyCount={allProperties.length}
          onNextListing={onNextListing}
          currentListingIndex={currentListingIndex}
          totalListings={rawSearchResults?.length || 0}
          communityAnalysis={communityAnalysis}
        />
      </div>

      {/* Map Container */}
      <div className="absolute inset-0">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={mapboxToken}
        style={{ width: '100%', height: '100%' }}
      >
        {/* Radius Circle Layer */}
        {radiusCircle && (
          <Source id="radius-circle" type="geojson" data={radiusCircle}>
            <Layer
              id="radius-circle-fill"
              type="fill"
              paint={{
                'fill-color': '#3B82F6',
                'fill-opacity': 0.1
              }}
            />
            <Layer
              id="radius-circle-outline"
              type="line"
              paint={{
                'line-color': '#3B82F6',
                'line-width': 2,
                'line-dasharray': [2, 2]
              }}
            />
          </Source>
        )}

        {/* Route Lines Layer */}
        {routes.length > 0 && (
          <Source
            id="routes"
            type="geojson"
            data={{
              type: 'FeatureCollection',
              features: routes
            }}
          >
            <Layer
              id="routes-line"
              type="line"
              paint={{
                'line-color': '#8B5CF6',
                'line-width': 3,
                'line-opacity': 0.6
              }}
            />
          </Source>
        )}
        {/* Top Result Marker - Special Star Marker */}
        {topResultCoords && (
          <Marker
            key={`marker-${currentListingIndex}-${topResultCoords._updateKey || ''}`}
            longitude={topResultCoords.longitude}
            latitude={topResultCoords.latitude}
            anchor="bottom"
          >
            <div className="relative">
              {/* Pulsing Ring Effect */}
              <div className="absolute inset-0 -m-4">
                <div className="w-12 h-12 rounded-full bg-green-500/20 animate-ping"></div>
              </div>
              {/* Star Icon */}
              <div className="relative z-10 flex items-center justify-center w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full border-3 border-white shadow-2xl shadow-green-500/50">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              {/* Label */}
              <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                <div className="bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                  Top Result
                </div>
              </div>
            </div>
          </Marker>
        )}

        {/* Show all properties as small markers */}
        {allProperties.map((property) => (
          <Marker
            key={property.id}
            longitude={property.longitude}
            latitude={property.latitude}
            anchor="bottom"
          >
            <div
              className={`transition-all cursor-pointer ${
                selectedProperty?.id === property.id
                  ? 'scale-150'
                  : 'scale-100 opacity-50 hover:opacity-100'
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full border-2 ${
                  selectedProperty?.id === property.id
                    ? 'bg-blue-500 border-white shadow-lg shadow-blue-500/50 animate-pulse'
                    : 'bg-blue-400 border-white'
                }`}
              />
            </div>
          </Marker>
        ))}

        {/* POI Markers */}
        {currentPOIs.map((poi: any, idx: number) => {
          const style = getPOIStyle(poi.category);
          return (
            <Marker
              key={`poi-${idx}-${currentListingIndex}`}
              longitude={poi.longitude}
              latitude={poi.latitude}
              anchor="bottom"
            >
              <div
                className="cursor-pointer transition-transform hover:scale-110"
                onClick={() => setSelectedPOI(poi)}
              >
                <div className="relative">
                  <div
                    className="w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center text-sm"
                    style={{ backgroundColor: style.color }}
                  >
                    {style.emoji}
                  </div>
                </div>
              </div>
            </Marker>
          );
        })}


        {/* POI Popup */}
        {selectedPOI && (
          <Popup
            longitude={selectedPOI.longitude}
            latitude={selectedPOI.latitude}
            anchor="bottom"
            onClose={() => setSelectedPOI(null)}
            closeButton={true}
            closeOnClick={false}
            offset={35}
            className="poi-popup"
          >
            <div className="backdrop-blur-xl bg-slate-900/80 border border-white/20 p-3 rounded-lg min-w-[200px]">
              <div className="flex items-start gap-2">
                <div className="text-2xl">{getPOIStyle(selectedPOI.category).emoji}</div>
                <div className="flex-1">
                  <h4 className="text-white font-semibold text-sm">{selectedPOI.name}</h4>
                  <p className="text-gray-300 text-xs mt-1 capitalize">
                    {selectedPOI.category.replace('_', ' ')}
                  </p>
                  {selectedPOI.address && (
                    <p className="text-gray-400 text-xs mt-1">{selectedPOI.address}</p>
                  )}
                  {(() => {
                    // Find POI index to get actual route distance
                    const poiIndex = currentPOIs.findIndex((p: any) =>
                      p.latitude === selectedPOI.latitude && p.longitude === selectedPOI.longitude
                    );
                    const distanceData = poiDistances[poiIndex];

                    if (distanceData) {
                      return (
                        <div className="mt-2 space-y-1">
                          <p className="text-purple-300 text-xs font-semibold">
                            🚗 {formatDistance(distanceData.distance)} ({formatDuration(distanceData.duration)})
                          </p>
                        </div>
                      );
                    } else if (selectedPOI.distance_meters) {
                      return (
                        <p className="text-blue-300 text-xs mt-1">
                          📏 {(selectedPOI.distance_meters / 1609.34).toFixed(2)} miles away (straight line)
                        </p>
                      );
                    }
                    return null;
                  })()}
                </div>
              </div>
            </div>
          </Popup>
        )}

        {/* Popup for selected property */}
        {selectedProperty && showPopup && (
          <Popup
            longitude={selectedProperty.longitude}
            latitude={selectedProperty.latitude}
            anchor="bottom"
            onClose={() => setShowPopup(false)}
            closeButton={true}
            closeOnClick={false}
            offset={25}
            className="property-popup"
          >
            <div className="backdrop-blur-xl bg-slate-900/60 border border-white/20 p-4 rounded-lg min-w-[280px]">
              <div className="space-y-2">
                <h3 className="text-white font-bold text-lg">
                  {selectedProperty.address}
                </h3>
                <p className="text-blue-300 text-sm">
                  {selectedProperty.city}, {selectedProperty.state}
                </p>
                <div className="border-t border-white/10 pt-2">
                  <p className="text-blue-400 font-bold text-xl">
                    ${(selectedProperty.price / 1000000).toFixed(2)}M
                  </p>
                  <div className="flex gap-4 mt-2 text-gray-300 text-sm">
                    <span>{selectedProperty.bedrooms} bed</span>
                    <span>{selectedProperty.bathrooms} bath</span>
                    <span>{selectedProperty.sqft.toLocaleString()} sqft</span>
                  </div>
                </div>
                <p className="text-gray-400 text-sm pt-2">
                  {selectedProperty.description.substring(0, 120)}...
                </p>
                <div className="pt-2 flex gap-2">
                  <button
                    onClick={() => {
                      setShowPopup(false);
                      setShowNegotiationModal(true);
                    }}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 px-3 rounded-lg text-sm font-semibold hover:from-purple-700 hover:to-pink-700 transition-all"
                  >
                    Start Negotiation 💬
                  </button>
                  <button className="flex-1 backdrop-blur-md bg-white/10 text-white py-2 px-3 rounded-lg text-sm font-semibold hover:bg-white/20 transition-all border border-white/20">
                    Details
                  </button>
                </div>
                <div className="pt-2 border-t border-white/10 mt-2">
                  <p className="text-blue-300 text-xs flex items-center gap-1">
                    <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                    Verified on ASI:One Blockchain
                  </p>
                </div>
              </div>
            </div>
          </Popup>
        )}
      </Map>

      {/* Map Legend / Info Box - Positioned to the left of listing info */}
      {topResultCoords && currentPOIs.length > 0 && (
        <div className="absolute top-[100px] right-[344px] z-20">
          <div className="backdrop-blur-xl bg-slate-900/95 border border-blue-500/30 rounded-lg shadow-2xl p-3 min-w-[200px]">
            <h4 className="text-white font-semibold text-sm mb-2">Map Legend</h4>
            <div className="space-y-2 text-xs">
              {currentRadiusMeters > 0 && (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 bg-blue-500 border-dashed border border-blue-500"></div>
                  <span className="text-gray-300">{formatDistance(currentRadiusMeters)} radius</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <div className="w-4 h-0.5 bg-purple-500"></div>
                <span className="text-gray-300">Routes to POIs</span>
              </div>
              {!isLoadingRoutes && routes.length > 0 && (
                <div className="pt-2 border-t border-white/10 mt-2">
                  <p className="text-green-300 font-semibold">
                    ✓ {routes.length} route{routes.length !== 1 ? 's' : ''} calculated
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Loading Indicator for Routes */}
      {isLoadingRoutes && (
        <div className="absolute top-20 right-4 z-20">
          <div className="backdrop-blur-xl bg-slate-900/95 border border-purple-500/30 rounded-lg shadow-2xl p-3">
            <div className="flex items-center gap-2 text-purple-300 text-sm">
              <div className="animate-spin w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full"></div>
              <span>Calculating routes...</span>
            </div>
          </div>
        </div>
      )}

      {/* Floating Sidebar for Top Result */}
      {topResultCoords && topResultDetails && (
        <div key={`listing-${currentListingIndex}-${topResultDetails?._updateKey || ''}`} className="absolute top-[100px] bottom-4 right-4 w-80 overflow-hidden">
          <div className="h-full overflow-y-auto bg-slate-900/95 backdrop-blur-xl border-2 border-green-500/40 rounded-xl shadow-2xl overflow-hidden">
            {/* Property Image */}
            {topResultCoords.image_url && (
              <div className="relative">
                <img
                  key={`img-${currentListingIndex}`}
                  src={topResultCoords.image_url}
                  alt="Property"
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
                <div className="absolute top-3 left-3">
                  <div className="bg-green-500 text-white text-xs font-bold px-3 py-1.5 rounded-full shadow-lg flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    {rawSearchResults && rawSearchResults.length > 1
                      ? `LISTING ${(currentListingIndex ?? 0) + 1}/${rawSearchResults.length}`
                      : 'TOP MATCH'
                    }
                  </div>
                </div>
              </div>
            )}

            {/* Property Details */}
            <div className="p-4 space-y-3">
              {/* Address & Description */}
              <div>
                <h3 className="text-white font-bold text-lg leading-tight">
                  {topResultCoords.address}
                </h3>
                {topResultDetails?.description && (
                  <p className="text-gray-400 text-sm mt-2 line-clamp-3">
                    {topResultDetails.description}
                  </p>
                )}
              </div>

              {/* Info Grid */}
              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/10">
                <div className="bg-slate-800/50 rounded-lg p-2.5">
                  <p className="text-gray-400 text-xs">Listed On</p>
                  <p className="text-white font-semibold text-sm mt-0.5">
                    {topResultDetails.display_link?.includes('redfin') ? 'Redfin' :
                     topResultDetails.display_link?.includes('zillow') ? 'Zillow' : 'Property Site'}
                  </p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-2.5">
                  <p className="text-gray-400 text-xs">Price</p>
                  <p className="text-green-400 font-bold text-sm mt-0.5">
                    {(() => {
                      // Try to extract price from title or description
                      const text = `${topResultDetails.title || ''} ${topResultDetails.description || ''}`;

                      // Match patterns like $1,200,000 or $1.2M or $2,500/mo
                      const priceMatch = text.match(/\$[\d,]+(?:\.[\d]+)?[KMB]?(?:\/mo)?/i);
                      if (priceMatch) {
                        const price = priceMatch[0];
                        // Check if it's a rental (contains /mo or /month)
                        const isRental = /\/mo/i.test(price);
                        return price;
                      }

                      // Fallback: Try to find any dollar amount
                      const dollarMatch = text.match(/\$[\d,]+/);
                      if (dollarMatch) {
                        return dollarMatch[0];
                      }

                      return 'Call for Price';
                    })()}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                <a
                  href={topResultDetails?.link || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 px-4 rounded-lg text-sm font-semibold hover:from-green-700 hover:to-green-800 transition-all text-center"
                >
                  View Full Listing →
                </a>

                <button
                  onClick={() => setShowNegotiationModal(true)}
                  className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-purple-700 transition-all text-center border border-white/10"
                >
                  Start Negotiation 💬
                </button>
              </div>

              {/* Status */}
              <div className="pt-2 border-t border-white/10">
                <p className="text-green-300 text-xs flex items-center gap-1.5">
                  <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  {rawSearchResults && rawSearchResults.length > 1
                    ? `Search result ${(currentListingIndex ?? 0) + 1} of ${rawSearchResults.length}`
                    : 'Best match for your search criteria'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Info Bar - Selected Property Only */}
      {selectedProperty && (
        <div className="absolute bottom-4 left-4">
          <div className="backdrop-blur-md bg-transparent border border-white/10 rounded-lg p-3 text-white shadow-xl">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span>Selected: {selectedProperty.address}</span>
            </div>
          </div>
        </div>
      )}
      </div>

      {/* Negotiation Modal */}
      {showNegotiationModal && (selectedProperty || (topResultCoords && topResultDetails)) && (
        <NegotiationModal
          property={
            selectedProperty || {
              id: currentListingIndex ?? 0,
              address: topResultCoords!.address,
              city: topResultDetails!.city || 'N/A',
              state: topResultDetails!.state || 'N/A',
              price: topResultDetails!.price || 0,
              bedrooms: topResultDetails!.bedrooms || 0,
              bathrooms: topResultDetails!.bathrooms || 0,
              sqft: topResultDetails!.sqft || 0,
              latitude: topResultCoords!.latitude,
              longitude: topResultCoords!.longitude,
              description: topResultDetails!.description || '',
              imageUrl: topResultCoords!.image_url || '',
              propertyType: topResultDetails!.propertyType || 'Residential',
            }
          }
          onClose={() => setShowNegotiationModal(false)}
        />
      )}

      <style jsx global>{`
        .mapboxgl-popup-content {
          background: transparent !important;
          padding: 0 !important;
          box-shadow: none !important;
        }
        .mapboxgl-popup-close-button {
          color: white !important;
          font-size: 20px !important;
          padding: 4px 8px !important;
          right: 8px !important;
          top: 8px !important;
        }
        .mapboxgl-popup-close-button:hover {
          background-color: rgba(255, 255, 255, 0.1) !important;
        }
      `}</style>
    </div>
  );
}
