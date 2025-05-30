import { useState, useEffect } from 'react';

export function useProductData(productId) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        // Check if product is a number (ID) or string (slug)
        const isNumeric = /^\d+$/.test(productId);
        
        let apiUrl;
        if (isNumeric) {
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/${productId}/`;
        } else {
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/by-slug/${productId}/`;
        }
        
        const response = await fetch(apiUrl, {
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch product details: ${response.status}`);
        }
        
        const data = await response.json();
        setProduct(data);
      } catch (err) {
        console.error('Error fetching product details:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (productId) {
      fetchProduct();
    }
  }, [productId]);

  return { product, loading, error };
}

export function useProductsByBrand(brand, page = 1) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://127.0.0.1:8000/myapp/api/products/?brand=${brand}&page=${page}`, { 
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch products');
        }
        
        const data = await response.json();
        setProducts(data.results || []);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (brand) {
      fetchProducts();
    }
  }, [brand, page]);

  return { products, loading, error };
}


