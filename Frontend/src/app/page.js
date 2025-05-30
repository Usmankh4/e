import iphone from "../image/15promax.jpg";
import Header from "../components/header";
import BannerImage from "../images/phone.png"
import Image from "next/image";
import samsung from "../image/samsungultra.jpg";
import google from "../image/Pixel8.png";

import Footer from "../components/footer";
import Link from "next/link";

export default function Home() {
  
  return (
    
    <div>
      
      <Header />
      <div>
      <div className="pageAfterHeader">
        <div className="heroBanner">
          <div className="box">
            <div className="frame-wrapper">
            <div className='div'>
                <h1 className='text-wrapper'>REPAIR IS OUR SPECIALTY</h1>
                <div className='frame-2'>
                  <div className='div-wrapper'>
                    <Link href= "/products/Accessories">
                    <button className='button-wrapper-2'>Shop</button>
                    </Link>
                  </div>
                  <div className='frame-3'>
                    <Link href="/repair">
                    <button className='button-wrapper-3'>Repair</button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="heroImage">
            <Image src={BannerImage}></Image>
          </div>
        </div>

        <div className="cardWrapper">
          <div className="cardLayout">
            
            <div className="iPhoneCard">
              <Link href="/phones/Apple">
              <h2>Apple</h2>
              <button>View All</button>
              <div className="iPhoneImage">
                <Image src={iphone}></Image>
              </div>
              </Link>
            </div>

            <div className="iPhoneCard">
              <Link href="/phones/Samsung">
              <h2>Samsung</h2>
              <button>View All</button>
              <div className="iPhoneImage">
                <Image height={243} src={samsung}></Image>
                
              </div>
              </Link>
            </div>

            <div className="iPhoneCard">
            <Link href="/phones/Android">
              <h2>Android</h2>
              <button>View All</button>
              <div className="iPhoneImage">
                <Image zoom height={243} src={google}></Image>
              </div>
              </Link>
            </div>
          </div>
        </div>

        <div className="cardsBelowContainer" >
          <div className="CardsBelow">
          
            <div className="bigcard">
            <Link href="/products/Accessories">

              <h2>Accessories</h2>
              <button>View All</button>
              <div className="iPhoneImage">
                <Image zoom height={243} src={google}></Image>
              </div>
              </Link>
            </div>
            <div className="bigcard">
            <Link href="/phones/Tablet">

              <h2>Tablets</h2>
              <button>View All</button>
              <div className="iPhoneImage">
                <Image zoom height={243} src={google}></Image>
              </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
    </div>
  );
}