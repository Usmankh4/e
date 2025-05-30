import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';

// Initialize Stripe only once at the module level
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

export function useStripe() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const createCheckoutSession = async (productData) => {
    try {
      setLoading(true);
      setError(null);
      
      // Log the request for debugging
      console.log('Creating checkout session with data:', productData);
      
      // Use the correct API endpoint for buy now functionality
      const apiUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'}/myapp/api/create-buy-now-session/`;
      
      console.log('Sending request to:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          variant_id: productData.variant_id,
          quantity: productData.quantity,
          // Include success and cancel URLs if needed
          success_url: `${window.location.origin}/checkout/success`,
          cancel_url: `${window.location.origin}/checkout/cancel`
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response:', errorText);
        throw new Error(`Failed to create checkout session: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Checkout session created:', data);
      
      // Store the session ID in localStorage before redirecting
      if (data.id) {
        localStorage.setItem('stripe_checkout_session_id', data.id);
      }
      
      // Redirect to Stripe checkout
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error('No checkout URL returned from server');
      }
      
      return { success: true };
    } catch (err) {
      console.error('Error creating checkout session:', err);
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  };

  return {
    createCheckoutSession,
    loading,
    error,
    stripePromise
  };
}
