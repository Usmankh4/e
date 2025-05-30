"use client";
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import '../../globals.css';

export default function CheckoutCancel() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [message, setMessage] = useState('Processing your cancellation...');
  const [error, setError] = useState(null);
  
  useEffect(() => {
    // First try to get the session_id from the URL
    let sessionId = searchParams.get('session_id');
    
    // If not in URL, try to get it from localStorage
    if (!sessionId && typeof window !== 'undefined') {
      sessionId = localStorage.getItem('stripe_checkout_session_id');
      console.log('Retrieved session ID from localStorage:', sessionId);
    }
    
    // Replace {CHECKOUT_SESSION_ID} with an empty string if it's still in the sessionId
    if (sessionId === '{CHECKOUT_SESSION_ID}') {
      console.log('Found placeholder session ID, checking localStorage instead');
      sessionId = localStorage.getItem('stripe_checkout_session_id');
    }
    
    if (!sessionId) {
      console.log('No session ID found in URL or localStorage');
      setMessage('Your checkout has been canceled.');
      return;
    }
    
    console.log('Using session ID for release:', sessionId);
    
    // Clear the session ID from localStorage to prevent reuse
    if (typeof window !== 'undefined') {
      localStorage.removeItem('stripe_checkout_session_id');
    }
    
    // Call our API to release the reservation
    const releaseReservation = async () => {
      try {
        console.log(`Releasing reservation for session: ${sessionId}`);
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000'}/myapp/api/release-checkout-reservation/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            session_id: sessionId
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          console.log('Reservation released successfully:', data);
          setMessage('Your checkout has been canceled and items have been returned to inventory.');
        } else {
          console.error('Error releasing reservation:', data);
          setMessage('Your checkout has been canceled, but there was an issue updating inventory.');
          setError(data.error || 'Unknown error');
        }
      } catch (error) {
        console.error('Error calling release reservation API:', error);
        setMessage('Your checkout has been canceled, but there was an issue updating inventory.');
        setError(error.message);
      }
    };
    
    releaseReservation();
  }, [searchParams]);
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-center mb-4">Checkout Canceled</h1>
        
        <div className="text-center mb-6">
          <p className="mb-2">{message}</p>
          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}
        </div>
        
        <div className="flex justify-center space-x-4">
          <Link href="/cart" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Return to Cart
          </Link>
          <Link href="/" className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  );
}
