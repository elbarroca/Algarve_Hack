export interface Property {
  id: number;
  address: string;
  city: string;
  state: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  latitude: number;
  longitude: number;
  description: string;
  imageUrl: string;
  propertyType: string;
}

export const mockProperties: Property[] = [
  {
    id: 1,
    address: "2847 Steiner St",
    city: "San Francisco",
    state: "CA",
    price: 2850000,
    bedrooms: 4,
    bathrooms: 3.5,
    sqft: 3200,
    latitude: 37.7989,
    longitude: -122.4368,
    description: "Stunning Victorian home in Pacific Heights with breathtaking bay views. Completely renovated with modern amenities while preserving historic charm.",
    imageUrl: "/properties/sf1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 2,
    address: "125 University Ave",
    city: "Palo Alto",
    state: "CA",
    price: 3250000,
    bedrooms: 5,
    bathrooms: 4,
    sqft: 4100,
    latitude: 37.4419,
    longitude: -122.1430,
    description: "Luxurious contemporary home near Stanford University. Features smart home technology, gourmet kitchen, and outdoor entertainment area.",
    imageUrl: "/properties/paloalto1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 3,
    address: "8765 Mountain View Dr",
    city: "Oakland",
    state: "CA",
    price: 1450000,
    bedrooms: 3,
    bathrooms: 2.5,
    sqft: 2400,
    latitude: 37.8044,
    longitude: -122.2711,
    description: "Modern craftsman home in desirable Oakland Hills neighborhood. Open floor plan with panoramic views of the Bay Area.",
    imageUrl: "/properties/oakland1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 4,
    address: "456 Castro St",
    city: "San Francisco",
    state: "CA",
    price: 1895000,
    bedrooms: 3,
    bathrooms: 2,
    sqft: 1850,
    latitude: 37.7625,
    longitude: -122.4351,
    description: "Charming Edwardian in the heart of Castro District. Updated kitchen, original hardwood floors, and private garden.",
    imageUrl: "/properties/sf2.jpg",
    propertyType: "Single Family"
  },
  {
    id: 5,
    address: "2100 Sand Hill Rd",
    city: "Menlo Park",
    state: "CA",
    price: 4750000,
    bedrooms: 6,
    bathrooms: 5.5,
    sqft: 5800,
    latitude: 37.4530,
    longitude: -122.1817,
    description: "Spectacular estate in prestigious Menlo Park location. Resort-style backyard with pool, spa, and outdoor kitchen.",
    imageUrl: "/properties/menlopark1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 6,
    address: "789 Embarcadero",
    city: "San Francisco",
    state: "CA",
    price: 2200000,
    bedrooms: 2,
    bathrooms: 2,
    sqft: 1600,
    latitude: 37.7955,
    longitude: -122.3937,
    description: "Luxury waterfront condo with floor-to-ceiling windows and stunning bay views. Premium building amenities including gym and concierge.",
    imageUrl: "/properties/sf3.jpg",
    propertyType: "Condo"
  },
  {
    id: 7,
    address: "3421 Park Blvd",
    city: "Berkeley",
    state: "CA",
    price: 1650000,
    bedrooms: 4,
    bathrooms: 3,
    sqft: 2800,
    latitude: 37.8715,
    longitude: -122.2730,
    description: "Beautiful Mediterranean-style home near UC Berkeley. Spacious layout with multiple living areas and mature landscaping.",
    imageUrl: "/properties/berkeley1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 8,
    address: "567 Main St",
    city: "San Jose",
    state: "CA",
    price: 1550000,
    bedrooms: 4,
    bathrooms: 3,
    sqft: 2900,
    latitude: 37.3382,
    longitude: -121.8863,
    description: "Contemporary home in prime San Jose location. Energy-efficient design with solar panels and Tesla charging station.",
    imageUrl: "/properties/sanjose1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 9,
    address: "1234 Redwood Ave",
    city: "Redwood City",
    state: "CA",
    price: 2100000,
    bedrooms: 4,
    bathrooms: 3.5,
    sqft: 3400,
    latitude: 37.4852,
    longitude: -122.2364,
    description: "Elegant home with modern finishes and custom upgrades throughout. Chef's kitchen and luxurious master suite.",
    imageUrl: "/properties/redwoodcity1.jpg",
    propertyType: "Single Family"
  },
  {
    id: 10,
    address: "890 Noe Valley Dr",
    city: "San Francisco",
    state: "CA",
    price: 2450000,
    bedrooms: 3,
    bathrooms: 2.5,
    sqft: 2200,
    latitude: 37.7505,
    longitude: -122.4331,
    description: "Stunning remodeled home in family-friendly Noe Valley. Private backyard oasis and top-rated schools nearby.",
    imageUrl: "/properties/sf4.jpg",
    propertyType: "Single Family"
  },
  {
    id: 11,
    address: "2345 El Camino Real",
    city: "Mountain View",
    state: "CA",
    price: 1850000,
    bedrooms: 3,
    bathrooms: 2.5,
    sqft: 2100,
    latitude: 37.3861,
    longitude: -122.0839,
    description: "Modern townhome near Google campus. Low-maintenance living with contemporary design and smart home features.",
    imageUrl: "/properties/mountainview1.jpg",
    propertyType: "Townhouse"
  },
  {
    id: 12,
    address: "678 Mission St",
    city: "San Francisco",
    state: "CA",
    price: 1250000,
    bedrooms: 2,
    bathrooms: 2,
    sqft: 1400,
    latitude: 37.7873,
    longitude: -122.4009,
    description: "Urban loft in vibrant SoMa district. Exposed brick, high ceilings, and walking distance to tech companies.",
    imageUrl: "/properties/sf5.jpg",
    propertyType: "Condo"
  },
  {
    id: 13,
    address: "4567 Skyline Blvd",
    city: "Oakland",
    state: "CA",
    price: 1750000,
    bedrooms: 4,
    bathrooms: 3,
    sqft: 3100,
    latitude: 37.8272,
    longitude: -122.1814,
    description: "Mid-century modern gem with panoramic views. Recently updated with designer finishes and outdoor deck.",
    imageUrl: "/properties/oakland2.jpg",
    propertyType: "Single Family"
  },
  {
    id: 14,
    address: "123 Stanford Ave",
    city: "Palo Alto",
    state: "CA",
    price: 2950000,
    bedrooms: 4,
    bathrooms: 3.5,
    sqft: 3600,
    latitude: 37.4275,
    longitude: -122.1697,
    description: "Classic California ranch-style home in Old Palo Alto. Beautifully landscaped grounds and indoor-outdoor living.",
    imageUrl: "/properties/paloalto2.jpg",
    propertyType: "Single Family"
  },
  {
    id: 15,
    address: "5678 Sunset Blvd",
    city: "San Francisco",
    state: "CA",
    price: 1650000,
    bedrooms: 3,
    bathrooms: 2,
    sqft: 1950,
    latitude: 37.7599,
    longitude: -122.4648,
    description: "Charming home in the Sunset District. Recently renovated with ocean views and close to Golden Gate Park.",
    imageUrl: "/properties/sf6.jpg",
    propertyType: "Single Family"
  }
];

export function searchProperties(filters: {
  city?: string;
  minPrice?: number;
  maxPrice?: number;
  bedrooms?: number;
  propertyType?: string;
}): Property[] {
  return mockProperties.filter(property => {
    if (filters.city && property.city.toLowerCase() !== filters.city.toLowerCase()) {
      return false;
    }
    if (filters.minPrice && property.price < filters.minPrice) {
      return false;
    }
    if (filters.maxPrice && property.price > filters.maxPrice) {
      return false;
    }
    if (filters.bedrooms && property.bedrooms < filters.bedrooms) {
      return false;
    }
    if (filters.propertyType && property.propertyType !== filters.propertyType) {
      return false;
    }
    return true;
  });
}
