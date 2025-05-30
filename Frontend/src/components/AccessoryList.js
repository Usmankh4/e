import { Suspense } from 'react';
import AccessoryCard from './AccessoryCard';
import Pagination from './Pagination';
import { processImageUrl } from '../utils/imageUtils';

async function getAccessories() {
  try {
    const res = await fetch('http://127.0.0.1:8000/myapp/api/accessories/', {
      cache: 'no-store'
    });
    
    if (!res.ok) {
      throw new Error('Failed to fetch accessories');
    }
    
    return res.json();
  } catch (error) {
    console.error('Error loading accessories:', error);
    return [];
  }
}

export default async function AccessoryList() {
  const accessories = await getAccessories();
  
  if (!accessories || accessories.length === 0) {
    return (
      <div className="AccessoriesEmpty">
        <p>No accessories found. Check back soon!</p>
      </div>
    );
  }
  
  return (
    <Suspense fallback={<div className="loading">Loading accessories...</div>}>
      <div className="AccessoriesWrapper">
        <div className="AccessoriesLayout">
          {accessories.map((accessory) => (
            <AccessoryCard 
              key={accessory.id} 
              accessory={accessory}
            />
          ))}
        </div>
      </div>
    </Suspense>
  );
}
