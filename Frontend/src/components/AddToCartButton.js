'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Reusable button component for adding items to cart
 * @param {Object} props - Component props
 * @param {string|number} props.productId - ID of the product/accessory
 * @param {string} props.productType - Type of product ('product' or 'accessory')
 * @param {Object} props.variant - Optional variant data for products with variants
 * @param {boolean} props.disabled - Whether the button is disabled
 */
export default function AddToCartButton({ productId, productType, variant, disabled = false }) {
  const [quantity, setQuantity] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const router = useRouter();

  const handleAddToCart = async () => {
    if (disabled) return;
    
    setIsLoading(true);
    setMessage('');
    
    try {
      const payload = {
        product_id: productId,
        quantity: quantity,
        product_type: productType
      };
      
      // Add variant data if provided (for products with variants)
      if (variant && productType === 'product') {
        payload.variant_id = variant.id;
      }
      
      const response = await fetch('http://127.0.0.1:8000/myapp/api/cart/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to add item to cart');
      }
      
      const data = await response.json();
      setMessage('Added to cart!');
      
      // Refresh the page to update cart count
      router.refresh();
      
      // Optional: Redirect to cart
      // router.push('/cart');
    } catch (error) {
      console.error('Error adding to cart:', error);
      setMessage('Error adding to cart. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="AddToCartContainer">
      <div className="QuantitySelector">
        <button 
          className="QuantityButton"
          onClick={() => setQuantity(prev => Math.max(1, prev - 1))}
          disabled={quantity <= 1 || disabled}
        >
          -
        </button>
        <span className="QuantityValue">{quantity}</span>
        <button 
          className="QuantityButton"
          onClick={() => setQuantity(prev => prev + 1)}
          disabled={disabled}
        >
          +
        </button>
      </div>
      
      <button 
        className="AddToCartButton"
        onClick={handleAddToCart}
        disabled={disabled || isLoading}
      >
        {isLoading ? 'Adding...' : 'Add to Cart'}
      </button>
      
      {message && (
        <div className="CartMessage">
          {message}
        </div>
      )}
    </div>
  );
}
