import Stripe from 'stripe';

export async function POST(request) {
  try {
    const body = await request.json();
    
    // Call our backend API instead of using Stripe directly
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/myapp/create-buy-now-session/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        variant_id: body.variantId,
        quantity: body.quantity || 1,
        success_url: `${request.headers.get('origin')}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${request.headers.get('origin')}/checkout/cancel`,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Error creating checkout session');
    }
    
    const sessionData = await response.json();
    return Response.json({ sessionId: sessionData.id, url: sessionData.url });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
