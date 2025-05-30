"use client";

import { useRouter } from 'next/navigation';
import { processImageUrl } from '../utils/imageUtils';

/**
 * Reusable accessory card component
 * Exactly matches the structure of ProductCard component
 * @param {Object} props - Component props
 * @param {Object} props.accessory - Accessory data
 * @param {Function} props.onClick - Optional click handler
 */
export default function AccessoryCard({ accessory, onClick }) {
  const router = useRouter();

  const handleClick = () => {
    if (onClick) {
      onClick(accessory);
      return;
    }
    
    // Navigate to the accessory detail page
    router.push(`/accessories/${accessory.slug}`);
  };

  // Process the image URL
  const imageUrl = processImageUrl(accessory.image);

  return (
    <div className="PhoneCard" key={accessory.id}>
      <h4>{accessory.name}</h4>
      <div className="PhoneImage" onClick={handleClick} style={{ cursor: 'pointer' }}>
        <img 
          src={imageUrl} 
          alt={accessory.name} 
          width={150} 
          height={200} 
          onError={(e) => {
            console.log("Image failed to load:", e.target.src);
            e.target.src = '/placeholder-accessory.jpg';
          }}
        />
      </div>
      <div className="PhonePrice">
        <h4>on sale for ${accessory.price}</h4>
      </div>
    </div>
  );
}
