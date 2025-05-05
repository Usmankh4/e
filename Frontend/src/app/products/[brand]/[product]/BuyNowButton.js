"use client";
import { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';

// Debug the environment variable
console.log("Stripe Key in BuyNowButton:", process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

// Initialize Stripe with the publishable key from environment variables
// Only initialize if the key is available
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

export default function BuyNowButton({ productId, defaultPrice, defaultImage }) {
  const [quantity, setQuantity] = useState(1);

  // Listen for changes in quantity
  useEffect(() => {
    const quantityElement = document.querySelector('.QuantitySelection span');
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'characterData' || mutation.type === 'childList') {
          const newQuantity = parseInt(quantityElement.textContent, 10);
          if (!isNaN(newQuantity)) {
            setQuantity(newQuantity);
          }
        }
      });
    });
    
    if (quantityElement) {
      observer.observe(quantityElement, { characterData: true, childList: true, subtree: true });
    }
    
    return () => {
      observer.disconnect();
    };
  }, []);

  const handleBuyNow = async () => {
    // Get current image from the product image element
    const productImageElement = document.querySelector('.ProductImage img');
    const currentImage = productImageElement ? productImageElement.src : defaultImage;
    
    // Get current price from the price element
    const priceElement = document.querySelector('.ProductPrice h3');
    const priceText = priceElement ? priceElement.textContent.replace('$', '') : defaultPrice.toString();
    const currentPrice = parseFloat(priceText);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/create-buy-now-session/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          variant_id: productId,
          price: isNaN(currentPrice) ? defaultPrice : currentPrice,
          quantity: quantity,
          image: currentImage
        }),
      });
      
      const { id, url } = await response.json();
      // Redirect directly to the Stripe checkout URL
      window.location.href = url;
    } catch (error) {
      console.error('Error creating buy now session:', error);
    }
  };

  return (
    <button onClick={handleBuyNow}>Buy Now</button>
  );
}
