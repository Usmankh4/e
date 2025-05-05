"use client";
import { useState } from 'react';

export default function ProductStorageSelector({ variants, selectedColor, defaultStorage }) {
  const [selectedStorage, setSelectedStorage] = useState(defaultStorage);
  const [finalPrice, setFinalPrice] = useState(() => {
    const storageVariant = variants.find(
      variant => variant.color === selectedColor && variant.storage === defaultStorage
    );
    return storageVariant ? parseFloat(storageVariant.price) : 0;
  });

  const handleStorageChange = (event) => {
    const newStorage = event.target.value;
    const storageVariant = variants.find(
      variant => variant.color === selectedColor && variant.storage === newStorage
    );
    setSelectedStorage(newStorage);
    
    if (storageVariant) {
      setFinalPrice(parseFloat(storageVariant.price));
      
      // Update the displayed price
      const priceElement = document.querySelector('.ProductPrice h3');
      if (priceElement) {
        priceElement.textContent = `$${parseFloat(storageVariant.price).toFixed(2)}`;
      }
    }
  };

  // Get unique storage options for the selected color
  const storageOptions = variants
    .filter(variant => variant.color === selectedColor)
    .map(variant => variant.storage);

  return (
    <select value={selectedStorage} onChange={handleStorageChange}>
      {storageOptions.map((storage) => (
        <option key={storage} value={storage}>
          {storage}
        </option>
      ))}
    </select>
  );
}
