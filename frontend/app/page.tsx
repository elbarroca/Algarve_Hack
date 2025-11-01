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
    // Convert backend properties to frontend Property format
    const geoReady = newProperties.filter(
      (prop) => typeof prop.latitude === 'number' && typeof prop.longitude === 'number'
    );

    const convertedProperties: Property[] = geoReady.map((prop, idx) => ({
      id: idx + 1000,
      address: prop.address || prop.title || 'Unknown Address',
      city: prop.location || 'Bay Area',
      state: 'CA',
      price: prop.price || 0,
      bedrooms: prop.bedrooms || 0,
      bathrooms: prop.bathrooms || 0,
      sqft: 0,
      latitude: prop.latitude,
      longitude: prop.longitude,
      description: prop.description || '',
      imageUrl: '/properties/default.jpg',
      propertyType: 'Single Family'
    }));

    // Set converted properties (no mock data fallback)
    setProperties(convertedProperties);
  };

  const handleRawSearchResults = (results: any[]) => {
    console.log('[Home] Storing raw search results:', results.length);
    console.log('[Home] Raw results with POIs:', results);

    // Limit to 5 listings max for faster cycling
    const limitedResults = results.slice(0, 5);
    setRawSearchResults(limitedResults);
    setCurrentListingIndex(0); // Reset to first listing

    // Extract top result details
    if (limitedResults.length > 0) {
      const topResult = limitedResults[0];
      console.log('[Home] Top result details:', topResult);
      console.log('[Home] Top result POIs:', topResult.pois);
      setTopResultDetails(topResult);
    }
  };

  const handleNextListing = () => {
    if (rawSearchResults.length === 0) return;

    const nextIndex = (currentListingIndex + 1) % rawSearchResults.length;
    setCurrentListingIndex(nextIndex);

    const nextListing = rawSearchResults[nextIndex];
    console.log('[Home] Cycling to listing', nextIndex + 1, 'of', rawSearchResults.length, ':', nextListing);

    // Force update by creating completely new objects with timestamp
    const timestamp = Date.now();

    // Update top result details - create new object to force re-render
    setTopResultDetails({
      ...nextListing,
      _updateKey: timestamp
    });

    // Update coordinates - create new object to force map update
    if (nextListing.latitude && nextListing.longitude) {
      setTopResultCoords({
        latitude: nextListing.latitude,
        longitude: nextListing.longitude,
        address: nextListing.address || nextListing.title || 'Unknown Address',
        image_url: nextListing.image_url,
        _updateKey: timestamp
      });
    }
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
