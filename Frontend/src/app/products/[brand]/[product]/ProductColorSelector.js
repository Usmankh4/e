"use client";
import { useState } from 'react';

export default function ProductColorSelector({ variants, defaultColor, productImage }) {
  const [selectedColor, setSelectedColor] = useState(defaultColor);
  const [imageURL, setImageURL] = useState(() => {
    const defaultVariant = variants.find(variant => variant.color === defaultColor);
    return defaultVariant?.color_image || productImage;
  });

  const handleColorChange = (event) => {
    const newColorName = event.target.value;
    setSelectedColor(newColorName);

    const colorVariant = variants.find(variant => variant.color === newColorName);
    const newImageURL = colorVariant?.color_image || productImage;
    setImageURL(newImageURL);
    
    // Update the main product image
    const productImageElement = document.querySelector('.ProductImage img');
    if (productImageElement) {
      productImageElement.src = newImageURL;
    }
  };

  // Get unique colors from variants
  const uniqueColors = [...new Set(variants.map(variant => variant.color))];

  return (
    <select value={selectedColor} onChange={handleColorChange}>
      {uniqueColors.map((color) => (
        <option key={color} value={color}>{color}</option>
      ))}
    </select>
  );
}
