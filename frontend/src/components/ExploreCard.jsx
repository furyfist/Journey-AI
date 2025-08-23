import React, { useState } from 'react';

const ExploreCard = ({ city, dateRange, imageUrl }) => {
  const [imageError, setImageError] = useState(false);

  // Updated fallback image with a real photography
  const fallbackImageUrl = "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&auto=format&fit=crop";

  return (
    <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-xl transition-shadow duration-300">
      <img
        src={imageError ? fallbackImageUrl : imageUrl}
        alt={`${city} destination`}
        onError={() => setImageError(true)}
        className="w-full h-64 object-cover transform group-hover:scale-110 transition-transform duration-300"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
        <div className="absolute bottom-4 left-4">
          <h3 className="text-2xl font-bold text-white tracking-wide">{city}</h3>
          <p className="text-sm text-white/90 mt-1">{dateRange}</p>
        </div>
      </div>
    </div>
  );
};

export default ExploreCard;