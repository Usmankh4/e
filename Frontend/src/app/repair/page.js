"use client";
import { useEffect, useState } from 'react';
import Footer from '../../components/footer';
import '../globals.css';
import Header from '../../components/header';
import Link from 'next/link';
import axios from 'axios';

export default function Repair() {
  const [phoneBrands, setPhoneBrands] = useState([]);

  useEffect(() => {
   const fetchphoneBrand = async () => {
    try {
      const response = await axios.get('http://localhost:8000/myapp/api/phone-brands/');
      setPhoneBrands(response.data.results);

    } catch(error){
      console.error('Error fetching phone brands', error);

    }
    }
    fetchphoneBrand();
   },[]);
    
      

  return (
    <div>
      <Header />
      <div className="pageAfterHeader">
        <div className="RepairHeader">
          <div className="RepairHeaderText">
            <h3>Please select your phone brand that needs repairing from the list below!</h3>
            <div className="RepairWrapper">
              <div className="phones-grid">
                {phoneBrands.map((brand) => (
                  <Link key={brand.id} href={`/repair/${brand.name}`}>
                    <div className="phonePicture">
                      <img src={brand.logo} alt={brand.name} width={150} height={104} />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}