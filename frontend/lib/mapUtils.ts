/**
 * Utility functions for Mapbox map operations
 */

/**
 * Create a circle polygon around a center point
 * @param center - [longitude, latitude]
 * @param radiusInMeters - radius in meters
 * @param points - number of points to use for the circle (more = smoother)
 * @returns GeoJSON Feature with Polygon geometry
 */
export function createCircle(
  center: [number, number],
  radiusInMeters: number,
  points: number = 64
) {
  const coords = {
    latitude: center[1],
    longitude: center[0]
  };

  const km = radiusInMeters / 1000;
  const ret = [];
  const distanceX = km / (111.32 * Math.cos((coords.latitude * Math.PI) / 180));
  const distanceY = km / 110.574;

  for (let i = 0; i < points; i++) {
    const theta = (i / points) * (2 * Math.PI);
    const x = distanceX * Math.cos(theta);
    const y = distanceY * Math.sin(theta);

    ret.push([coords.longitude + x, coords.latitude + y]);
  }
  ret.push(ret[0]); // Close the ring

  return {
    type: 'Feature' as const,
    geometry: {
      type: 'Polygon' as const,
      coordinates: [ret]
    },
    properties: {}
  };
}

/**
 * Fetch routes from Mapbox Directions API
 */
export async function fetchRoute(
  origin: [number, number],
  destination: [number, number],
  profile: 'driving' | 'walking' | 'cycling' = 'driving',
  accessToken: string
) {
  const url = `https://api.mapbox.com/directions/v5/mapbox/${profile}/${origin[0]},${origin[1]};${destination[0]},${destination[1]}?geometries=geojson&access_token=${accessToken}`;

  const response = await fetch(url);
  const data = await response.json();

  if (data.routes && data.routes.length > 0) {
    const route = data.routes[0];
    return {
      geometry: route.geometry,
      distance: route.distance, // in meters
      duration: route.duration  // in seconds
    };
  }

  return null;
}

/**
 * Fetch distance matrix from Mapbox Matrix API
 * Returns distances and durations from sources to destinations
 */
export async function fetchDistanceMatrix(
  sources: [number, number][],
  destinations: [number, number][],
  profile: 'driving' | 'walking' | 'cycling' = 'driving',
  accessToken: string
) {
  // Build coordinates string
  const allCoords = [...sources, ...destinations];
  const coordinates = allCoords.map(coord => `${coord[0]},${coord[1]}`).join(';');

  // Sources are first N coordinates, destinations are remaining
  const sourceIndices = sources.map((_, i) => i).join(';');
  const destinationIndices = destinations.map((_, i) => i + sources.length).join(';');

  const url = `https://api.mapbox.com/directions-matrix/v1/mapbox/${profile}/${coordinates}?sources=${sourceIndices}&destinations=${destinationIndices}&annotations=distance,duration&access_token=${accessToken}`;

  const response = await fetch(url);
  const data = await response.json();

  if (data.code === 'Ok') {
    return {
      distances: data.distances, // 2D array: distances[sourceIndex][destIndex] in meters
      durations: data.durations, // 2D array: durations[sourceIndex][destIndex] in seconds
      destinations: data.destinations
    };
  }

  return null;
}

/**
 * Format distance for display
 */
export function formatDistance(meters: number): string {
  const miles = meters / 1609.34;
  if (miles < 0.1) {
    return `${Math.round(meters)} m`;
  }
  return `${miles.toFixed(2)} mi`;
}

/**
 * Format duration for display
 */
export function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) {
    return `${minutes} min`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}
