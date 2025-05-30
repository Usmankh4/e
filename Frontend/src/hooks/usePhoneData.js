import { useProductData, useProductsByBrand } from './useProductData';

// These hooks are just wrappers around the product hooks for semantic clarity
// They help separate the concept of "phones" from generic "products"

export function usePhoneData(phoneId) {
  // Reuse the existing product data hook but with phone-specific naming
  return useProductData(phoneId);
}

export function usePhonesByBrand(brand, page = 1) {
  // Reuse the existing products-by-brand hook but with phone-specific naming
  return useProductsByBrand(brand, page);
}
