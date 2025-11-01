// Real API Service - Connected to Backend uAgents System
// NO MOCK DATA - All real API calls

import {
  PropertyListing,
  ChatMessage,
  POI,
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface ChatRequest {
  message: string;
  session_id: string;
}

interface ChatResponse {
  status: string;
  data: {
    message?: string;
    properties?: PropertyListing[];
    search_summary?: string;
    total_found?: number;
    agent_message?: string;
    is_complete?: boolean;
    is_general_question?: boolean;
    community_analysis?: any;
    geocoded_results?: Array<{
      index: number;
      latitude: number;
      longitude: number;
      address: string;
    }>;
    poi_results?: Array<{
      listing_index: number;
      pois: POI[];
    }>;
  };
}

class RealHomesAIAPI {
  private sessionId: string;

  constructor() {
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Send chat message to backend - REAL API CALL
   */
  async sendChatMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: this.sessionId,
        } as ChatRequest),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      return data as ChatResponse;
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  }

  /**
   * Get health status from backend
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Try to connect to the chat endpoint to verify backend is running
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'test',
          session_id: 'health_check',
        }),
      });
      // If we get a response (even error), backend is running
      return response.status !== 0;
    } catch {
      return false;
    }
  }

  /**
   * Get session ID
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Reset session
   */
  resetSession(): void {
    this.sessionId = this.generateSessionId();
  }
}

export const realAPI = new RealHomesAIAPI();
