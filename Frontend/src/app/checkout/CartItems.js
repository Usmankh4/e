"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { loadStripe } from '@stripe/stripe-js';

// Debug the environment variable
console.log("Stripe Key in CartItems:", process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

// Initialize Stripe with the publishable key from environment variables
// Only initialize if the key is available
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

export default function CartItems() {
  const [cartItems, setCartItems] = useState([]);
  const router = useRouter();

  useEffect(() => {
    // Get cart items from localStorage
    const getCartFromStorage = () => {
      const cart = localStorage.getItem('cart');
      const parsedCart = cart ? JSON.parse(cart) : [];
      console.log("Cart from localStorage:", parsedCart);
      return parsedCart;
    };
    
    setCartItems(getCartFromStorage());
  }, []);

  const handleRemoveFromCart = (id) => {
    const updatedCart = cartItems.map(item => {
      if (item.id === id) {
        return { ...item, quantity: item.quantity - 1 };
      }
      return item;
    }).filter(item => item.quantity > 0);

    setCartItems(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
  };

  const navigateToProduct = (item) => {
    // Add detailed debugging
    console.log("Item being navigated to:", JSON.stringify(item, null, 2));
    console.log("Item properties:", Object.keys(item));
    
    // Use slug if available, otherwise fall back to ID
    const productIdentifier = item.slug || item.productId;
    console.log("Navigating to product with identifier:", productIdentifier, "of type:", typeof productIdentifier);
    router.push(`/products/${item.brand}/${productIdentifier}`);
  };

  const handleCheckout = async () => {
    try {
      console.log("Starting checkout process with cart items:", cartItems);
      
      // Transform cart items to the format expected by the backend
      const formattedItems = cartItems.map(item => {
        console.log("Processing cart item:", item);
        return {
          variant_id: item.variantId, // Use the explicit variantId field
          quantity: item.quantity,
          product_id: item.productId
        };
      });
      
      console.log("Formatted items for backend:", formattedItems);
      
      // Check if we have any valid variant IDs
      if (formattedItems.length === 0) {
        console.error("No items in cart");
        alert("Your cart is empty. Please add items before checking out.");
        return;
      }
      
      // Check if all items have variant IDs
      const missingVariantIds = formattedItems.filter(item => !item.variant_id);
      if (missingVariantIds.length > 0) {
        console.error("Some items are missing variant IDs:", missingVariantIds);
        alert("There was an issue with some items in your cart. Please try adding them again.");
        return;
      }
      
      // Log the request data for debugging
      console.log("Making request to:", `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/create-checkout-session/`);
      console.log("With request data:", { 
        items: formattedItems,
        success_url: window.location.origin + '/checkout/success',
        cancel_url: window.location.origin + '/checkout/cancel?session_id={CHECKOUT_SESSION_ID}'
      });
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/create-checkout-session/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          items: formattedItems,
          success_url: window.location.origin + '/checkout/success',
          cancel_url: window.location.origin + '/checkout/cancel?session_id={CHECKOUT_SESSION_ID}'
        }),
      });
      
      // Log the response status and headers for debugging
      console.log("Response status:", response.status);
      console.log("Response headers:", Object.fromEntries([...response.headers.entries()]));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Server response error:', response.status, errorText);
        throw new Error(`Failed to create checkout session: ${response.status} ${errorText}`);
      }
      
      const responseData = await response.json();
      console.log("Checkout response data:", responseData);
      
      // Check if we have a direct URL to redirect to
      if (responseData.url) {
        console.log("Redirecting directly to Stripe URL:", responseData.url);
        // Store the session ID in localStorage before redirecting
        if (responseData.id) {
          console.log("Storing session ID in localStorage:", responseData.id);
          localStorage.setItem('stripe_checkout_session_id', responseData.id);
        }
        window.location.href = responseData.url;
        return;
      }
      
      // Fall back to the old method if no direct URL is provided
      const sessionId = responseData.id || responseData.sessionId;
      if (!sessionId) {
        console.error("No session ID found in response:", responseData);
        throw new Error("No session ID returned from server");
      }
      
      console.log("Redirecting to checkout with session ID:", sessionId);
      const stripe = await stripePromise;
      
      // Check if Stripe is properly initialized
      if (!stripe) {
        console.error("Stripe is not initialized. Check if NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY is set correctly.");
        alert("Payment system is not properly configured. Please try again later or contact support.");
        return;
      }
      
      const { error } = await stripe.redirectToCheckout({ sessionId });
      
      if (error) {
        console.error('Error redirecting to Stripe checkout:', error);
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  };

  const totalAmount = cartItems.reduce((total, item) => total + item.price * item.quantity, 0);

  if (cartItems.length === 0) {
    return (
      <div className="CartPage">
        <h1>Your cart is empty</h1>
      </div>
    );
  }

  return (
    <div className="CartPage">
      <h1>Your Cart Page</h1>
      {cartItems.map((item) => (
        <div key={item.id} className="CartItem">
          <div className="productImage" onClick={() => navigateToProduct(item)}>
            <img src={item.image} alt={item.name} style={{ cursor: 'pointer' }} />
          </div>
          <div className="ProductDetails">
            <h3>{item.name}</h3>
            <p>${(item.price * item.quantity).toFixed(2)}</p>
            {/* Only show color if it's not 'Default' */}
            {item.color && item.color !== 'Default' && (
              <p>Colour: {item.color}</p>
            )}
            {/* Only show storage if it's not 'Default' */}
            {item.storage && item.storage !== 'Default' && (
              <p>Storage: {item.storage}</p>
            )}
            <p>Quantity: {item.quantity}</p>
          </div>
          <div className="RemoveButton">
            <button onClick={() => handleRemoveFromCart(item.id)}>Remove</button>
          </div>
        </div>
      ))}
      <div className="CartTotal">
        <div className="TotalAmount">
          <h2>Total: ${totalAmount.toFixed(2)}</h2>
        </div>
        <div className="CheckoutButton">
          <button onClick={handleCheckout}>Checkout</button>
        </div>
      </div>
    </div>
  );
}
