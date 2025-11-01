// Common TypeScript types and interfaces

export interface NavLink {
  label: string;
  href: string;
  external?: boolean;
}

export interface Feature {
  icon: string;
  title: string;
  description: string;
  gradient: string;
}

export interface Stat {
  value: string;
  label: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  tags: string[];
  imageUrl?: string;
  link?: string;
  featured?: boolean;
}

export interface Service {
  icon: string;
  title: string;
  description: string;
  features: string[];
  color: string;
}

export interface Testimonial {
  id: string;
  name: string;
  role: string;
  company: string;
  testimonial: string;
  avatar?: string;
  rating?: number;
}

export interface ContactInfo {
  name: string;
  email: string;
  message: string;
  phone?: string;
  subject?: string;
}

export interface SocialLink {
  name: string;
  href: string;
  icon: string;
}

export type ButtonVariant = 'primary' | 'secondary' | 'outline';
export type ButtonSize = 'small' | 'medium' | 'large';
export type LoadingSize = 'small' | 'medium' | 'large';

