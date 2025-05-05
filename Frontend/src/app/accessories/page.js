"use client";
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/header';
import Footer from '@/components/footer';
import '../../app/globals.css';

function AccessoriesPage() {
  const { brand } = useParams();
  const [accessories, setAccessories] = useState([]);


  useEffect(() => {
    const fetchAccessories = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/myapp/api/accessories/`);
        setAccessories(response.data.results);
        console.log(response.data.results);
      } catch (error) {
        console.error('Error fetching accessories:', error);
      }
    };
    fetchAccessories();
  }, [brand]);

  return (
    <div>
      <Header />
      <div className="pageAfterHeader">
        <h2>ACCESSORIES</h2>
        <div className="PhoneWrapper">
          {accessories.map((accessory) => (
            <div className="PhoneCard" key={accessory.id}>
              <Link href={`/Accessories/${brand}/${accessory.id}`}>
                
                  <h4>{accessory.name}</h4>
                  <img src={accessory.image} alt={accessory.name} style={{ width: 150, height: 200 }} />
                  <h4>On sale for ${accessory.price}</h4>
                
              </Link>
            </div>
          ))}
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default AccessoriesPage;
