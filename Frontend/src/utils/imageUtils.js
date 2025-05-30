/**
 * Utility functions for handling image URLs in the application
 */

/**
 * Processes an image URL to ensure it has the correct format
 * @param {string} rawImageUrl - The raw image URL from the API
 * @param {string} fallbackImage - Optional fallback image if URL is invalid
 * @returns {string} - Properly formatted image URL
 */
export function processImageUrl(rawImageUrl, fallbackImage = '/placeholder-phone.jpg') {
  if (!rawImageUrl) return fallbackImage;
  
  if (rawImageUrl.startsWith('http')) {
    return rawImageUrl;
  }
  
  if (rawImageUrl.startsWith('/media')) {
    return `http://localhost:8000${rawImageUrl}`;
  }
  
  return `http://localhost:8000/media/${rawImageUrl}`;
}
