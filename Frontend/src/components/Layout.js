import React from 'react';
import Header from './header';
import Footer from './footer';

/**
 * Reusable layout component that wraps content with header and footer
 */
export default function Layout({ children, className = "pageAfterHeader" }) {
  return (
    <div className="PhoneBackground">
      <Header />
      <div className={className}>
        {children}
      </div>
      <Footer />
    </div>
  );
}
