"use client";

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { addToCart } from "../utils/cartUtils";
import BuyNowButton from "./BuyNowButton";

export default function AccessoryActions({ accessory }) {
  const router = useRouter();
  const [quantity] = useState(1); // Default quantity
  
  const handleAddToCart = () => {
    if (!accessory) return;
    
    // Create a unique ID for the cart item
    const cartItemId = `${accessory.id}`;
    
    // Prepare accessory details for cart
    const accessoryDetails = {
      id: cartItemId,
      productId: accessory.id,
      variantId: null, // Accessories don't have variants
      name: accessory.name,
      image: accessory.image,
      price: parseFloat(accessory.price),
      quantity,
      brand: accessory.brand,
    };

    addToCart(accessoryDetails);
    router.push('/checkout');
  };
  
  return (
    <>
      <div className="cartButton">
        <button onClick={handleAddToCart}>Add To Cart</button>
      </div>
      
      <div className="cartButton">
        <BuyNowButton
          productId={accessory.id}
          variantId={null}
          price={parseFloat(accessory.price)}
          quantity={quantity}
          image={accessory.image}
        />
      </div>
    </>
  );
}
