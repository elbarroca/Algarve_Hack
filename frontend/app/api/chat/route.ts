import { NextRequest } from 'next/server';

// Backend uAgents REST endpoint
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';

// Force dynamic behavior (no caching)
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function POST(req: NextRequest) {
  try {
    const { message, sessionId } = await req.json();

    // Call uAgents REST endpoint
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId || 'default'
      })
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    // Parse single JSON response from uAgents REST
    const data = await response.json();

    return Response.json(data);

  } catch (error) {
    console.error('Chat API error:', error);
    return Response.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}
