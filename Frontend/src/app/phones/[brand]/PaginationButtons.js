"use client";
import { useRouter } from 'next/navigation';

export default function PaginationButtons({ brand, currentPage }) {
  const router = useRouter();

  const handlePrevious = () => {
    router.push(`/phones/${brand}?page=${currentPage - 1}`);
  };

  const handleNext = () => {
    router.push(`/phones/${brand}?page=${currentPage + 1}`);
  };

  return (
    <div className="pageButton">
      {currentPage > 1 && (
        <button onClick={handlePrevious}>Previous</button>
      )}
      <button onClick={handleNext}>Next</button>
    </div>
  );
}
