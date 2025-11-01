// API Types for Homes AI Algarve Backend Integration
// Based on PRD requirements and backend models

export interface UserRequirements {
  budget_min?: number;
  budget_max?: number;
  bedrooms?: number;
  bathrooms?: number;
  location: string;
  additional_info?: string;
}

export interface PropertyListing {
  address?: string;
  city?: string;
  price?: number;
  bedrooms?: number;
  bathrooms?: number;
  sqft?: number;
  description?: string;
  url?: string;
  latitude?: number;
  longitude?: number;
  image_url?: string;
  compatibility_score?: number;
}

export interface SeekerProfile {
  budget_min?: number;
  budget_max: number;
  schedule: 'early' | 'standard' | 'late';
  pets: boolean;
  smoking: boolean;
  wfh_days: number;
  cleanliness: 'low' | 'med' | 'high';
  noise_tolerance: 'low' | 'med' | 'high';
  preferred_cities: string[];
}

export interface HouseProfile {
  city: string;
  rooms: number;
  rules_pets: boolean;
  rules_smoking: boolean;
  quiet_hours: string;
  bills_included: boolean;
  internet_speed_mbps?: number;
  existing_tenants: number;
  landlord_contact: string;
}

export interface MatchResponse {
  score: number; // 0-100
  reasons: string[];
  session_id: string;
}

export interface SearchRequest {
  user_message: string;
  session_id: string;
  seeker_profile?: SeekerProfile;
}

export interface SearchResponse {
  properties: PropertyListing[];
  search_summary: string;
  total_found: number;
  session_id: string;
}

export interface POI {
  name: string;
  category: string;
  latitude: number;
  longitude: number;
  address?: string;
  distance_meters?: number;
}

export interface FAQItem {
  question: string;
  answer: string;
  links?: Array<{
    title: string;
    url: string;
  }>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  properties?: PropertyListing[];
  loading?: boolean;
}

// Backend API Response Types
export interface ChatResponse {
  status: string;
  data: {
    message?: string;
    properties?: PropertyListing[];
    search_summary?: string;
    total_found?: number;
    agent_message?: string;
    is_complete?: boolean;
    is_general_question?: boolean;
  };
}


