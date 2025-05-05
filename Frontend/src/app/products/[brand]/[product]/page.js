"use client";
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { z } from 'zod';
import { loadStripe } from '@stripe/stripe-js';
import Footer from "../../../../components/footer";
import Header from "../../../../components/header";

// Debug the environment variable
console.log("Stripe Key in product page:", process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);

// Initialize Stripe with the publishable key from environment variables
// Only initialize if the key is available
const stripePromise = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY 
  ? loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
  : null;

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

export default function ProductPage() {
  const router = useRouter();
  const { product } = useParams();
  const [phone, setPhone] = useState(null);
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedStorage, setSelectedStorage] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [finalPrice, setFinalPrice] = useState(0);
  const [imageURL, setImageURL] = useState('');
  const [availableStock, setAvailableStock] = useState(null);
  const [maxQuantity, setMaxQuantity] = useState(null); // Default max quantity
  const [stockStatus, setStockStatus] = useState('plenty'); // 'plenty', 'low', or 'very-low'

  useEffect(() => {
    const fetchPhone = async () => {
      try {
        // Log the product parameter to see what we're getting
        console.log("Product parameter:", product);
        
        // Check if product is a number (ID) or string (slug)
        const isNumeric = /^\d+$/.test(product);
        
        let apiUrl;
        if (isNumeric) {
          // If it's a numeric ID, use the regular endpoint
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/${product}/`;
        } else {
          // If it's a slug, use the by-slug endpoint
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/by-slug/${product}/`;
        }
        
        console.log("Using API URL:", apiUrl);
        
        const response = await fetch(apiUrl, {
          cache: 'no-store'
        });
        
        console.log("API response status:", response.status);
        
        if (!response.ok) {
          console.error("Error response:", await response.text());
          throw new Error(`Failed to fetch product details: ${response.status}`);
        }
        
        const phoneData = await response.json();
        console.log("Product data:", phoneData); // Debug log
        setPhone(phoneData);
        
        // Extract color options from variants
        if (phoneData.variants && phoneData.variants.length > 0) {
          // Get unique colors from variants
          const uniqueColors = [...new Set(phoneData.variants.map(variant => variant.color))];
          
          // Set default color
          const defaultColor = uniqueColors[0];
          setSelectedColor(defaultColor);
          
          // Find variant with the selected color
          const defaultVariant = phoneData.variants.find(variant => variant.color === defaultColor);
          
          // Set image URL from the color variant or fall back to base image
          const variantImage = defaultVariant.image_url || defaultVariant.color_image;
          const rawImageUrl = variantImage || phoneData.image_url || phoneData.base_image;
          
          // Fix the image URL by adding the backend base URL if needed
          let processedImageUrl = rawImageUrl;
          if (rawImageUrl) {
            if (rawImageUrl.startsWith('/media')) {
              processedImageUrl = `http://localhost:8000${rawImageUrl}`;
            } else if (!rawImageUrl.startsWith('http')) {
              processedImageUrl = `http://localhost:8000/media/${rawImageUrl}`;
            }
          } else {
            processedImageUrl = '/placeholder-phone.jpg';
          }
          
          setImageURL(processedImageUrl);
          console.log("Setting image URL:", processedImageUrl);
          
          // Get unique storage options for the selected color
          const storageOptions = phoneData.variants
            .filter(variant => variant.color === defaultColor)
            .map(variant => variant.storage);
          
          if (storageOptions.length > 0) {
            // Set default storage
            const defaultStorage = storageOptions[0];
            setSelectedStorage(defaultStorage);
            
            // Find the price for the selected color and storage
            const selectedVariant = phoneData.variants.find(
              variant => variant.color === defaultColor && variant.storage === defaultStorage
            );
            
            setFinalPrice(parseFloat(selectedVariant.price));
            setAvailableStock(selectedVariant.available_stock);
            // Get max purchase quantity from variant or use default
            const maxPurchaseLimit = selectedVariant.max_purchase_quantity || 10;
            // Only disable the increment button when stock is actually 0
            setMaxQuantity(selectedVariant.available_stock > 0 ? Math.max(1, Math.min(maxPurchaseLimit, selectedVariant.available_stock)) : 0);
            setStockStatus(selectedVariant.stock_status);
          } else {
            setSelectedStorage('Default');
            setFinalPrice(parseFloat(phoneData.base_price));
          }
        } else {
          // No variants available
          setSelectedColor('Default');
          setSelectedStorage('Default');
          setImageURL(phoneData.base_image);
          setFinalPrice(parseFloat(phoneData.base_price));
        }
      } catch (error) {
        console.error('Error fetching product details:', error);
      }
    };
    
    fetchPhone();
  }, [product]);

  const handleColorChange = (event) => {
    const newColorName = event.target.value;
    setSelectedColor(newColorName);

    if (phone.variants && phone.variants.length > 0) {
      const colorVariant = phone.variants.find(variant => variant.color === newColorName);
      const newImageURL = colorVariant.image_url || colorVariant.color_image || phone.base_image;
      
      // Fix the image URL by adding the backend base URL if needed
      let processedImageUrl = newImageURL;
      if (newImageURL) {
        if (newImageURL.startsWith('/media')) {
          processedImageUrl = `http://localhost:8000${newImageURL}`;
        } else if (!newImageURL.startsWith('http')) {
          processedImageUrl = `http://localhost:8000/media/${newImageURL}`;
        }
      } else {
        processedImageUrl = '/placeholder-phone.jpg';
      }
      
      setImageURL(processedImageUrl);
      
      // Get unique storage options for the selected color
      const storageOptions = phone.variants
        .filter(variant => variant.color === newColorName)
        .map(variant => variant.storage);
      
      if (storageOptions.length > 0) {
        // Set default storage
        const defaultStorage = storageOptions[0];
        setSelectedStorage(defaultStorage);
        
        // Find the price for the selected color and storage
        const selectedVariant = phone.variants.find(
          variant => variant.color === newColorName && variant.storage === defaultStorage
        );
        
        setFinalPrice(parseFloat(selectedVariant.price));
        setAvailableStock(selectedVariant.available_stock);
        // Get max purchase quantity from variant or use default
        const maxPurchaseLimit = selectedVariant.max_purchase_quantity || 10;
        // Only disable the increment button when stock is actually 0
        setMaxQuantity(selectedVariant.available_stock > 0 ? Math.max(1, Math.min(maxPurchaseLimit, selectedVariant.available_stock)) : 0);
        setStockStatus(selectedVariant.stock_status);
      } else {
        setSelectedStorage('Default');
        setFinalPrice(parseFloat(phone.base_price));
      }
    }
  };

  const handleStorageChange = (event) => {
    const newStorage = event.target.value;
    const selectedVariant = phone.variants.find(
      variant => variant.color === selectedColor && variant.storage === newStorage
    );
    setSelectedStorage(newStorage);
    setFinalPrice(parseFloat(selectedVariant.price));
    
    // Update stock information based on selected variant
    if (selectedVariant) {
      // Calculate available stock from variant data
      const stock = selectedVariant.count_in_stock - (selectedVariant.reserved_stock || 0);
      setAvailableStock(stock);
      
      // Get max purchase quantity from variant or use default
      const maxPurchaseLimit = selectedVariant.max_purchase_quantity || 10;
      // Only disable the increment button when stock is actually 0
      setMaxQuantity(stock > 0 ? Math.max(1, Math.min(maxPurchaseLimit, stock)) : 0);
      
      // Set stock status for UI indicators
      if (stock <= 3) {
        setStockStatus('very-low');
      } else if (stock <= 10) {
        setStockStatus('low');
      } else {
        setStockStatus('plenty');
      }
      
      // Adjust quantity if current selection exceeds new maximum
      if (quantity > Math.min(maxPurchaseLimit, stock)) {
        setQuantity(Math.min(maxPurchaseLimit, stock));
      }
    }
  };

  const incrementQuantity = () => {
    if (quantity < maxQuantity) {
      setQuantity(prevQuantity => prevQuantity + 1);
    }
  };

  const decrementQuantity = () => {
    setQuantity(prevQuantity => prevQuantity > 1 ? prevQuantity - 1 : 1);
  };

  const handleAddToCart = () => {
    // Find the selected variant based on color and storage
    const selectedVariant = phone.variants.find(
      variant => variant.color === selectedColor && variant.storage === selectedStorage
    );
    
    console.log("Selected variant for cart:", selectedVariant);
    
    if (!selectedVariant && phone.variants && phone.variants.length > 0) {
      console.error('Selected variant not found');
      return;
    }
    
    // Get the image URL and price from the selected variant or fallback to the phone
    const imageURL = selectedVariant && selectedVariant.image_url ? selectedVariant.image_url : phone.image_url;
    const finalPrice = selectedVariant && selectedVariant.price ? selectedVariant.price : phone.price;
    
    // Process the image URL for the cart
    let processedImageUrl = imageURL || phone.base_image;
    if (processedImageUrl) {
      if (processedImageUrl.startsWith('/media')) {
        processedImageUrl = `http://localhost:8000${processedImageUrl}`;
      } else if (!processedImageUrl.startsWith('http')) {
        processedImageUrl = `http://localhost:8000/media/${processedImageUrl}`;
      }
    } else {
      processedImageUrl = '/placeholder-phone.jpg';
    }
    
    const productDetails = {
      id: Math.random().toString(36).substr(2, 9), // Generate a unique cart item ID
      productId: phone.id,
      slug: phone.slug, // Add the product slug to the cart item
      variantId: selectedVariant ? selectedVariant.id : null, // Add the variant ID
      name: phone.name,
      image: processedImageUrl,
      price: finalPrice,
      quantity,
      color: selectedColor || 'Default',
      storage: selectedStorage || 'Default',
      brand: phone.brand,
      // Add a flag to identify if this is an accessory
      isAccessory: phone.category === 'Accessories' || !phone.variants || phone.variants.length === 0
    };

    console.log("Adding to cart with details:", productDetails);
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
      console.log("Starting Buy Now process...");
      console.log("Phone data:", phone);
      console.log("Selected color:", selectedColor);
      console.log("Selected storage:", selectedStorage);
      
      // Find the selected variant based on color and storage
      const selectedVariant = phone.variants.find(
        variant => variant.color === selectedColor && variant.storage === selectedStorage
      );
      
      console.log("Found variant:", selectedVariant);
      
      if (!selectedVariant) {
        console.error('Selected variant not found');
        return;
      }
      
      const requestData = {
        variant_id: selectedVariant.id,
        quantity: quantity,
        success_url: window.location.origin + '/checkout/success',
        cancel_url: window.location.origin + '/checkout/cancel'
      };
      
      console.log("Sending request with data:", requestData);
      
      const response = await fetch('http://127.0.0.1:8000/myapp/api/create-buy-now-session/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      
      console.log("Response status:", response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`Failed to create checkout session: ${errorText}`);
      }
      
      const responseData = await response.json();
      console.log("Response data:", responseData);
      
      // Check if we have a direct URL to redirect to
      if (responseData.url) {
        console.log("Redirecting directly to Stripe URL:", responseData.url);
        window.location.href = responseData.url;
        return;
      }
      
      // Fall back to the old method if no direct URL is provided
      const sessionId = responseData.id;
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

  if (!phone) {
    return (
      <div>
        <Header />
        <div className="pageAfterHeader">
          <div>Loading...</div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="ProductLayout">
        <div className="ProductContainer">
          <div className="ProductImage">
            <img 
              src={imageURL} 
              alt={phone?.name} 
              onError={(e) => {
                console.error("Image failed to load:", e.target.src);
                // Try to fix relative URLs by adding the backend base URL
                if (e.target.src && !e.target.src.startsWith('http')) {
                  const fixedUrl = `http://127.0.0.1:8001${e.target.src}`;
                  console.log("Trying with fixed URL:", fixedUrl);
                  e.target.src = fixedUrl;
                } else {
                  // If that fails too, use a placeholder
                  e.target.src = '/placeholder-phone.jpg';
                }
              }}
            />
          </div>
          <div className="ProductInfo">
            <h2 className="ProductTitle">{phone.name}</h2>
            <div className="ProductPrice">
              <h3>${finalPrice.toFixed(2)}</h3>
            </div>
            <div className="SelectionsContainer">
              <div className="ColourAndStorage">
                {/* Only show color selection if colors are available */}
                {phone.variants && phone.variants.length > 0 && (
                  <div className="ColourSelection">
                    <select value={selectedColor} onChange={handleColorChange}>
                      {[...new Set(phone.variants.map(variant => variant.color))].map((color) => (
                        <option key={color} value={color}>{color}</option>
                      ))}
                    </select>
                  </div>
                )}
                
                {/* Only show storage selection if storage options are available */}
                {phone.variants && phone.variants.length > 0 && (
                  <div className="StorageSelection">
                    <select value={selectedStorage} onChange={handleStorageChange}>
                      {phone.variants
                        .filter(variant => variant.color === selectedColor)
                        .map(variant => variant.storage)
                        .map((storage) => (
                          <option key={storage} value={storage}>{storage}</option>
                        ))}
                    </select>
                  </div>
                )}
                
                <div className="QuantitySelection">
                  <button onClick={decrementQuantity} disabled={quantity <= 1}>-</button>
                  <span>{quantity}</span>
                  <button onClick={incrementQuantity} disabled={quantity >= maxQuantity}>+</button>
                </div>
                
                {/* Stock status indicators */}
                {availableStock !== null && (
                  <div className={`stock-status ${stockStatus}`}>
                    {availableStock > 10 ? (
                      <span>In Stock</span>
                    ) : availableStock > 0 ? (
                      <span>Only {availableStock} left in stock</span>
                    ) : (
                      <span>Out of Stock</span>
                    )}
                  </div>
                )}
                
                {/* Purchase limit indicator */}
                {maxQuantity < 10 && (
                  <div className="purchase-limit">
                    Limit {maxQuantity} per order
                  </div>
                )}
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
      </div>
      <Footer />
    </div>
  );
}
