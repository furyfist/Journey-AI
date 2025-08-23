import React from 'react';
import ExploreCard from './ExploreCard';

// Sample data
const destinations = [
  { city: 'Denver', dateRange: 'Sep 2-12', imageUrl: 'https://images.unsplash.com/photo-1620227989934-21f4ae4f0148?q=80&w=800' },
  { city: 'Tokyo', dateRange: 'Oct 15-25', imageUrl: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=800' },
  { city: 'Melbourne', dateRange: 'Nov 5-15', imageUrl: 'https://images.unsplash.com/photo-1544439322-4d5164a2ed54?q=80&w=800' },
  { city: 'Austin', dateRange: 'Sep 20-30', imageUrl: 'https://images.unsplash.com/photo-1531218150217-54595bc2b934?q=80&w=800' },
  { city: 'New York', dateRange: 'Dec 1-10', imageUrl: 'https://images.unsplash.com/photo-1534430480872-3498386e7856?q=80&w=800' },
  { city: 'Istanbul', dateRange: 'Oct 10-20', imageUrl: 'https://images.unsplash.com/photo-1562369324-4d87752e5842?q=80&w=800' },
  { city: 'Cairo', dateRange: 'Nov 22-Dec 2', imageUrl: 'https://images.unsplash.com/photo-1572079863414-2a623701a2f1?q=80&w=800' },
  { city: 'Marrakech', dateRange: 'Sep 18-28', imageUrl: 'https://images.unsplash.com/photo-1579733479412-f3a3644f1334?q=80&w=800' },
];


const Explore = () => {
  return (
    <section className="container mx-auto px-6 py-12">
      <h2 className="text-3xl font-bold text-teal-heading">Explore</h2>
      <p className="mt-2 text-subtext-gray">Not sure where to go? Try out some suggestions!</p>

      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {destinations.map((dest) => (
          <ExploreCard
            key={dest.city}
            city={dest.city}
            dateRange={dest.dateRange}
            imageUrl={`${dest.imageUrl}&auto=format&fit=crop`}
          />
        ))}
      </div>
    </section>
  );
};

export default Explore;