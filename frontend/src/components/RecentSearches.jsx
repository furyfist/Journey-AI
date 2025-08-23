import React from 'react';

const RecentSearches = () => {
  return (
    <section className="container mx-auto px-6 py-8">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-teal-heading">Recent Searches</h2>
        <a href="#" className="text-subtext-gray hover:text-teal-heading transition-colors">
          View all →
        </a>
      </div>
      {/* Dynamic list or carousel will go here */}
      <div className="mt-4 text-center text-subtext-gray py-10 border-2 border-dashed border-gray-300 rounded-lg">
        Your recent searches will appear here.
      </div>
    </section>
  );
};

export default RecentSearches;