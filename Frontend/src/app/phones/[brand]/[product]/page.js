"use client";
import { useParams, useRouter } from 'next/navigation';
import { z } from 'zod';
import Layout from "../../../../components/Layout";
import StatusMessage from "../../../../components/StatusMessage";
import ProductVariantSelector from "../../../../components/ProductVariantSelector";
import BuyNowButton from "../../../../components/BuyNowButton";
import { usePhoneData } from "../../../../hooks/usePhoneData";
import { useProductVariants } from "../../../../hooks/useProductVariants";
import { addToCart } from "../../../../utils/cartUtils";

// Define schema for cart items
const CartItemSchema = z.object({
  id: z.string(),
  productId: z.string(),
  variantId: z.string().nullable(),
  name: z.string(),
  image: z.string(),
  price: z.number(),
  quantity: z.number(),
  color: z.string(),
  storage: z.string(),
});

export default function PhonePage() {
  const router = useRouter();
  const { product: phoneId, brand } = useParams();
  
  // Use our custom hook to fetch phone data
  const { product: phone, loading, error } = usePhoneData(phoneId);
  
  // Use our custom hook to manage phone variants
  const {
    selectedColor,
    selectedStorage,
    quantity,
    finalPrice,
    imageURL,
    availableStock,
    maxQuantity,
    stockStatus,
    handleColorChange,
    handleStorageChange,
    incrementQuantity,
    decrementQuantity
  } = useProductVariants(phone);

  // Handle adding phone to cart
  const handleAddToCart = () => {
    if (!phone) return;
    
    // Create a unique ID for the cart item
    const cartItemId = `${phone.id}_${selectedColor}_${selectedStorage}`;
    
    // Prepare phone details for cart
    const phoneDetails = {
      id: cartItemId,
      productId: phone.id,
      variantId: phone.variants?.find(v => v.color === selectedColor && v.storage === selectedStorage)?.id || null,
      name: phone.name,
      image: imageURL,
      price: finalPrice,
      quantity,
      color: selectedColor,
      storage: selectedStorage,
      brand: brand,
    };

    // Validate the phone details against our schema
    try {
      CartItemSchema.parse(phoneDetails);
      addToCart(phoneDetails);
      router.push('/checkout');
    } catch (err) {
      console.error('Invalid phone details:', err);
    }
  };

  // Show loading or error state
  if (loading || error || !phone) {
    return (
      <Layout>
        <StatusMessage 
          isLoading={loading} 
          error={error || (!phone && !loading && "Phone not found")} 
          onBack={() => router.back()} 
          errorTitle="Error loading phone"
        />
      </Layout>
    );
  }

  // Extract unique colors and storage options for the variant selector
  const uniqueColors = phone.variants 
    ? [...new Set(phone.variants.map(variant => variant.color))]
    : [];
    
  const storageOptions = phone.variants && selectedColor
    ? [...new Set(phone.variants
        .filter(variant => variant.color === selectedColor)
        .map(variant => variant.storage))]
    : [];

  return (
    <Layout>
      <div className="ProductLayout">
        <div className="ProductContainer">
          <div className="ProductImage">
            <img 
              src={imageURL} 
              alt={phone.name} 
              onError={(e) => {
                console.error("Image failed to load:", e.target.src);
                e.target.src = '/placeholder-phone.jpg';
              }}
            />
          </div>
          <div className="ProductInfo">
            <h2 className="ProductTitle">{phone.name}</h2>
            <div className="ProductPrice">
              <h3>${finalPrice.toFixed(2)}</h3>
            </div>
            
            {/* Use our reusable variant selector component */}
            <ProductVariantSelector
              colors={uniqueColors}
              storageOptions={storageOptions}
              selectedColor={selectedColor}
              selectedStorage={selectedStorage}
              quantity={quantity}
              maxQuantity={maxQuantity}
              stockStatus={stockStatus}
              onColorChange={handleColorChange}
              onStorageChange={handleStorageChange}
              onIncrement={incrementQuantity}
              onDecrement={decrementQuantity}
            />
            
            <div className="cartButton">
              <button 
                onClick={handleAddToCart}
                disabled={!maxQuantity || maxQuantity === 0}
              >
                Add To Cart
              </button>
            </div>
            
            <div className="cartButton">
              {/* Use our reusable BuyNow component */}
              <BuyNowButton
                productId={phone.id}
                variantId={phone.variants?.find(v => v.color === selectedColor && v.storage === selectedStorage)?.id}
                price={finalPrice}
                quantity={quantity}
                image={imageURL}
                disabled={!maxQuantity || maxQuantity === 0}
              />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
