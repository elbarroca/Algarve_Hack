'use client';

import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { Property } from '@/lib/mockData';

interface NegotiationModalProps {
  property: Property;
  onClose: () => void;
}

export function NegotiationModal({ property, onClose }: NegotiationModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    additionalInfo: '',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isProbing, setIsProbing] = useState(false);
  const [isCallInProgress, setIsCallInProgress] = useState(false);
  const [callSummary, setCallSummary] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      console.log('Sending negotiation request:', {
        address: property.address,
        name: formData.name,
        email: formData.email,
        additional_info: formData.additionalInfo,
      });

      // Immediately show probing screen
      setIsSubmitting(false);
      setIsProbing(true);

      const response = await fetch('http://localhost:8080/api/negotiate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: property.address,
          name: formData.name,
          email: formData.email,
          additional_info: formData.additionalInfo,
        }),
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        // Reset to form and show error
        setIsProbing(false);
        setIsCallInProgress(false);
        setError(`Failed to start negotiation: ${response.status}`);
        return;
      }

      // When we get response, probing is done and call has started
      // Transition from probing to call in progress
      setIsProbing(false);
      setIsCallInProgress(true);

      const result = await response.json();
      console.log('Negotiation completed:', result);

      // Check if response has success flag
      if (result.success) {
        // Store the result and transition to summary
        setCallSummary(result);
        setIsCallInProgress(false);
      } else {
        // Show error and go back to form
        setIsCallInProgress(false);
        setError(result.message || 'Unknown error');
      }
    } catch (err) {
      console.error('Negotiation error:', err);
      setIsProbing(false);
      setIsCallInProgress(false);
      setError('Failed to start negotiation. Please try again.');
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  // Generate next actions from call summary if not provided
  const generateNextActions = (summary: any): string[] => {
    const actions = [];

    if (summary?.findings && summary.findings.length > 0) {
      actions.push('Review identified leverage points with your agent');
      actions.push('Prepare counter-offer based on findings');
    }

    if (summary?.leverage_score && summary.leverage_score < 5) {
      actions.push('Consider improving your negotiation position');
    } else if (summary?.leverage_score && summary.leverage_score >= 7) {
      actions.push('Proceed with confidence - strong negotiation position');
    }

    actions.push('Schedule follow-up call with listing agent');
    actions.push('Prepare offer documentation');

    return actions;
  };

  // Probing screen - gathering intelligence
  if (isProbing) {
    return createPortal(
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-lg" onClick={(e) => e.stopPropagation()}>
        <div className="relative w-full max-w-md bg-gradient-to-br from-slate-900/95 to-slate-800/95 border border-blue-500/30 rounded-2xl shadow-2xl backdrop-blur-xl p-8" onClick={(e) => e.stopPropagation()}>
          <div className="flex flex-col items-center space-y-6">
            {/* Animated search icon */}
            <div className="relative">
              <div className="absolute inset-0 animate-ping">
                <div className="w-20 h-20 rounded-full bg-blue-500/30"></div>
              </div>
              <div className="relative z-10 w-20 h-20 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* Loading text */}
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold text-white">Probing Property</h3>
              <p className="text-white/60">Gathering intelligence and leverage data...</p>
            </div>

            {/* Loading dots */}
            <div className="flex gap-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>,
      document.body
    );
  }

  // Loading screen during call
  if (isCallInProgress) {
    return createPortal(
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-lg" onClick={(e) => e.stopPropagation()}>
        <div className="relative w-full max-w-md bg-gradient-to-br from-slate-900/95 to-slate-800/95 border border-purple-500/30 rounded-2xl shadow-2xl backdrop-blur-xl p-8" onClick={(e) => e.stopPropagation()}>
          <div className="flex flex-col items-center space-y-6">
            {/* Animated phone icon */}
            <div className="relative">
              <div className="absolute inset-0 animate-ping">
                <div className="w-20 h-20 rounded-full bg-purple-500/30"></div>
              </div>
              <div className="relative z-10 w-20 h-20 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                <svg className="w-10 h-10 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                </svg>
              </div>
            </div>

            {/* Loading text */}
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-bold text-white">Call in Progress</h3>
              <p className="text-white/60">Our AI agent is negotiating on your behalf...</p>
            </div>

            {/* Loading dots */}
            <div className="flex gap-2">
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      </div>,
      document.body
    );
  }

  // Show call summary after call completes
  if (callSummary) {
    return createPortal(
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900/95 to-slate-800/95 border border-green-500/30 rounded-2xl shadow-2xl backdrop-blur-xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors z-10"
            aria-label="Close modal"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Header */}
          <div className="p-6 border-b border-white/10">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Call Summary</h2>
                <p className="text-sm text-white/60">Negotiation completed successfully</p>
              </div>
            </div>
          </div>

          {/* Summary Content */}
          <div className="p-6 space-y-6">
            {/* Call Summary */}
            {callSummary.call_summary && (
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-white/90">Call Summary</h3>
                <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-lg p-4">
                  <p className="text-white/80 leading-relaxed whitespace-pre-wrap">{callSummary.call_summary}</p>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-white/10">
            <button
              onClick={onClose}
              className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 rounded-lg text-white font-semibold shadow-lg shadow-green-500/20 transition-all"
            >
              Complete & Close
            </button>
            <p className="text-center text-white/40 text-xs mt-3">
              Review your next actions above and proceed with your negotiation strategy
            </p>
          </div>
        </div>
      </div>,
      document.body
    );
  }

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-gradient-to-br from-slate-900/95 to-slate-800/95 border border-white/20 rounded-2xl shadow-2xl backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors z-10"
          aria-label="Close modal"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Header - Property Info */}
        <div className="p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white mb-2">
            Start AI Negotiation
          </h2>
          <p className="text-sm text-white/60 mb-3">
            Our AI agent will negotiate this property on your behalf
          </p>
          <div className="space-y-1">
            <p className="text-lg text-white/90 font-semibold">
              {property.address}
            </p>
            {property.city && property.state && property.city !== 'N/A' && property.state !== 'N/A' && (
              <p className="text-sm text-white/70">
                {property.city}, {property.state}
              </p>
            )}
            {property.price && property.price > 0 && (
              <div className="flex items-center gap-2 mt-3">
                <span className="text-sm text-white/60">Listed Price:</span>
                <span className="text-xl font-bold text-green-400">
                  {formatPrice(property.price)}
                </span>
              </div>
            )}
            {(property.bedrooms || property.bathrooms || property.sqft) && (
              <div className="text-xs text-white/50 mt-1">
                {property.bedrooms ? `${property.bedrooms} beds` : ''}
                {property.bedrooms && (property.bathrooms || property.sqft) ? ' • ' : ''}
                {property.bathrooms ? `${property.bathrooms} baths` : ''}
                {property.bathrooms && property.sqft ? ' • ' : ''}
                {property.sqft ? `${property.sqft.toLocaleString()} sqft` : ''}
              </div>
            )}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Contact Information Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white/90 border-b border-white/10 pb-2">
              Your Information
            </h3>

            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Full Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Email <span className="text-red-400">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all"
                placeholder="john@example.com"
              />
            </div>
          </div>

          {/* Additional Information Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white/90 border-b border-white/10 pb-2">
              Negotiation Preferences
            </h3>

            <div>
              <label
                htmlFor="additionalInfo"
                className="block text-sm font-medium text-white/80 mb-2"
              >
                Additional Information
              </label>
              <textarea
                id="additionalInfo"
                name="additionalInfo"
                rows={5}
                value={formData.additionalInfo}
                onChange={handleChange}
                className="w-full px-4 py-2.5 bg-white/5 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all resize-none"
                placeholder="Share any preferences or requirements (budget constraints, move-in timeline, financing status, property concerns, etc.). Our AI agent will use this to negotiate on your behalf."
              />
            </div>

            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
              <p className="text-purple-300 text-sm flex items-start gap-2">
                <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span>Our AI agent will handle the negotiation process with the listing agent on your behalf.</span>
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/20 rounded-lg text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 rounded-lg text-white font-semibold shadow-lg shadow-purple-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Starting...' : 'Start AI Negotiation'}
            </button>
          </div>
        </form>

        {/* Footer Note */}
        <div className="px-6 pb-6">
          <p className="text-xs text-white/40 text-center">
            Our AI agent will contact the listing agent and negotiate on your behalf. You'll receive updates via email.
          </p>
        </div>
      </div>
    </div>,
    document.body
  );
}
