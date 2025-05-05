"use client";
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AddToCartButton({ product, defaultColor, defaultStorage, defaultPrice, defaultImage }) {
  const [selectedColor, setSelectedColor] = useState(defaultColor);
  const [selectedStorage, setSelectedStorage] = useState(defaultStorage);
  const [quantity, setQuantity] = useState(1);
  const router = useRouter();

  // Listen for changes in color selection
  useState(() => {
    const colorSelector = document.querySelector('.ColourSelection select');
    if (colorSelector) {
      colorSelector.addEventListener('change', (e) => {
        setSelectedColor(e.target.value);
      });
    }
    
    return () => {
      if (colorSelector) {
        colorSelector.removeEventListener('change', (e) => {
          setSelectedColor(e.target.value);
        });
      }
    };
  }, []);

  // Listen for changes in storage selection
  useState(() => {
    const storageSelector = document.querySelector('.StorageSelection select');
    if (storageSelector) {
      storageSelector.addEventListener('change', (e) => {
        setSelectedStorage(e.target.value);
      });
    }
    
    return () => {
      if (storageSelector) {
        storageSelector.removeEventListener('change', (e) => {
          setSelectedStorage(e.target.value);
        });
      }
    };
  }, []);

  // Listen for changes in quantity
  useState(() => {
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

  const getCartFromStorage = () => {
    if (typeof window !== 'undefined') {
      const cart = localStorage.getItem('cart');
      return cart ? JSON.parse(cart) : [];
    }
    return [];
  };

  const saveCartToStorage = (cart) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('cart', JSON.stringify(cart));
    }
  };

  const handleAddToCart = () => {
    // Get current image from the product image element
    const productImageElement = document.querySelector('.ProductImage img');
    const currentImage = productImageElement ? productImageElement.src : defaultImage;
    
    // Get current price from the price element
    const priceElement = document.querySelector('.ProductPrice h3');
    const priceText = priceElement ? priceElement.textContent.replace('$', '') : defaultPrice.toString();
    const currentPrice = parseFloat(priceText);

    const cartItemId = `${product.id}_${selectedColor}_${selectedStorage}`;
    const productDetails = {
      id: cartItemId,
      productId: product.id,
      name: product.name,
      image: currentImage,
      price: isNaN(currentPrice) ? defaultPrice : currentPrice,
      quantity,
      color: selectedColor,
      storage: selectedStorage,
      brand: product.brand,
    };

    addToCart(productDetails);
  };

  const addToCart = (productDetails) => {
    let cart = getCartFromStorage();
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
        brand: product.brand,
      });
    }
    
    saveCartToStorage(cart);
    router.push('/checkout');
  };

  return (
    <button onClick={handleAddToCart}>Add To Cart</button>
  );
}
