"use client";
import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import Footer from "../../../components/footer";
import Header from "../../../components//header";
import '../../globals.css';

export default function BrandPage() {
  const router = useRouter();
  const { brand } = useParams();
  const [phones, setPhones] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  
  useEffect(() => {
    const fetchPhones = async () => {
      try {
        // Get page from URL query if it exists
        const urlParams = new URLSearchParams(window.location.search);
        const pageParam = urlParams.get('page');
        const page = pageParam ? parseInt(pageParam) : 1;
        setCurrentPage(page);
        
        // Add debug log to see what we're fetching
        console.log(`Fetching phones for brand: ${brand}, page: ${page}`);
        
        const response = await fetch(`http://127.0.0.1:8000/myapp/api/products/?brand=${brand}&page=${page}`, { 
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch phones');
        }
        
        const data = await response.json();
        console.log("API response data:", data);
        setPhones(data.results || []);
      } catch (error) {
        console.error('Error fetching phones:', error);
        setPhones([]);
      }
    };
    
    fetchPhones();
  }, [brand]);

  const handleProductClick = (phone) => {
    // Use slug if available, otherwise fall back to ID
    const productIdentifier = phone.slug || phone.id;
    console.log("Navigating to product with identifier:", productIdentifier);
    router.push(`/products/${brand}/${productIdentifier}`);
  };

  const handlePrevious = () => {
    const newPage = currentPage - 1;
    setCurrentPage(newPage);
    router.push(`/products/${brand}?page=${newPage}`);
  };

  const handleNext = () => {
    const newPage = currentPage + 1;
    setCurrentPage(newPage);
    router.push(`/products/${brand}?page=${newPage}`);
  };

  return (
    <div>
      <div className="PhoneBackground">
        <Header />
        <div className="pageAfterHeader">
          <div className="PhoneTitle">
            <h2>{brand ? brand.toUpperCase() : ''}</h2>
            <div className="PhoneWrapper">
              <div className="PhoneLayout">
                {phones.map((phone) => (
                  <div className="PhoneCard" key={phone.id || phone.name}>
                    <h4>{phone.name}</h4>
                    <div 
                      className="PhoneImage" 
                      onClick={() => handleProductClick(phone)}
                      style={{ cursor: 'pointer' }}
                    >
                      <img 
                        src={(() => {
                          const rawImageUrl = phone.image_url || phone.base_image;
                          if (!rawImageUrl) return '/placeholder-phone.jpg';
                          if (rawImageUrl.startsWith('http')) return rawImageUrl;
                          if (rawImageUrl.startsWith('/media')) return `http://localhost:8000${rawImageUrl}`;
                          return `http://localhost:8000/media/${rawImageUrl}`;
                        })()} 
                        alt={phone.name} 
                        width={150} 
                        height={200} 
                        onError={(e) => {
                          console.error("Image failed to load:", e.target.src);
                          e.target.src = '/placeholder-phone.jpg';
                        }}
                      />
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
          </div>
        </div>
        <Footer />
      </div>
    </div>
  );
}
