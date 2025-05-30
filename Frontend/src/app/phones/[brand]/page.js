"use client";
import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Layout from "../../../components/Layout";
import ProductCard from "../../../components/ProductCard";
import Pagination from "../../../components/Pagination";
import { usePhonesByBrand } from "../../../hooks/usePhoneData";
import '../../globals.css';

export default function BrandPage() {
  const router = useRouter();
  const { brand } = useParams();
  const [currentPage, setCurrentPage] = useState(1);
  
  // Get page from URL on initial load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const pageParam = urlParams.get('page');
    if (pageParam) {
      setCurrentPage(parseInt(pageParam) || 1);
    }
  }, []);
  
  // Use our custom hook to fetch phones by brand
  const { products: phones, loading, error } = usePhonesByBrand(brand, currentPage);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    router.push(`/phones/${brand}?page=${newPage}`);
  };

  return (
    <Layout>
      <div className="PhoneTitle">
        <h2>{brand ? brand.toUpperCase() : ''}</h2>
        
        {loading ? (
          <div className="loading">Loading...</div>
        ) : error ? (
          <div className="error">
            <p>Error loading phones: {error}</p>
          </div>
        ) : (
          <>
            <div className="PhoneWrapper">
              <div className="PhoneLayout">
                {phones.map((phone) => (
                  <ProductCard 
                    key={phone.id || phone.name}
                    product={phone}
                    brand={brand}
                  />
                ))}
              </div>
            </div>
            
            <Pagination 
              currentPage={currentPage}
              onPageChange={handlePageChange}
              hasPreviousPage={currentPage > 1}
            />
          </>
        )}
      </div>
    </Layout>
  );
}
