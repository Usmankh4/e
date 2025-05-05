"use client";
import { useState, useEffect, createContext, useContext } from 'react';
import { loadStripe } from '@stripe/stripe-js';

// Create a context for Stripe
const StripeContext = createContext(null);

export function useStripe() {
  return useContext(StripeContext);
}

export function StripeProvider({ children }) {
  const [stripe, setStripe] = useState(null);
  
  useEffect(() => {
    // Initialize Stripe only on the client side
    const initializeStripe = async () => {
      try {
        // Use the environment variable for the Stripe publishable key
        const stripeKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
        const stripeInstance = await loadStripe(stripeKey);
        setStripe(stripeInstance);
      } catch (error) {
        console.error('Failed to initialize Stripe:', error);
      }
    };
    
    initializeStripe();
  }, []);
  
  return (
    <StripeContext.Provider value={stripe}>
      {children}
    </StripeContext.Provider>
  );
}
