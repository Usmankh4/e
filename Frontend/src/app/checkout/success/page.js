"use client";
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Footer from "../../../components/footer";
import Header from "../../../components/header";
import '../../globals.css';
import './success.css';

export default function CheckoutSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [orderDetails, setOrderDetails] = useState(null);
  const [purchasedItems, setPurchasedItems] = useState([]);
  const [shippingDetails, setShippingDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [inventoryUpdated, setInventoryUpdated] = useState(false);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        setIsLoading(true);
        
        if (sessionId) {
          // Clear the cart immediately after successful checkout
          localStorage.setItem('cart', JSON.stringify([]));
          
          // Fetch order details from our API
          const sessionResponse = await fetch(`/api/session-details?session_id=${sessionId}`);
          
          if (sessionResponse.ok) {
            const data = await sessionResponse.json();
            
            // Format the order details
            setOrderDetails({
              id: data.id,
              date: new Date().toLocaleDateString(),
              total: data.amount_total,
              paymentMethod: 'Credit Card',
              status: data.payment_status === 'paid' ? 'Confirmed' : data.payment_status,
              customerEmail: data.customer_email
            });
            
            // Format the purchased items
            if (data.items) {
              setPurchasedItems(data.items.map(item => ({
                name: item.name,
                description: item.description,
                image: item.image,
                quantity: item.quantity,
                price: item.amount_total / item.quantity,
                subtotal: item.amount_total
              })));
            }
            
            // Format the shipping details if available
            if (data.shipping) {
              setShippingDetails({
                method: 'Standard Shipping',
                estimatedDelivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
                address: `${data.shipping.address.line1}, ${data.shipping.address.city}, ${data.shipping.address.state} ${data.shipping.address.postal_code}, ${data.shipping.address.country}`,
                name: data.shipping.name
              });
            }
            
            // Backup method: Directly commit the reservation to update inventory
            // This ensures inventory is updated even if the webhook fails
            if (data.payment_status === 'paid' && !inventoryUpdated) {
              try {
                const commitResponse = await fetch('/api/commit-reservation', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({ sessionId }),
                });
                
                if (commitResponse.ok) {
                  console.log('Inventory updated successfully');
                  setInventoryUpdated(true);
                } else {
                  console.error('Failed to update inventory');
                }
              } catch (commitError) {
                console.error('Error updating inventory:', commitError);
              }
            }
          } else {
            // If the API call fails, use the cart data from localStorage as fallback
            const cartItems = localStorage.getItem('cart');
            const parsedItems = cartItems ? JSON.parse(cartItems) : [];
            setPurchasedItems(parsedItems);
            
            // Create a mock order
            setOrderDetails({
              id: sessionId || 'ORD-' + Math.floor(Math.random() * 1000000),
              date: new Date().toLocaleDateString(),
              total: parsedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0),
              paymentMethod: 'Credit Card',
              status: 'Confirmed'
            });
            
            // Create mock shipping details
            setShippingDetails({
              method: 'Standard Shipping',
              estimatedDelivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString(),
              address: '123 Main St, Anytown, USA',
              name: 'Customer'
            });
          }
        }
        
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching order details:', error);
        setIsLoading(false);
      }
    };
    
    fetchOrderDetails();
  }, [sessionId, inventoryUpdated]);

  const handleContinueShopping = () => {
    router.push('/');
  };

  if (isLoading) {
    return (
      <div>
        <Header />
        <div className="pageAfterHeader">
          <div className="LoadingContainer">
            <h2>Loading your order details...</h2>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="pageAfterHeader">
        <div className="SuccessContainer">
          <div className="SuccessHeader">
            <h1>Thank You for Your Order!</h1>
            <p>Your payment was successful and your order has been placed.</p>
          </div>
          
          {orderDetails && (
            <div className="OrderSummary">
              <h2>Order Summary</h2>
              <div className="OrderDetails">
                <div className="OrderInfo">
                  <p><strong>Order ID:</strong> {orderDetails.id}</p>
                  <p><strong>Order Date:</strong> {orderDetails.date}</p>
                  <p><strong>Order Status:</strong> {orderDetails.status}</p>
                  <p><strong>Payment Method:</strong> {orderDetails.paymentMethod}</p>
                  {orderDetails.customerEmail && (
                    <p><strong>Customer Email:</strong> {orderDetails.customerEmail}</p>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {purchasedItems.length > 0 && (
            <div className="PurchasedItems">
              <h2>Purchased Items</h2>
              <div className="ItemsList">
                {purchasedItems.map((item, index) => (
                  <div key={index} className="PurchasedItem">
                    <div className="ItemImage">
                      {item.image && <img src={item.image} alt={item.name} width={80} height={80} />}
                    </div>
                    <div className="ItemDetails">
                      <h3>{item.name}</h3>
                      {item.color && <p><strong>Color:</strong> {item.color}</p>}
                      {item.storage && <p><strong>Storage:</strong> {item.storage}</p>}
                      <p><strong>Quantity:</strong> {item.quantity}</p>
                      <p><strong>Price:</strong> ${(item.price).toFixed(2)}</p>
                      <p><strong>Subtotal:</strong> ${(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="OrderTotal">
                <h3>Total: ${orderDetails?.total.toFixed(2)}</h3>
              </div>
            </div>
          )}
          
          {shippingDetails && (
            <div className="ShippingDetails">
              <h2>Shipping Information</h2>
              <p><strong>Recipient:</strong> {shippingDetails.name}</p>
              <p><strong>Shipping Method:</strong> {shippingDetails.method}</p>
              <p><strong>Estimated Delivery:</strong> {shippingDetails.estimatedDelivery}</p>
              <p><strong>Shipping Address:</strong> {shippingDetails.address}</p>
            </div>
          )}
          
          <div className="ReceiptActions">
            <button onClick={handleContinueShopping} className="ContinueShoppingButton">
              Continue Shopping
            </button>
            <button onClick={() => window.print()} className="PrintReceiptButton">
              Print Receipt
            </button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
