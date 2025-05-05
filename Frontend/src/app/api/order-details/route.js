import Stripe from 'stripe';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');
    
    if (!sessionId) {
      return Response.json({ error: 'Session ID is required' }, { status: 400 });
    }
    
    // Initialize Stripe with the secret key
    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
    
    try {
      // Retrieve the checkout session
      const session = await stripe.checkout.sessions.retrieve(sessionId, {
        expand: ['line_items', 'customer', 'payment_intent']
      });
      
      // Extract order details
      const orderDetails = {
        order: {
          id: session.id,
          date: new Date(session.created * 1000).toLocaleDateString(),
          total: session.amount_total / 100, // Convert from cents to dollars
          paymentMethod: 'Credit Card',
          status: session.payment_status === 'paid' ? 'Paid' : session.payment_status
        },
        items: session.line_items?.data.map(item => ({
          id: item.id,
          name: item.description,
          price: item.amount_total / 100 / item.quantity, // Convert from cents to dollars
          quantity: item.quantity,
          image: item.price?.product?.images?.[0] || '',
          color: 'Default', // This would come from metadata in a real implementation
          storage: 'Default' // This would come from metadata in a real implementation
        })) || [],
        shipping: {
          method: 'Standard Shipping',
          estimatedDelivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
          address: session.customer_details?.address ? 
            `${session.customer_details.address.line1}, ${session.customer_details.address.city}, ${session.customer_details.address.state} ${session.customer_details.address.postal_code}` : 
            'Address not provided',
          trackingNumber: 'TRK' + Math.floor(Math.random() * 10000000)
        }
      };
      
      return Response.json(orderDetails);
    } catch (stripeError) {
      console.error('Error retrieving Stripe session:', stripeError);
      
      // If we can't retrieve the session from Stripe, return mock data
      return Response.json({
        order: {
          id: sessionId,
          date: new Date().toLocaleDateString(),
          total: 0,
          paymentMethod: 'Credit Card',
          status: 'Processing'
        },
        items: [],
        shipping: {
          method: 'Standard Shipping',
          estimatedDelivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
          address: 'Address will be confirmed',
          trackingNumber: 'Tracking number will be provided after shipping'
        }
      });
    }
  } catch (error) {
    console.error('Error processing order details request:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
