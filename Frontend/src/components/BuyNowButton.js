import { useStripe } from '../hooks/useStripe';

/**
 * Reusable Buy Now button component that handles Stripe checkout
 * Maintains original CSS classes and styling
 */
export default function BuyNowButton({ 
  productId, 
  variantId = null,
  price, 
  quantity, 
  image,
  disabled = false 
}) {
  const { createCheckoutSession, loading } = useStripe();

  const handleBuyNow = async () => {
    await createCheckoutSession({
      variant_id: variantId || productId,
      price: price,
      quantity: quantity,
      image: image
    });
  };

  // Use the original button styling without any additional classes
  return (
    <button 
      onClick={handleBuyNow} 
      disabled={disabled || loading}
    >
      {loading ? 'Processing...' : 'Buy Now'}
    </button>
  );
}
