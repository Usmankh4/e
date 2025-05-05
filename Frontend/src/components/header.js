"use client";
import "../app/globals.css";
import Link from 'next/link';
import { useCart } from "../app/cart/CartContext";
export default function Header() {
  const { cartItems } = useCart();
  const totalItemsInCart = cartItems.reduce((total, item) => total + item.quantity, 0);


  return (
    <div className="header">
      <div className="headerTop">
        <div className="headerTopLeft">
          <h2>Zain Wireless</h2>
        </div>
        
        <div className="headerTopRight">
        <Link href="/checkout">
          <svg className="svgIcon" width="20" height="20">
            <path d="M18.125,15.804l-4.038-4.037c0.675-1.079,1.012-2.308,1.01-3.534C15.089,4.62,12.199,1.75,8.584,1.75C4.815,1.75,1.982,4.726,2,8.286c0.021,3.577,2.908,6.549,6.578,6.549c1.241,0,2.417-0.347,3.44-0.985l4.032,4.026c0.167,0.166,0.43,0.166,0.596,0l1.479-1.478C18.292,16.234,18.292,15.968,18.125,15.804 M8.578,13.99c-3.198,0-5.716-2.593-5.733-5.71c-0.017-3.084,2.438-5.686,5.74-5.686c3.197,0,5.625,2.493,5.64,5.624C14.242,11.548,11.621,13.99,8.578,13.99 M16.349,16.981l-3.637-3.635c0.131-0.11,0.721-0.695,0.876-0.884l3.642,3.639L16.349,16.981z"></path>
          </svg> 
          <svg className="svgIconShop" width="20" height="20">
            <path d="M17.638,6.181h-3.844C13.581,4.273,11.963,2.786,10,2.786c-1.962,0-3.581,1.487-3.793,3.395H2.362c-0.233,0-0.424,0.191-0.424,0.424v10.184c0,0.232,0.191,0.424,0.424,0.424h15.276c0.234,0,0.425-0.191,0.425-0.424V6.605C18.062,6.372,17.872,6.181,17.638,6.181 M13.395,9.151c0.234,0,0.425,0.191,0.425,0.424S13.629,10,13.395,10c-0.232,0-0.424-0.191-0.424-0.424S13.162,9.151,13.395,9.151 M10,3.635c1.493,0,2.729,1.109,2.936,2.546H7.064C7.271,4.744,8.506,3.635,10,3.635 M6.605,9.151c0.233,0,0.424,0.191,0.424,0.424S6.838,10,6.605,10c-0.233,0-0.424-0.191-0.424-0.424S6.372,9.151,6.605,9.151 M17.214,16.365H2.786V7.029h3.395v1.347C5.687,8.552,5.332,9.021,5.332,9.575c0,0.703,0.571,1.273,1.273,1.273c0.702,0,1.273-0.57,1.273-1.273c0-0.554-0.354-1.023-0.849-1.199V7.029h5.941v1.347c-0.495,0.176-0.849,0.645-0.849,1.199c0,0.703,0.57,1.273,1.272,1.273s1.273-0.57,1.273-1.273c0-0.554-0.354-1.023-0.849-1.199V7.029h3.395V16.365z"></path>
          </svg>
          {totalItemsInCart > 0 && (
            <span className="totalItemsInCart">{totalItemsInCart}</span>
          )}
          </Link>
        </div>
      </div>

      <hr color="#2f2f2f"/>

      <div className="headerBottom">
        <ul>
          <li className="link"><a href="/">Home</a></li>
          <li className="link"><Link href="/products/Apple">Apple</Link></li>
          <li className="link"><Link href="/products/Samsung">Samsung</Link></li>
          <li className="link"><Link href="/products/Android">Android</Link></li>
          <li className="link"><Link href="/products/Tablet">Tablet</Link></li>
          <li className="link"><Link href="/products/Accessories">Accessories</Link></li>
          <li className="link"><Link href="/repair">Repair</Link></li>
          <li className="link"><Link href="/contactus">Contact Us</Link></li>
        </ul>
      </div>
    </div>
  );
}
