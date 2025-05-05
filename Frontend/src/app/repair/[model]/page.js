"use client";
import Image from "next/image";
import Link from "next/link";
import Footer from "../../../components/footer";
import Header from "../../../components/header";
import { useParams } from 'next/navigation';
  import axios from 'axios';
  import { useEffect, useState } from 'react';
  
  export default function ModelProducts() {

    const { model } = useParams();  
    const [products, setProducts] = useState([]);
    
  
    useEffect(() => {
      if (model) {
        const fetchProducts = async () => {
          const res = await axios.get(`http://localhost:8000/myapp/api/phone-models/?brandName=${model}`);  
          setProducts(res.data.results);
        };
        fetchProducts();
        
      }
    }, [model]);
  
    if (!products) return <div>Loading...</div>;

  return (
    <div>
    <Header></Header>
    <div className="pageAfterHeader">
      <div className="RepairHeader">
      <div className="RepairWrapper">
        <div className="phones-grid">
          {products.map((phone) => (
            
            <div className="phone-card" key={phone.name}>
              {console.log(phone.name)}
              <div className="phonecardPicture">
                <div className="phonePicturewrapper">
              <img src={phone.image} alt={phone.name} width={150} height={204} />
              </div>
              </div>
              <h4>{phone.name}</h4>
              <p>Get your phone fixed today. Check out our price list now!</p>
              <Link href={`/repair/${model}/${phone.name}`}>
                <button>LEARN MORE</button> 
              </Link> 
            </div>
          ))}
        </div>
      </div>
      </div>
    </div>
    <Footer></Footer>
  </div>



    
  );
          }
        