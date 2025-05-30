"use client";

import { useState } from 'react';

export default function AccessoryImage({ src, alt }) {
  const [imgSrc, setImgSrc] = useState(src);
  
  const handleError = () => {
    console.error("Image failed to load:", src);
    setImgSrc('/placeholder-accessory.jpg');
  };
  
  return (
    <img 
      src={imgSrc} 
      alt={alt} 
      onError={handleError}
      className="accessory-image"
    />
  );
}
