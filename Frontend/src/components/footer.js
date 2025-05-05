import React from "react";

import "../app/globals.css"



import Link from "next/link";

function Footer() {
  return (
         

    <div>
      <div className="header">
        <div className="headerTop">
          <div className="footerTopLeft">
           <h4>Main Menu</h4>

          <ul>
            <li className="link">
              <a href="/">Home</a>
            </li>
            <li className="link">
              <Link href="/products/Apple">Apple</Link>
            </li>
            <li className="link">
              <Link href="/products/Samsung">Samsung</Link>
            </li>
            <li className="link">
              <Link href="/products/Android">Android</Link>
            </li>
            <li className="link">
              <Link href="/products/Tablet">Tablet</Link>
            </li>
            <li className="link">
              <Link href="/products/Accessories">Accessories</Link>
            </li>
            <li className="link">
              <Link href="/repair">Repair</Link>
            </li>
            <li className="link">
              <Link href="/contactus">Contact Us</Link>
            </li>
            
          </ul>
          </div>

          <div className="footerTopLeft">
          <h4>Contact Us</h4>
           
           <ul>
             
             <li className="link">
               <Link href="/contactus">   Mississauga: 905 232 7771</Link>
             </li>
             <li className="link">
               <Link href="/contactus">zainwireless@gmail.com</Link>
             </li>
             <li className="link">
               <Link href="/contactus">3415 Dixie Rd, Mississauga, ON</Link>
             </li>
             <li className="link">
               <Link href="/contactus">L4Y 2B1</Link>
             </li>

           </ul>
          </div>

          <div className="footerTopRight">
          <h4>Policy</h4>
           
           <ul>
             <li className="link">
               <a href="/private">Private Policy</a>
             </li>
             <li className="link">
               <Link href="/terms">Terms Of Service</Link>
             </li>
             <li className="link">
               <Link href="/refundpolicy">Refund Policy</Link>
             </li>
             <li className="link">
               <Link href="/shippingpolicy">Shipping Policy</Link>
             </li>
             <li className="link">
               <Link href="/warranty">Warranty</Link>
             </li>
             <li className="link">
               <Link href="/covid19warranty">Covid-19 Warranty</Link>
             </li>
           </ul>
          </div>
        </div>

        <hr color="#2f2f2f" />

        <div className="footerBottom">
          {/* <ul>
  <li className="activeLink"><a href="/">Home</a></li>
  <li className='link'><Link href="/phones/iphone">Apple</Link></li>
  <li className="link"><Link href="/samsung">Samsung</Link></li>
  <li className="link"><Link href="/contactus">Contact Us</Link></li>
</ul> */}

          <p>Copyright @Zainwireless</p>
        </div>
      </div>
    </div>
  );
}

export default Footer;