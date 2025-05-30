import React from 'react';

/**
 * Component for selecting product variants (color, storage, quantity)
 * Maintains original CSS classes from the existing implementation
 */
export default function ProductVariantSelector({
  colors = [],
  storageOptions = [],
  selectedColor,
  selectedStorage,
  quantity,
  maxQuantity,
  stockStatus,
  onColorChange,
  onStorageChange,
  onIncrement,
  onDecrement
}) {
  return (
    <div className="SelectionsContainer">
      <div className="ColourAndStorage">
        {colors.length > 0 && (
          <div className="ColourSelection">
            <select value={selectedColor} onChange={onColorChange}>
              {colors.map((color) => (
                <option key={color} value={color}>{color}</option>
              ))}
            </select>
          </div>
        )}
        
        {storageOptions.length > 0 && (
          <div className="StorageSelection">
            <select value={selectedStorage} onChange={onStorageChange}>
              {storageOptions.map((storage) => (
                <option key={storage} value={storage}>{storage}</option>
              ))}
            </select>
          </div>
        )}
        
        <div className="QuantitySelection">
          <button onClick={onDecrement} disabled={quantity <= 1}>-</button>
          <span>{quantity}</span>
          <button onClick={onIncrement} disabled={quantity >= maxQuantity}>+</button>
        </div>
        
        {/* Stock status indicators with original class names */}
        {maxQuantity !== null && (
          <div className={`stock-status ${stockStatus}`}>
            {stockStatus === 'reserved' ? (
              <span>Temporarily Unavailable</span>
            ) : maxQuantity > 5 ? (
              <span>In Stock</span>
            ) : maxQuantity > 0 ? (
              <span>Only {maxQuantity} left in stock</span>
            ) : (
              <span>Out of Stock</span>
            )}
          </div>
        )}
        
        {/* No purchase limit */}
      </div>
    </div>
  );
}
