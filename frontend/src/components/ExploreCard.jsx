import React from 'react';

const ExploreCard = ({ city, dateRange, imageUrl }) => {
  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden group cursor-pointer transform hover:-translate-y-1 transition-transform duration-300">
      <img
        src={imageUrl}
        alt={`A scenic view of ${city}`}
        className="w-full h-48 object-cover group-hover:opacity-90 transition-opacity"
        loading="lazy"
      />
      <div className="p-4">
        <h3 className="font-bold text-gray-700">{city}</h3>
        <p className="text-sm text-subtext-gray">{dateRange}</p>
      </div>
    </div>
  );
};

export default ExploreCard;