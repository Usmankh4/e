"use client";
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { loadStripe } from '@stripe/stripe-js';

// Debug the environment variable
console.log("Stripe Key in ProductClient:", process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

// Initialize Stripe with the publishable key from environment variables
// Only initialize if the key is available
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

export default function ProductClient({ phone }) {
  const router = useRouter();
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedStorage, setSelectedStorage] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [finalPrice, setFinalPrice] = useState(0);
  const [imageURL, setImageURL] = useState('');

  useEffect(() => {
    // Set default values when component mounts
    if (phone.colors && phone.colors.length > 0) {
      const defaultColor = phone.colors[0].name;
      setSelectedColor(defaultColor);
      
      const defaultImage = phone.color_images.find(image => image.color_name === defaultColor);
      setImageURL(defaultImage ? defaultImage.image : phone.image);
    } else {
      setImageURL(phone.image);
    }

    if (phone.storage_options && phone.storage_options.length > 0) {
      const defaultStorage = phone.storage_options[0].storage_amount;
      setSelectedStorage(defaultStorage);
      setFinalPrice(parseFloat(phone.storage_options[0].price));
    } else {
      setFinalPrice(parseFloat(phone.price));
    }
  }, [phone]);

  const handleColorChange = (event) => {
    const newColorName = event.target.value;
    setSelectedColor(newColorName);

    const colorImageEntry = phone.color_images.find(imageEntry => imageEntry.color_name === newColorName);
    const newImageURL = colorImageEntry ? colorImageEntry.image : phone.image;
    setImageURL(newImageURL);
  };

  const handleStorageChange = (event) => {
    const newStorage = event.target.value;
    const storageOption = phone.storage_options.find(option => option.storage_amount === newStorage);
    setSelectedStorage(newStorage);
    setFinalPrice(parseFloat(storageOption.price));
  };

  const incrementQuantity = () => {
    setQuantity(prevQuantity => prevQuantity + 1);
  };

  const decrementQuantity = () => {
    setQuantity(prevQuantity => prevQuantity > 1 ? prevQuantity - 1 : 1);
  };

  const handleAddToCart = () => {
    const cartItemId = `${phone.id}_${selectedColor}_${selectedStorage}`;
    const productDetails = {
      id: cartItemId,
      productId: phone.id,
      name: phone.name,
      image: imageURL,
      price: finalPrice,
      quantity,
      color: selectedColor,
      storage: selectedStorage,
      brand: phone.brand,
    };

    addToCart(productDetails);
  };

  const addToCart = (productDetails) => {
    let cart = [];
    if (typeof window !== 'undefined') {
      const cartJson = localStorage.getItem('cart');
      cart = cartJson ? JSON.parse(cartJson) : [];
    }
    
    const existingIndex = cart.findIndex(item => 
      item.productId === productDetails.productId && 
      item.color === productDetails.color && 
      item.storage === productDetails.storage
    );
    
    if (existingIndex !== -1) {
      cart[existingIndex].quantity += productDetails.quantity;
    } else {
      cart.push({
        ...productDetails,
        brand: phone.brand,
      });
    }
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('cart', JSON.stringify(cart));
    }
    
    router.push('/checkout');
  };

  const handleBuyNow = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/create-checkout-session/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          productId: phone.id,
          price: finalPrice,
          quantity: quantity,
          image: imageURL
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }
      
      const { sessionId } = await response.json();
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({ sessionId });
      
      if (error) {
        console.error('Error redirecting to Stripe checkout:', error);
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    }
  };

  if (!phone) return null;

  return (
    <div className="ProductContainer">
      <div className="ProductImage">
        <img src={imageURL} alt={phone.name} />
      </div>
      <div className="ProductInfo">
        <h2 className="ProductTitle">{phone.name}</h2>
        <div className="ProductPrice">
          <h3>${finalPrice.toFixed(2)}</h3>
        </div>
        <div className="SelectionsContainer">
          <div className="ColourAndStorage">
            <div className="ColourSelection">
              <select value={selectedColor} onChange={handleColorChange}>
                {phone.colors.map((color) => (
                  <option key={color.id} value={color.name}>{color.name}</option>
                ))}
              </select>
            </div>
            <div className="StorageSelection">
              <select value={selectedStorage} onChange={handleStorageChange}>
                {phone.storage_options.map((option) => (
                  <option key={option.id} value={option.storage_amount}>
                    {option.storage_amount}
                  </option>
                ))}
              </select>
            </div>
            <div className="QuantitySelection">
              <button onClick={decrementQuantity}>-</button>
              <span>{quantity}</span>
              <button onClick={incrementQuantity}>+</button>
            </div>
          </div>
          <div className="cartButton">
            <button onClick={handleAddToCart}>Add To Cart</button>
          </div>
          <div className="cartButton">
            <button onClick={handleBuyNow}>Buy Now</button>
          </div>
        </div>
      </div>
    </div>
  );
}
