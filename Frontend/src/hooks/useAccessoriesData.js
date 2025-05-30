import { useState, useEffect } from 'react';

export function useAccessoriesData(page = 1) {
  const [accessories, setAccessories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAccessories = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://127.0.0.1:8000/myapp/api/products/?product_type=accessory&page=${page}`, { 
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch accessories');
        }
        
        const data = await response.json();
        setAccessories(data.results || []);
      } catch (err) {
        console.error('Error fetching accessories:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAccessories();
  }, [page]);

  return { accessories, loading, error };
}

export function useAccessoryDetail(accessoryId) {
  // This reuses the same logic as useProductData but with a different name for clarity
  const [accessory, setAccessory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAccessory = async () => {
      try {
        setLoading(true);
        // Check if accessory is a number (ID) or string (slug)
        const isNumeric = /^\d+$/.test(accessoryId);
        
        let apiUrl;
        if (isNumeric) {
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/${accessoryId}/`;
        } else {
          apiUrl = `http://127.0.0.1:8000/myapp/api/products/by-slug/${accessoryId}/`;
        }
        
        const response = await fetch(apiUrl, {
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch accessory details: ${response.status}`);
        }
        
        const data = await response.json();
        setAccessory(data);
      } catch (err) {
        console.error('Error fetching accessory details:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (accessoryId) {
      fetchAccessory();
    }
  }, [accessoryId]);

  return { accessory, loading, error };
}
