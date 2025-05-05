"use client";
import { useRouter } from 'next/navigation';

export default function BrandPageClient({ phones, brand, currentPage }) {
  const router = useRouter();

  const handleProductClick = (phoneId) => {
    router.push(`/products/${brand}/${phoneId}`);
  };

  const handlePrevious = () => {
    router.push(`/products/${brand}?page=${currentPage - 1}`);
  };

  const handleNext = () => {
    router.push(`/products/${brand}?page=${currentPage + 1}`);
  };

  return (
    <>
      <div className="PhoneWrapper">
        <div className="PhoneLayout">
          {phones.map((phone) => (
            <div className="PhoneCard" key={phone.id || phone.name}>
              <h4>{phone.name}</h4>
              <div 
                className="PhoneImage" 
                onClick={() => handleProductClick(phone.id)}
                style={{ cursor: 'pointer' }}
              >
                <img src={phone.image} alt={phone.name} width={150} height={200} />
              </div>
              <div className="PhonePrice">
                <h4>on sale for ${phone.price}</h4>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div>
        <div className="pageButton">
          {currentPage > 1 && (
            <button onClick={handlePrevious}>Previous</button>
          )}
          <button onClick={handleNext}>Next</button>
        </div>
      </div>
    </>
  );
}
