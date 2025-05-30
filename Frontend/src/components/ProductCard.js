import { useRouter } from 'next/navigation';
import { processImageUrl } from '../utils/imageUtils';

/**
 * Reusable product card component
 * Maintains original CSS classes and styling
 * Note: This component now navigates to /phones/ routes instead of /products/
 * @param {Object} props - Component props
 * @param {Object} props.product - Product data (or phone data)
 * @param {string} props.brand - Brand name
 * @param {Function} props.onClick - Optional click handler
 */
export default function ProductCard({ product, brand, onClick }) {
  const router = useRouter();

  const handleClick = () => {
    if (onClick) {
      onClick(product);
      return;
    }
    
    // Use product.slug if available, otherwise fall back to product.id
    const productIdentifier = product.slug || product.id;
    router.push(`/phones/${brand}/${productIdentifier}`);
  };

  // Get the appropriate price
  const displayPrice = product.price || product.base_price;
  
  // Process the image URL
  const imageUrl = processImageUrl(product.image_url || product.base_image);

  return (
    <div className="PhoneCard" key={product.id || product.name}>
      <h4>{product.name}</h4>
      <div className="PhoneImage" onClick={handleClick} style={{ cursor: 'pointer' }}>
        <img 
          src={imageUrl} 
          alt={product.name} 
          width={150} 
          height={200} 
          onError={(e) => {
            console.log("Image failed to load:", e.target.src);
            e.target.src = '/placeholder-phone.jpg';
          }}
        />
      </div>
      <div className="PhonePrice">
        <h4>on sale for ${displayPrice}</h4>
      </div>
    </div>
  );
}
