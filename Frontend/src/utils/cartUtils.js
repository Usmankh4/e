/**
 * Utility functions for cart operations
 */

/**
 * Add an item to the cart
 * @param {Object} productDetails - Product details to add to cart
 * @returns {Array} - Updated cart items
 */
export function addToCart(productDetails) {
  let cart = getCart();
  
  const existingIndex = cart.findIndex(item => 
    item.productId === productDetails.productId && 
    item.color === productDetails.color && 
    item.storage === productDetails.storage
  );
  
  if (existingIndex !== -1) {
    cart[existingIndex].quantity += productDetails.quantity;
  } else {
    cart.push(productDetails);
  }
  
  saveCart(cart);
  return cart;
}

/**
 * Get the current cart from localStorage
 * @returns {Array} - Cart items
 */
export function getCart() {
  if (typeof window === 'undefined') return [];
  
  const cartJson = localStorage.getItem('cart');
  return cartJson ? JSON.parse(cartJson) : [];
}

/**
 * Save cart to localStorage
 * @param {Array} cart - Cart items to save
 */
export function saveCart(cart) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('cart', JSON.stringify(cart));
}

/**
 * Remove an item from the cart
 * @param {string} itemId - ID of the item to remove
 * @returns {Array} - Updated cart items
 */
export function removeFromCart(itemId) {
  let cart = getCart();
  cart = cart.filter(item => item.id !== itemId);
  saveCart(cart);
  return cart;
}

/**
 * Update the quantity of an item in the cart
 * @param {string} itemId - ID of the item to update
 * @param {number} quantity - New quantity
 * @returns {Array} - Updated cart items
 */
export function updateCartItemQuantity(itemId, quantity) {
  let cart = getCart();
  const itemIndex = cart.findIndex(item => item.id === itemId);
  
  if (itemIndex !== -1) {
    cart[itemIndex].quantity = quantity;
    saveCart(cart);
  }
  
  return cart;
}

/**
 * Clear the cart
 * @returns {Array} - Empty cart
 */
export function clearCart() {
  saveCart([]);
  return [];
}
