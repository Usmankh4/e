export async function GET(request) {
  try {
    // Get session_id from query params
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      return Response.json({ error: 'Session ID is required' }, { status: 400 });
    }
    
    // Call backend to get session details
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/myapp/get-session-details/?session_id=${sessionId}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Error getting session details');
    }
    
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error('Error getting session details:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
