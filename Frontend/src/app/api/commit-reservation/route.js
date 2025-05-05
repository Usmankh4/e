export async function POST(request) {
  try {
    const body = await request.json();
    const { sessionId } = body;
    
    if (!sessionId) {
      return Response.json({ error: 'Session ID is required' }, { status: 400 });
    }
    
    // Call backend to commit the reservation
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/myapp/inventory/commit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Error committing reservation');
    }
    
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error('Error committing reservation:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
