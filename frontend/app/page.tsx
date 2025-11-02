'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import MapView from '@/components/MapView';
import { Property } from '@/lib/mockData';

export default function Home() {
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);
  const [topResultCoords, setTopResultCoords] = useState<{ latitude: number; longitude: number; address: string; image_url?: string } | null>(null);
  const [rawSearchResults, setRawSearchResults] = useState<any[]>([]);
  const [topResultDetails, setTopResultDetails] = useState<any>(null);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [currentListingIndex, setCurrentListingIndex] = useState(0);
  const [communityAnalysis, setCommunityAnalysis] = useState<any>(null);

  const handlePropertiesFound = (newProperties: any[]) => {
    console.log('[Home] Received properties:', newProperties.length);
    console.log('[Home] Sample property:', newProperties[0]);
    
    // Convert backend properties to frontend Property format
    // Extract coordinates from location object if needed
    const geoReady = newProperties.map((prop, idx) => {
      // Extract coordinates - check multiple locations
      let lat = prop.latitude;
      let lon = prop.longitude;
      
      if (!lat || !lon) {
        const location = prop.location;
        if (location && typeof location === 'object') {
          lat = location.latitude;
          lon = location.longitude;
        }
      }
      
      // Return with coordinates normalized to root level
      return {
        ...prop,
        latitude: lat,
        longitude: lon,
        _originalIndex: idx
      };
    }).filter(
      (prop) => {
        const hasCoords = typeof prop.latitude === 'number' && typeof prop.longitude === 'number' && 
                         !isNaN(prop.latitude) && !isNaN(prop.longitude);
        if (!hasCoords) {
          console.warn('[Home] Property missing coordinates:', prop.address || prop.title, prop);
        }
        return hasCoords;
      }
    );

    console.log('[Home] Properties with valid coordinates:', geoReady.length);
    console.log('[Home] Properties with POIs:', geoReady.filter(p => p.pois && p.pois.length > 0).length);

    const convertedProperties: Property[] = geoReady.map((prop, idx) => {
      const location = prop.location || {};
      const locationStr = typeof location === 'string' ? location : (location.full_address || location.city || location.address || '');
      
      return {
        id: prop._originalIndex !== undefined ? prop._originalIndex + 1000 : idx + 1000,
        address: prop.address || prop.title || locationStr || 'Unknown Address',
        city: typeof location === 'string' ? location : (location.city || 'Faro'),
        state: 'Algarve',
        price: typeof prop.price === 'object' ? (prop.price?.amount || 0) : (prop.price || 0),
        bedrooms: prop.bedrooms || 0,
        bathrooms: prop.bathrooms || 0,
        sqft: prop.area_m2 || prop.sqft || 0,
        latitude: prop.latitude,
        longitude: prop.longitude,
        description: prop.description || '',
        imageUrl: prop.image_url || prop.images?.[0] || '/properties/default.jpg',
        propertyType: prop.property_type || 'Single Family'
      };
    });

    console.log('[Home] Converted properties for map:', convertedProperties.length);
    console.log('[Home] First property sample:', {
      id: convertedProperties[0]?.id,
      address: convertedProperties[0]?.address,
      lat: convertedProperties[0]?.latitude,
      lon: convertedProperties[0]?.longitude
    });
    
    // Set converted properties (no mock data fallback)
    setProperties(convertedProperties);
  };

  const handleRawSearchResults = (results: any[]) => {
    console.log('[Home] Storing raw search results:', results.length);
    console.log('[Home] Raw results with POIs:', results.map(r => ({ 
      address: r.address || r.location?.full_address,
      pois: r.pois?.length || 0,
      lat: r.latitude || r.location?.latitude,
      lon: r.longitude || r.location?.longitude
    })));

    // Don't limit - show all results from backend (they're already filtered)
    setRawSearchResults(results);
    setCurrentListingIndex(0); // Reset to first listing

    // Extract top result details and coordinates
    if (results.length > 0) {
      const topResult = results[0];
      console.log('[Home] Top result details:', topResult);
      console.log('[Home] Top result POIs:', topResult.pois);
      setTopResultDetails(topResult);
      
      // Update top result coordinates if available
      const lat = topResult.latitude || topResult.location?.latitude;
      const lon = topResult.longitude || topResult.location?.longitude;
      if (lat && lon) {
        setTopResultCoords({
          latitude: lat,
          longitude: lon,
          address: topResult.address || topResult.title || topResult.location?.full_address || 'Unknown Address',
          image_url: topResult.image_url
        });
      }
    }
  };

  const handleNextListing = () => {
    if (rawSearchResults.length === 0) return;

    const nextIndex = (currentListingIndex + 1) % rawSearchResults.length;
    setCurrentListingIndex(nextIndex);

    const nextListing = rawSearchResults[nextIndex];
    console.log('[Home] Cycling to listing', nextIndex + 1, 'of', rawSearchResults.length, ':', nextListing);

    // Update top result details
    setTopResultDetails({
      ...nextListing
    });

    // Update coordinates
    const lat = nextListing.latitude || nextListing.location?.latitude;
    const lon = nextListing.longitude || nextListing.location?.longitude;
    if (lat && lon) {
      setTopResultCoords({
        latitude: lat,
        longitude: lon,
        address: nextListing.address || nextListing.title || nextListing.location?.full_address || 'Unknown Address',
        image_url: nextListing.image_url
      });
    }

    // Clear community analysis when changing listings (will be re-fetched if available for this listing)
    setCommunityAnalysis(null);
  };

  const handleTopResultCoordinates = (coords: { latitude: number; longitude: number; address: string; image_url?: string } | null) => {
    console.log('[Home] Received top result coordinates:', coords);
    setTopResultCoords(coords);
  };

  const handleCommunityAnalysis = (analysis: any) => {
    console.log('[Home] Received community analysis:', analysis);
    setCommunityAnalysis(analysis);
  };

  return (
    <div className="h-screen w-screen overflow-hidden bg-black flex">
      <div className="w-1/4 h-full border-r border-slate-700/50">
        <ChatInterface
          onPropertiesFound={handlePropertiesFound}
          onTopResultCoordinates={handleTopResultCoordinates}
          onRawSearchResults={handleRawSearchResults}
          onCommunityAnalysis={handleCommunityAnalysis}
          sessionId={sessionId}
          onListingSelect={setCurrentListingIndex}
          currentListingIndex={currentListingIndex}
          onTopResultDetails={setTopResultDetails}
        />
      </div>
      <div className="w-3/4 h-full">
        <MapView
          selectedProperty={selectedProperty}
          allProperties={properties}
          topResultCoords={topResultCoords}
          topResultDetails={topResultDetails}
          rawSearchResults={rawSearchResults}
          onNextListing={handleNextListing}
          currentListingIndex={currentListingIndex}
          communityAnalysis={communityAnalysis}
        />
      </div>
    </div>
  );
}
