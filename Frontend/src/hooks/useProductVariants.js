import { useState, useEffect } from 'react';
import { processImageUrl } from '../utils/imageUtils';

/**
 * Custom hook for managing product variant selections
 * @param {Object} product - The product data
 * @returns {Object} - State and handlers for product variants
 */
export function useProductVariants(product) {
  const [selectedColor, setSelectedColor] = useState('');
  const [selectedStorage, setSelectedStorage] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [finalPrice, setFinalPrice] = useState(0);
  const [imageURL, setImageURL] = useState('');
  const [availableStock, setAvailableStock] = useState(null);
  const [maxQuantity, setMaxQuantity] = useState(null);
  const [stockStatus, setStockStatus] = useState('plenty');

  // Initialize default selections when product data changes
  useEffect(() => {
    if (!product) return;

    // Set default color if variants exist
    if (product.variants && product.variants.length > 0) {
      const uniqueColors = [...new Set(product.variants.map(variant => variant.color))];
      const defaultColor = uniqueColors[0];
      setSelectedColor(defaultColor);
      
      // Find variant with the selected color
      const defaultVariant = product.variants.find(variant => variant.color === defaultColor);
      
      // Set image URL from the color variant or fall back to base image
      const variantImage = defaultVariant.image_url || defaultVariant.color_image;
      const rawImageUrl = variantImage || product.image_url || product.base_image;
      setImageURL(processImageUrl(rawImageUrl));
      
      // Get unique storage options for the selected color
      const storageOptions = product.variants
        .filter(variant => variant.color === defaultColor)
        .map(variant => variant.storage);
      
      if (storageOptions.length > 0) {
        // Set default storage
        const defaultStorage = storageOptions[0];
        setSelectedStorage(defaultStorage);
        
        // Find the price for the selected color and storage
        const selectedVariant = product.variants.find(
          variant => variant.color === defaultColor && variant.storage === defaultStorage
        );
        
        setFinalPrice(parseFloat(selectedVariant.price));
        
        // Calculate true available stock (total - reserved)
        const totalStock = selectedVariant.count_in_stock || 0;
        const reservedStock = selectedVariant.reserved_stock || 0;
        const trueAvailability = Math.max(0, totalStock - reservedStock);
        
        setAvailableStock(trueAvailability);
        setMaxQuantity(trueAvailability);
        
        // Determine stock status
        if (trueAvailability === 0 && reservedStock > 0) {
          setStockStatus('reserved');
        } else if (trueAvailability === 0) {
          setStockStatus('out');
        } else if (trueAvailability <= 5) {
          setStockStatus('low');
        } else {
          setStockStatus('plenty');
        }
      } else {
        setSelectedStorage('Default');
        setFinalPrice(parseFloat(product.base_price));
      }
    } else {
      // No variants available
      setSelectedColor('Default');
      setSelectedStorage('Default');
      setImageURL(processImageUrl(product.base_image));
      setFinalPrice(parseFloat(product.base_price));
    }
  }, [product]);

  // Handle color change
  const handleColorChange = (event) => {
    const newColorName = event.target.value;
    setSelectedColor(newColorName);

    if (product.variants && product.variants.length > 0) {
      const colorVariant = product.variants.find(variant => variant.color === newColorName);
      const newImageURL = colorVariant.image_url || colorVariant.color_image || product.base_image;
      setImageURL(processImageUrl(newImageURL));
      
      // Get unique storage options for the selected color
      const storageOptions = product.variants
        .filter(variant => variant.color === newColorName)
        .map(variant => variant.storage);
      
      if (storageOptions.length > 0) {
        // Set default storage
        const defaultStorage = storageOptions[0];
        setSelectedStorage(defaultStorage);
        
        // Find the price for the selected color and storage
        const selectedVariant = product.variants.find(
          variant => variant.color === newColorName && variant.storage === defaultStorage
        );
        
        setFinalPrice(parseFloat(selectedVariant.price));
        
        // Calculate true available stock (total - reserved)
        const totalStock = selectedVariant.count_in_stock || 0;
        const reservedStock = selectedVariant.reserved_stock || 0;
        const trueAvailability = Math.max(0, totalStock - reservedStock);
        
        setAvailableStock(trueAvailability);
        setMaxQuantity(trueAvailability);
        
        // Determine stock status
        if (trueAvailability === 0 && reservedStock > 0) {
          setStockStatus('reserved');
        } else if (trueAvailability === 0) {
          setStockStatus('out');
        } else if (trueAvailability <= 5) {
          setStockStatus('low');
        } else {
          setStockStatus('plenty');
        }
      } else {
        setSelectedStorage('Default');
        setFinalPrice(parseFloat(product.base_price));
      }
    }
  };

  // Handle storage change
  const handleStorageChange = (event) => {
    const newStorage = event.target.value;
    setSelectedStorage(newStorage);
    
    if (product.variants && product.variants.length > 0) {
      const selectedVariant = product.variants.find(
        variant => variant.color === selectedColor && variant.storage === newStorage
      );
      
      if (selectedVariant) {
        setFinalPrice(parseFloat(selectedVariant.price));
        
        // Calculate true available stock (total - reserved)
        const totalStock = selectedVariant.count_in_stock || 0;
        const reservedStock = selectedVariant.reserved_stock || 0;
        const trueAvailability = Math.max(0, totalStock - reservedStock);
        
        setAvailableStock(trueAvailability);
        setMaxQuantity(trueAvailability);
        
        // Determine stock status
        if (trueAvailability === 0 && reservedStock > 0) {
          setStockStatus('reserved');
        } else if (trueAvailability === 0) {
          setStockStatus('out');
        } else if (trueAvailability <= 5) {
          setStockStatus('low');
        } else {
          setStockStatus('plenty');
        }
      }
    }
  };

  // Quantity handlers
  const incrementQuantity = () => {
    setQuantity(prev => (prev >= maxQuantity) ? maxQuantity : prev + 1);
  };

  const decrementQuantity = () => {
    setQuantity(prev => prev > 1 ? prev - 1 : 1);
  };

  return {
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
    decrementQuantity,
    setQuantity
  };
}
