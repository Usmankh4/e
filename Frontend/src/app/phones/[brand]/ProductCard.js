"use client";
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function ProductCard({ phone, brand }) {
  const router = useRouter();

  const handleClick = () => {
    // Use phone.slug if available, otherwise fall back to phone.id
    const productIdentifier = phone.slug || phone.id;
    router.push(`/phones/${brand}/${productIdentifier}`);
  };

  return (
    <div className="PhoneCard" key={phone.name}>
      <h4>{phone.name}</h4>
      <div className="PhoneImage" onClick={handleClick} style={{ cursor: 'pointer' }}>
        <img 
          src={phone.image_url || phone.base_image || '/placeholder-phone.jpg'} 
          alt={phone.name} 
          width={150} 
          height={200} 
          onError={(e) => {
            console.log("Image failed to load:", e.target.src);
            e.target.src = '/placeholder-phone.jpg';
          }}
        />
      </div>
      <div className="PhonePrice">
        <h4>on sale for ${phone.price || phone.base_price}</h4>
      </div>
    </div>
  );
}
