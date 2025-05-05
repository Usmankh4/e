"use client";
import { useState } from 'react';

export default function ProductQuantity() {
  const [quantity, setQuantity] = useState(1);

  const incrementQuantity = () => {
    setQuantity(prevQuantity => prevQuantity + 1);
  };

  const decrementQuantity = () => {
    setQuantity(prevQuantity => prevQuantity > 1 ? prevQuantity - 1 : 1);
  };

  return (
    <>
      <button onClick={decrementQuantity}>-</button>
      <span>{quantity}</span>
      <button onClick={incrementQuantity}>+</button>
    </>
  );
}
